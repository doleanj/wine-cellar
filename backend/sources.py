"""Registry of supported "fill from link" sites: one parser module per site."""
import generic
import lcdbb
import leclerc

# leclerc exposes the same constants as lcdbb (added below to keep that module's API small)
leclerc.KEY = "leclerc"
leclerc.NAME = "E.Leclerc"
leclerc.HOSTS = leclerc.ALLOWED_HOSTS
leclerc.PATH_PREFIX = "/fp/"
leclerc.EXAMPLE = "https://www.e.leclerc/fp/…"
leclerc.FIELDS = ["name", "grape", "vintage", "type", "region", "country", "alcohol", "volume_ml", "sulphites",
                  "pairings", "profile_fruit", "profile_personality", "keep_until_years", "serving_temp",
                  "tasting", "price", "barcode", "image_url", "url"]

SOURCES = [leclerc, lcdbb, generic]  # generic last: it accepts any https page


def match(url: str):
    """(module, canonical url) of the first parser that accepts the link, else (None, '')."""
    for mod in SOURCES:
        canon = mod.canonical_url(url)
        if canon:
            return mod, canon
    return None, ""


def describe() -> list:
    return [{"key": m.KEY, "name": m.NAME, "hosts": list(m.HOSTS), "path_prefix": m.PATH_PREFIX,
             "example": m.EXAMPLE, "fields": m.FIELDS} for m in SOURCES]
