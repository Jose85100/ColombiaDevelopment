"""Run from repo root: PYTHONPATH=python python python/examples/integrity_demo.py"""
from colombia_dev.integrity import build_log, checkpoint, verify

payloads = [
    {"contract": "SYNTHETIC-RAIL-001", "milestone": "M1", "action": "registered"},
    {"contract": "SYNTHETIC-RAIL-001", "milestone": "M1", "action": "verified"},
]
original = build_log(payloads)
trusted = checkpoint(original)  # In practice authenticate via an external witness.
forged = build_log([dict(payloads[0], action="paid"), payloads[1]])
print("Synthetic example; no real contract or payment")
print("Original matches external checkpoint:", verify(original, trusted))
print("Rewritten history is internally consistent:", verify(forged, checkpoint(forged)))
print("Rewritten history matches external checkpoint:", verify(forged, trusted))
print("Truncated history matches external checkpoint:", verify(original[:-1], trusted))
