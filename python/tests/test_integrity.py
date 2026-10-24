from copy import deepcopy
import pytest
from colombia_dev.integrity import build_log, canonical, checkpoint, verify


def sample():
    return build_log([
        {"contract": "synthetic-001", "action": "registered"},
        {"contract": "synthetic-001", "action": "verified"},
        {"contract": "synthetic-001", "action": "authorized"},
    ])


def test_clean_and_empty():
    for log in [[], sample()]:
        assert verify(log, checkpoint(log))


@pytest.mark.parametrize("attack", ["edit", "reorder", "delete", "truncate", "duplicate"])
def test_detect_mutations(attack):
    original = sample()
    log = deepcopy(original)
    if attack == "edit":
        log[0]["payload"]["action"] = "paid"
    elif attack == "reorder":
        log.reverse()
    elif attack == "delete":
        del log[1]
    elif attack == "truncate":
        log.pop()
    else:
        log.append(deepcopy(log[-1]))
    assert not verify(log, checkpoint(original))


def test_rewrite_requires_external_checkpoint():
    original = sample()
    payloads = [dict(e["payload"]) for e in original]
    payloads[0]["action"] = "paid"
    forged = build_log(payloads)
    assert verify(forged, checkpoint(forged))  # Internal consistency is insufficient.
    assert not verify(forged, checkpoint(original))


def test_no_checkpoint_or_malformed_event_fails():
    assert not verify(sample(), None)
    assert not verify([{}], checkpoint(sample()))


def test_canonical_and_input_isolation():
    assert canonical({"b": "2", "a": "1"}) == canonical({"a": "1", "b": "2"})
    source = {"action": "registered"}
    log = build_log([source])
    source["action"] = "paid"
    assert log[0]["payload"]["action"] == "registered"
    with pytest.raises(ValueError):
        canonical({"amount": 1.0})


def test_checkpoint_count_and_root_are_checked():
    log = sample()
    for key, bad in [("count", 4), ("root", "0" * 64), ("version", "unknown")]:
        trusted = checkpoint(log)
        trusted[key] = bad
        assert not verify(log, trusted)
