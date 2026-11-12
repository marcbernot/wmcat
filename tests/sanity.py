"""Quick sanity checks on the sample catalog (run: pixi run sanity)."""

from wmcat import open_catalog

cat = open_catalog()
assert len(cat) == 10, len(cat)
assert len(cat.search(holding_institution="SBB")) == 2
assert len(cat.search(motif="lily")) == 2
assert len(cat.search(wm_type="01")) == 7  # substring: 01 and 01f
assert len(cat.search(wm_type="01", exact=True)) == 3
assert len(cat.search(wm_type="01f", exact=True)) == 4
assert len(cat.search(holding_institution="SLUB", wm_type="02f", exact=True)) == 3
assert cat[0]["doi"].startswith("10.5281/zenodo.")
print("sanity OK")
print(cat.search(wm_type="01f", exact=True))
