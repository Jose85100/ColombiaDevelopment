from colombia_dev.territorial import Territory, score

def test_territorial_bounds():
    r = score(Territory(.8, .6, .2, .8, .9, .7))
    assert all(0 <= r[k] <= 1 for k in ("vulnerability", "opportunity", "priority"))
