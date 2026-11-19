#!/usr/bin/env python3
"""Validate the Sauna Traditions of the World dataset. Exit code 0 = all checks pass.

Checks: required columns, row counts, unique names, numeric types, min <= max,
Celsius/Fahrenheit agreement, plausible ranges, controlled vocabularies,
CSV/JSON agreement, cross-file references and banned wording.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
errors = []


def err(msg):
    errors.append(msg)


def load_csv(name):
    with open(os.path.join(HERE, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


T_COLS = [
    "name", "local_name", "country_or_region", "category", "heat_source",
    "typical_air_temp_c_min", "typical_air_temp_c_max", "typical_air_temp_f_min", "typical_air_temp_f_max",
    "typical_water_temp_c_min", "typical_water_temp_c_max", "typical_water_temp_f_min", "typical_water_temp_f_max",
    "typical_relative_humidity", "typical_relative_humidity_pct_min", "typical_relative_humidity_pct_max",
    "typical_round_minutes_min", "typical_round_minutes_max",
    "water_on_stones", "whisk_or_ritual", "headwear_traditionally_worn", "headwear_note",
    "cooling_practice", "unesco_status", "notes",
]
H_COLS = ["headwear_name", "local_name", "tradition", "region", "material", "shape",
          "worn_dry_or_wet", "purpose", "notes"]
INT_COLS = [c for c in T_COLS if c.endswith(("_min", "_max"))]
PAIRS = [(c, c[:-4] + "_max") for c in T_COLS if c.endswith("_min")]
VOCAB = {
    "typical_relative_humidity": {"", "low", "medium", "high"},
    "water_on_stones": {"", "yes", "no", "sometimes", "n-a"},
    "headwear_traditionally_worn": {"", "yes", "sometimes", "no"},
}
RANGES = {  # plausible bounds, inclusive
    "typical_air_temp_c": (30, 120), "typical_water_temp_c": (30, 48),
    "typical_relative_humidity_pct": (0, 100), "typical_round_minutes": (1, 60),
}
# UNESCO entries verified against ich.unesco.org; anything else must be blank.
UNESCO_OK = {
    "Finnish sauna": "2020",
    "Estonian smoke sauna (Võromaa)": "2014",
    "Icelandic geothermal pool and hot tub": "2025",
}
BANNED = ["detox", "toxin", "burns fat", "burn fat", "cure", "heals", "soak the hat",
          "wet the hat", "dampen", "best seller", "amazon"]


def to_int(row, col, label):
    v = row[col].strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        err(f"{label}: {col} is not an integer: {v!r}")
        return None


def check_traditions(rows):
    if not 25 <= len(rows) <= 40:
        err(f"sauna_traditions.csv: expected 25-40 rows, got {len(rows)}")
    if list(rows[0].keys()) != T_COLS:
        err("sauna_traditions.csv: column list or order differs from the data dictionary")
    names = [r["name"] for r in rows]
    if len(set(names)) != len(names):
        err("sauna_traditions.csv: duplicate names")
    for r in rows:
        label = r["name"] or "<no name>"
        for col in ("name", "country_or_region", "category", "heat_source"):
            if not r[col].strip():
                err(f"{label}: required field {col} is empty")
        vals = {c: to_int(r, c, label) for c in INT_COLS}
        for lo, hi in PAIRS:
            a, b = vals[lo], vals[hi]
            if (a is None) != (b is None):
                err(f"{label}: {lo}/{hi} must both be set or both be empty")
            elif a is not None and a > b:
                err(f"{label}: {lo} ({a}) > {hi} ({b})")
        for kind in ("air", "water"):
            for end in ("min", "max"):
                c = vals[f"typical_{kind}_temp_c_{end}"]
                f = vals[f"typical_{kind}_temp_f_{end}"]
                if (c is None) != (f is None):
                    err(f"{label}: {kind} temp {end}: Celsius and Fahrenheit must both be set or both be empty")
                elif c is not None and abs((c * 9 / 5 + 32) - f) > 1:
                    err(f"{label}: {kind} temp {end}: {c} °C does not match {f} °F")
        for prefix, (lo, hi) in RANGES.items():
            for end in ("min", "max"):
                v = vals[f"{prefix}_{end}"]
                if v is not None and not lo <= v <= hi:
                    err(f"{label}: {prefix}_{end}={v} outside plausible range {lo}-{hi}")
        for col, allowed in VOCAB.items():
            if r[col] not in allowed:
                err(f"{label}: {col}={r[col]!r} not in {sorted(allowed)}")
        if vals["typical_relative_humidity_pct_min"] is not None and not r["typical_relative_humidity"]:
            err(f"{label}: humidity percent given without a low/medium/high level")
        u = r["unesco_status"].strip()
        if u:
            if label not in UNESCO_OK:
                err(f"{label}: unesco_status set but entry is not on the verified list")
            elif UNESCO_OK[label] not in u:
                err(f"{label}: unesco_status should mention year {UNESCO_OK[label]}")
        elif label in UNESCO_OK:
            err(f"{label}: verified UNESCO entry is missing")
        for col, v in r.items():
            if v != v.strip():
                err(f"{label}: {col} has leading/trailing whitespace")
            if "\n" in v:
                err(f"{label}: {col} contains a line break")
            low = v.lower()
            for word in BANNED:
                if word in low:
                    err(f"{label}: {col} contains banned wording {word!r}")


def check_json(rows, name, cols, int_cols):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        data = json.load(f)
    if len(data) != len(rows):
        err(f"{name}: {len(data)} records but CSV has {len(rows)}")
        return
    for rec, row in zip(data, rows):
        if list(rec.keys()) != cols:
            err(f"{name}: keys differ from CSV columns")
            return
        for c in cols:
            j, v = rec[c], row[c]
            expect = None if v == "" else (int(v) if c in int_cols else v)
            if j != expect:
                err(f"{name}: {row[cols[0]]}: {c} JSON {j!r} != CSV {expect!r}")


def check_headwear(rows, tradition_names):
    if list(rows[0].keys()) != H_COLS:
        err("sauna_headwear.csv: column list or order differs from the data dictionary")
    for r in rows:
        label = "headwear: " + r["headwear_name"]
        for col in ("headwear_name", "region", "material", "shape", "worn_dry_or_wet", "purpose"):
            if not r[col].strip():
                err(f"{label}: required field {col} is empty")
        if r["tradition"] and r["tradition"] not in tradition_names:
            err(f"{label}: tradition {r['tradition']!r} not found in sauna_traditions.csv")
        mat, worn = r["material"].lower(), r["worn_dry_or_wet"].lower()
        if mat.startswith("wool felt") and not worn.startswith("dry"):
            err(f"{label}: wool felt headwear must be listed as worn dry")
        if "wet" in worn:
            err(f"{label}: worn_dry_or_wet must be dry, varies or n-a")
        for col, v in r.items():
            for word in BANNED:
                if word in v.lower():
                    err(f"{label}: {col} contains banned wording {word!r}")


def main():
    t = load_csv("sauna_traditions.csv")
    h = load_csv("sauna_headwear.csv")
    check_traditions(t)
    check_json(t, "sauna_traditions.json", T_COLS, set(INT_COLS))
    check_headwear(h, {r["name"] for r in t})
    check_json(h, "sauna_headwear.json", H_COLS, set())
    filled = sum(1 for r in t if r["typical_air_temp_c_min"] or r["typical_water_temp_c_min"])
    print(f"sauna_traditions.csv: {len(t)} rows, {len(T_COLS)} columns, {filled} rows with a temperature range")
    print(f"sauna_headwear.csv:   {len(h)} rows, {len(H_COLS)} columns")
    if errors:
        print(f"FAILED: {len(errors)} problem(s)")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("OK: all checks passed")


if __name__ == "__main__":
    main()
