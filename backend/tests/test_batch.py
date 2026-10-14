def test_batch_update_reaches_its_route(client, admin_headers):
    # PUT /wines/batch used to be shadowed by PUT /wines/{wine_id} ("batch" -> 422).
    ids = [client.post("/wines", json={"name": f"Batch {n}", "quantity": 1}, headers=admin_headers).json()["id"]
           for n in (1, 2)]
    r = client.put("/wines/batch", json={"ids": ids, "updates": {"location": "Rack C", "rating": 4}},
                   headers=admin_headers)
    assert r.status_code == 200 and r.json() == {"updated": 2}
    by_id = {w["id"]: w for w in client.get("/wines").json()}
    assert all(by_id[i]["location"] == "Rack C" and by_id[i]["rating"] == 4 for i in ids)


def test_batch_update_requires_admin(client, admin_headers):
    wid = client.post("/wines", json={"name": "Batch Locked", "quantity": 1}, headers=admin_headers).json()["id"]
    assert client.put("/wines/batch", json={"ids": [wid], "updates": {"location": "X"}}).status_code == 401
