def test_regions_seeded_and_ordered(client, admin_headers):
    r = client.get("/regions", headers=admin_headers)
    assert r.status_code == 200
    keys = [x["key"] for x in r.json()]
    assert keys[:3] == ["bordelais", "sud-ouest", "languedoc-roussillon"]
    assert len(keys) == 10 and "champagne" in keys
    bordeaux = r.json()[0]
    assert "Pauillac" in bordeaux["appellations"]
    assert bordeaux["intro"] == "" and bordeaux["image_url"] == ""


def test_update_region_requires_admin(client):
    assert client.put("/regions/alsace", json={"intro": "x"}).status_code == 401


def test_update_region(client, admin_headers):
    r = client.put("/regions/alsace", headers=admin_headers, json={
        "intro": "Bande étroite entre Vosges et Rhin.",
        "appellations": ["Alsace Grand Cru", " Riesling ", ""],
        "image_url": "/api/images/abc.png",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["intro"].startswith("Bande")
    assert d["appellations"] == ["Alsace Grand Cru", "Riesling"]
    assert d["image_url"] == "/api/images/abc.png"
    again = [x for x in client.get("/regions", headers=admin_headers).json() if x["key"] == "alsace"][0]
    assert again["image_url"] == "/api/images/abc.png"


def test_update_region_rejects_foreign_image_url(client, admin_headers):
    r = client.put("/regions/alsace", headers=admin_headers, json={"image_url": "https://evil.example/x.png"})
    assert r.status_code == 422


def test_update_unknown_region(client, admin_headers):
    assert client.put("/regions/atlantis", headers=admin_headers, json={"intro": "x"}).status_code == 404


def test_region_extra_text_roundtrip(client, admin_headers):
    r = client.put("/regions/alsace", headers=admin_headers, json={"extra": "Longer text.", "extra_source": "https://example.test/x"})
    assert r.status_code == 200 and r.json()["extra"] == "Longer text." and r.json()["extra_source"] == "https://example.test/x"
    got = [x for x in client.get("/regions", headers=admin_headers).json() if x["key"] == "alsace"][0]
    assert got["extra"] == "Longer text."
    # other fields untouched by a partial update
    assert got["intro"] == client.put("/regions/alsace", headers=admin_headers, json={"extra": ""}).json()["intro"]


def test_startup_migrates_an_old_regions_table_before_seeding(tmp_path, monkeypatch):
    """Existing installs have a regions table without extra/extra_source: starting the app must not fail."""
    import main
    from sqlalchemy import create_engine, text

    eng = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with eng.begin() as c:
        c.execute(text("CREATE TABLE regions (id INTEGER PRIMARY KEY AUTOINCREMENT, key VARCHAR NOT NULL UNIQUE, "
                       "name VARCHAR NOT NULL, intro VARCHAR, appellations VARCHAR, image_url VARCHAR, sort_order INTEGER)"))
        c.execute(text("INSERT INTO regions (key, name, intro, appellations, image_url, sort_order) "
                       "VALUES ('alsace', 'Alsace', 'old intro', '[]', '', 0)"))
    monkeypatch.setattr(main, "engine", eng)
    main._migrate_regions()
    main._seed_regions()   # used to raise "no such column: regions.extra"
    with eng.connect() as c:
        cols = {r[1] for r in c.execute(text("PRAGMA table_info(regions)"))}
        intro = c.execute(text("SELECT intro FROM regions WHERE key = 'alsace'")).scalar()
        count = c.execute(text("SELECT COUNT(*) FROM regions")).scalar()
    assert {"extra", "extra_source"} <= cols and intro == "old intro" and count == len(main.REGIONS_SEED)


def test_regions_migration_runs_before_seeding_at_import():
    import inspect
    import main
    src = inspect.getsource(main)
    assert src.index("\n_migrate_regions()\n") < src.index("\n_seed_regions()\n")
