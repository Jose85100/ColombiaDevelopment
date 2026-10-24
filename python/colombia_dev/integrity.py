"""Synthetic integrity lab. No signatures, persistence, identity or blockchain.

A checkpoint is trusted only if obtained/authenticated outside the log operator.
Canonical encoding below is intentionally limited to JSON string maps.
"""
from hashlib import sha256
import json

GENESIS = "0" * 64


def canonical(payload):
    """Local deterministic encoding, not a cross-language canonical JSON standard."""
    if (not isinstance(payload, dict) or
            not all(isinstance(k, str) and isinstance(v, str)
                    for k, v in payload.items())):
        raise ValueError("payload must be a map of strings to strings")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def event_digest(index, previous, payload):
    body = str(index).encode("ascii") + b"\x00" + previous.encode("ascii")
    return sha256(b"IPV-event-v1\x00" + body + b"\x00" + canonical(payload)).hexdigest()


def build_log(payloads):
    """Create a new list without retaining mutable references to input maps."""
    events, previous = [], GENESIS
    for index, payload in enumerate(payloads):
        digest = event_digest(index, previous, payload)
        events.append(dict(index=index, previous=previous,
                           payload=dict(payload), digest=digest))
        previous = digest
    return events


def merkle_root(digests):
    """Domain-separated tree; odd last nodes duplicate. Not RFC 9162 encoding."""
    nodes = [sha256(b"\x00" + bytes.fromhex(d)).digest() for d in digests]
    if not nodes:
        return sha256(b"").hexdigest()
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [sha256(b"\x01" + nodes[i] + nodes[i + 1]).digest()
                 for i in range(0, len(nodes), 2)]
    return nodes[0].hex()


def checkpoint(events):
    """Snapshot only; does not sign or authenticate the returned checkpoint."""
    return dict(version="ipv-lab-v1", count=len(events),
                tip=events[-1]["digest"] if events else GENESIS,
                root=merkle_root([e["digest"] for e in events]))


def verify(events, trusted_checkpoint):
    """Verify exact covered history against an independently trusted snapshot.

    Missing checkpoint fails closed. This does not establish identity, truth,
    timestamps or completeness beyond the externally committed event count.
    """
    if not isinstance(trusted_checkpoint, dict):
        return False
    previous = GENESIS
    try:
        for index, event in enumerate(events):
            if set(event) != {"index", "previous", "payload", "digest"}:
                return False
            if type(event["index"]) is not int or event["index"] != index:
                return False
            if event["previous"] != previous:
                return False
            digest = event_digest(index, previous, event["payload"])
            if event["digest"] != digest:
                return False
            previous = digest
        return checkpoint(events) == trusted_checkpoint
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError):
        return False
