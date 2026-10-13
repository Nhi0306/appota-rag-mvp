from __future__ import annotations


def load_units(raw_units: dict) -> dict:
    units = {}
    for key, info in raw_units.items():
        units[key] = {
            "name": info["name"],
            "parent": info.get("parent"),
        }
    return units


def ancestors(unit: str, units: dict) -> list:
    path = []
    cur = unit
    seen = set()
    while cur and cur not in seen:
        path.append(cur)
        seen.add(cur)
        info = units.get(cur)
        cur = info["parent"] if info else None
    return path


def unit_depth(unit: str) -> int:
    return len([p for p in unit.split(".") if p])