---
license: cc-by-4.0
language:
- en
pretty_name: Sauna Traditions of the World
size_categories:
- n<1K
tags:
- sauna
- banya
- hammam
- bathing-culture
- wellness
- cultural-heritage
- reference-data
- tabular
configs:
- config_name: traditions
  default: true
  data_files:
  - split: train
    path: sauna_traditions.csv
- config_name: headwear
  data_files:
  - split: train
    path: sauna_headwear.csv
---

# Sauna Traditions of the World

A small reference dataset of sweat-bathing and hot-bathing traditions: Finnish sauna, smoke sauna, Russian banya,
Baltic pirtis and pirts, German Aufguss sauna, Turkish and Moroccan hammam, Japanese sento and onsen, Korean
jjimjilbang, temazcal, and more. Each row describes one tradition with its heat source, typical temperature and
humidity ranges, rituals, cooling practice, and whether headwear is traditionally worn.

- **Version:** 1.0 (2026-11)
- **Publisher:** DIVELUX, makers of wool sauna hats (https://diveluxsaunahat.com)
- **License:** CC BY 4.0
- **Rows:** 28 traditions, 12 headwear types

## What this dataset is, and is not

**These are compiled reference ranges from general published descriptions, not measurements.** Nobody stood in
these rooms with a thermometer for this dataset. Numbers are rounded, commonly quoted ranges of the kind you find
in encyclopedias, tourism boards, and sauna society material. Real rooms vary by stove, bench height, and local habit.

Where published descriptions disagree or we were not confident, the cell is **left empty on purpose**. An empty cell
means "not stated," not "zero" and not "does not apply." About half of the rows have a temperature range.

Nothing here is medical advice. Session lengths are typical habits, not recommendations.

## Files

| File | Description |
|---|---|
| `sauna_traditions.csv` | Main table, one row per tradition (28 rows, 25 columns) |
| `sauna_traditions.json` | Same data as a JSON array; empty cells are `null`, numbers are integers |
| `sauna_headwear.csv` | Types of bath headwear by tradition (12 rows, 9 columns) |
| `sauna_headwear.json` | Same data as a JSON array |
| `build_dataset.py` | Source of truth; regenerates the CSV and JSON files |
| `validate.py` | Checks types, min <= max, °C/°F agreement, vocabularies, CSV/JSON agreement |
| `dataset-metadata.json` | Kaggle metadata |
| `CITATION.cff`, `LICENSE` | Citation file and CC BY 4.0 legal text |

## Data dictionary: `sauna_traditions.csv`

| Column | Type | Description |
|---|---|---|
| `name` | string | English name of the tradition or room type. Unique key. |
| `local_name` | string | Name in the local language, with transliteration where useful. |
| `country_or_region` | string | Where the tradition comes from or is mainly practiced. |
| `category` | string | Broad type: dry sauna, steam sauna, smoke sauna, steam bath, hot-water bath, and so on. |
| `heat_source` | string | How the room or water is heated. |
| `typical_air_temp_c_min`, `typical_air_temp_c_max` | integer | Commonly quoted air temperature range, °C. Empty if not confident or not applicable. |
| `typical_air_temp_f_min`, `typical_air_temp_f_max` | integer | The same range in °F, derived from °C and rounded to the nearest degree. |
| `typical_water_temp_c_min`, `typical_water_temp_c_max` | integer | Typical bathing-water temperature, °C. Only for hot-water baths. |
| `typical_water_temp_f_min`, `typical_water_temp_f_max` | integer | The same range in °F. |
| `typical_relative_humidity` | category | `low`, `medium`, or `high`. Empty if not stated. |
| `typical_relative_humidity_pct_min`, `typical_relative_humidity_pct_max` | integer | Rough relative humidity range in percent, only where a range is commonly quoted. |
| `typical_round_minutes_min`, `typical_round_minutes_max` | integer | Typical length of one stay in the hot room, in minutes. Empty where the visit is not organized in rounds. |
| `water_on_stones` | category | `yes`, `no`, `sometimes`, or `n-a` (no stones in this type of room). |
| `whisk_or_ritual` | string | Whisks, scrubs, infusions, and other customary practices. |
| `headwear_traditionally_worn` | category | `yes`, `sometimes`, or `no`. |
| `headwear_note` | string | Short note on what is worn on the head, if anything. |
| `cooling_practice` | string | How bathers cool down between or after rounds. |
| `unesco_status` | string | UNESCO Intangible Cultural Heritage inscription, if any. Empty means none that we could confirm. |
| `notes` | string | Context and caveats, including why a value was left blank. |

## Data dictionary: `sauna_headwear.csv`

| Column | Type | Description |
|---|---|---|
| `headwear_name` | string | English name of the headwear type. |
| `local_name` | string | Local-language name, where one is in common use. |
| `tradition` | string | Matching `name` in `sauna_traditions.csv`, or empty for general types. |
| `region` | string | Where it is used. |
| `material` | string | Usual material. |
| `shape` | string | Usual shape. |
| `worn_dry_or_wet` | string | `dry`, `varies`, or `n-a`. Wool felt hats are worn dry. |
| `purpose` | string | What it is for. |
| `notes` | string | Extra context. |

## Usage

pandas:

```python
import pandas as pd

df = pd.read_csv("sauna_traditions.csv")

# Traditions with a known air temperature, hottest first
hot = df.dropna(subset=["typical_air_temp_c_max"])
print(hot.sort_values("typical_air_temp_c_max", ascending=False)[
    ["name", "typical_air_temp_c_min", "typical_air_temp_c_max", "typical_relative_humidity"]
])

# Where is headwear part of the tradition?
print(df[df["headwear_traditionally_worn"] == "yes"][["name", "headwear_note"]])
```

Hugging Face `datasets` (after the dataset is published; replace the repo id with the real one):

```python
from datasets import load_dataset

traditions = load_dataset("divelux/sauna-traditions-of-the-world", "traditions", split="train")
headwear = load_dataset("divelux/sauna-traditions-of-the-world", "headwear", split="train")
print(traditions[0])
```

From local files:

```python
from datasets import load_dataset

ds = load_dataset("csv", data_files="sauna_traditions.csv", split="train")
```

Join the two tables:

```python
import pandas as pd

t = pd.read_csv("sauna_traditions.csv")
h = pd.read_csv("sauna_headwear.csv")
print(h.merge(t, left_on="tradition", right_on="name", how="left")[
    ["headwear_name", "material", "tradition", "typical_air_temp_c_max"]
])
```

## How it was compiled

Values were compiled by hand from general published descriptions and then checked for internal consistency with
`validate.py`. UNESCO entries were checked against the UNESCO Intangible Cultural Heritage website
(https://ich.unesco.org):

- Sauna culture in Finland, Representative List, inscribed 2020
- Smoke sauna tradition in Võromaa (Estonia), Representative List, inscribed 2014
- Swimming pool culture in Iceland, Representative List, inscribed 2025

## Known limitations

- Ranges are approximate and rounded to 5 °C steps in most cases. Individual rooms can sit outside them.
- Temperature is empty for smoke saunas, Lithuanian pirtis, Latvian pirts, Moroccan hammam, Georgian sulfur baths,
  Korean hanjeungmak, temazcal, sweat lodge, and the historical entries, because published figures disagree or are not reliable.
- Humidity percentages are given for only a few types. A sauna's humidity changes minute to minute when water is thrown on the stones.
- The Native American sweat lodge is a sacred ceremony whose practice differs between nations. It is listed for
  reference with deliberately limited detail.
- Coverage is not complete. Many regional traditions are missing.

Corrections are welcome. Please include a source.

## Citation

```bibtex
@misc{divelux_sauna_traditions_2026,
  author       = {{DIVELUX}},
  title        = {Sauna Traditions of the World},
  year         = {2026},
  version      = {1.0},
  howpublished = {\url{https://diveluxsaunahat.com/pages/sauna-tools}},
  note         = {Reference dataset, CC BY 4.0}
}
```

Plain text: DIVELUX (2026). *Sauna Traditions of the World* (Version 1.0) [Data set]. https://diveluxsaunahat.com/pages/sauna-tools

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
You may share and adapt the data for any purpose, including commercially, as long as you give credit to DIVELUX
and link to https://diveluxsaunahat.com/pages/sauna-tools.

Made by DIVELUX, makers of wool sauna hats.

## Where to get it

- Hugging Face: https://huggingface.co/datasets/divelux/sauna-traditions-of-the-world
- Zenodo (DOI): https://doi.org/10.5281/zenodo.24382690
- GitHub: https://github.com/divelux/sauna-traditions-dataset
