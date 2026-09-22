"""
Merge Forbes Billionaire List CSVs (1996-2025) into a single US-citizens-only,
billionaire-by-year panel, then filter it down to just the people who appear
in the CA Billionaires Revenues and Migration dataset.

Forbes name formats differ across the years:
  - 1996-2000: "Last, First [Middle] [Suffix]"   e.g. "Gates, William H. III"
  - 2001-2025: "First Last[, Suffix]"             e.g. "Bill Gates" / "Herbert Allen, Jr."

Both are normalized into a "First Last[ Suffix]" display form, and into a
looser "match key" (first + last name only, common nicknames folded together,
suffixes dropped) used to join against the CA dataset.

Note: "CA Billionaires Revenues and Migration - Raw Data Collection.csv"
itself is treated as 2026 data (a current snapshot, one year past the last
Forbes CSV) -- see var_model_ca_billionaires.py, which appends it as the
2026 observation before forecasting 2027.

Note: MOVED_OUT_OF_CA drops specific people from the panel starting the year
they left California, so the historical trend reflects who was actually a
CA billionaire in each year rather than crediting California with wealth
that had already relocated.
"""

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CA_FILE = BASE_DIR / "CA Billionaires Revenues and Migration - Raw Data Collection.csv"
OUTPUT_FILE = BASE_DIR / "Forbes_CA_Billionaires_1996_2025.csv"

FIRST_NAME_START_YEAR = 2001  # first year Forbes switched to "First Last" format

# People who moved out of California -- excluded from the panel starting the
# year they left, so the "CA billionaire" trend doesn't keep crediting
# California with wealth that moved elsewhere.
MOVED_OUT_OF_CA = {
    "Larry Ellison": 2020,
    "Drew Houston": 2020,
    "Lynsi Snyder": 2025,
}

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}

# Common nickname -> canonical first-name folding, so e.g. "Bill Gates" (2001+)
# matches "Gates, William H. III" (1996-2000). Best-effort, not exhaustive.
NICKNAME_CANON = {
    "bill": "william", "billy": "william", "will": "william",
    "larry": "lawrence",
    "bob": "robert", "rob": "robert", "robby": "robert", "bobby": "robert",
    "rick": "richard", "dick": "richard", "richie": "richard",
    "dave": "david",
    "chuck": "charles", "charlie": "charles",
    "jim": "james", "jimmy": "james",
    "tom": "thomas", "tommy": "thomas",
    "mike": "michael", "mikey": "michael",
    "steve": "steven",
    "jeff": "jeffrey",
    "ken": "kenneth", "kenny": "kenneth",
    "ed": "edward", "eddie": "edward", "ted": "edward",
    "don": "donald", "donnie": "donald",
    "greg": "gregory",
    "andy": "andrew",
    "joe": "joseph", "joey": "joseph",
    "sam": "samuel", "sammy": "samuel",
    "nick": "nicholas",
    "tony": "anthony",
    "fred": "frederick", "freddy": "frederick",
    "alex": "alexander",
    "matt": "matthew",
    "chris": "christopher",
    "dan": "daniel", "danny": "daniel",
    "gene": "eugene",
    "hank": "henry",
    "walt": "walter",
    "phil": "philip",
    "ray": "raymond",
    "herb": "herbert",
    "nate": "nathan",
    "peggy": "margaret", "maggie": "margaret", "marge": "margaret",
    "liz": "elizabeth", "beth": "elizabeth", "betty": "elizabeth",
    "cathy": "catherine", "kate": "catherine", "katie": "catherine",
    "gus": "augustus",
}


def clean_display_name(raw_name: str, year: int) -> str:
    """Reconstruct a 'First Last[ Suffix]' display name from the raw Forbes name."""
    name = raw_name.strip()
    if "," not in name:
        return name

    if year < FIRST_NAME_START_YEAR:
        # "Last, First [Middle] [Suffix]"
        last, rest = name.split(",", 1)
        tokens = rest.strip().split()
        suffix = None
        if tokens and tokens[-1].strip(".").lower() in SUFFIXES:
            suffix = tokens[-1].strip(".")
            tokens = tokens[:-1]
        if not tokens:
            return last.strip()
        first = tokens[0]
        display = f"{first} {last.strip()}"
        if suffix:
            display = f"{display} {suffix}"
        return display
    else:
        # "First Last, Suffix"
        base, suffix = name.split(",", 1)
        suffix = suffix.strip().rstrip(".")
        return f"{base.strip()} {suffix}" if suffix else base.strip()


def match_key(display_name: str) -> str:
    """Loose join key: first + last token, suffixes dropped, nicknames folded.

    NICKNAME_CANON only folds informal nicknames into a formal canonical
    spelling (e.g. "Bill" -> "William"). It deliberately never folds two
    *formal* name spellings into each other (e.g. "Stephen" is never folded
    to "Steven", even though they're homophones) -- doing so once caused a
    real false match between two unrelated people who share a surname
    ("Steven Cohen", the Point72 hedge fund manager, vs. "Stephen Cohen",
    the Palantir co-founder on the CA list), silently merging their wealth
    histories together.
    """
    cleaned = re.sub(r"[^\w\s]", "", display_name).lower()
    tokens = [t for t in cleaned.split() if t not in SUFFIXES]
    if not tokens:
        return ""
    first, last = tokens[0], tokens[-1]
    first = NICKNAME_CANON.get(first, first)
    return f"{first} {last}"


def load_forbes_year(year: int) -> pd.DataFrame:
    path = BASE_DIR / f"Forbes Billionaire List {year}.csv"
    df = pd.read_csv(path)
    df = df[df["Country of Citizenship"] == "United States"].copy()
    df["Year"] = year
    df["Name"] = df["Name"].apply(lambda n: clean_display_name(n, year))
    df["Match Key"] = df["Name"].apply(match_key)
    for col in ("Source of Wealth", "Industry"):
        if col not in df.columns:
            df[col] = pd.NA
    return df[["Year", "Rank", "Name", "Match Key", "Wealth (in $1B USD)",
               "Country of Citizenship", "Source of Wealth", "Industry"]]


def load_ca_names() -> pd.DataFrame:
    ca = pd.read_csv(CA_FILE)
    ca = ca[["Name"]].dropna().drop_duplicates().copy()
    ca = ca.rename(columns={"Name": "CA Name"})
    ca["Match Key"] = ca["CA Name"].apply(match_key)
    return ca


def main():
    years = range(1996, 2026)
    forbes = pd.concat([load_forbes_year(y) for y in years], ignore_index=True)

    ca_names = load_ca_names()

    merged = forbes.merge(ca_names, on="Match Key", how="inner")
    merged = merged.rename(columns={"Name": "Forbes Name"})
    merged = merged[["CA Name", "Year", "Rank", "Wealth (in $1B USD)",
                      "Country of Citizenship", "Source of Wealth", "Industry",
                      "Forbes Name"]]

    before = len(merged)
    for name, move_year in MOVED_OUT_OF_CA.items():
        merged = merged[~((merged["CA Name"] == name) & (merged["Year"] >= move_year))]
    removed = before - len(merged)

    merged = merged.sort_values(["CA Name", "Year"]).reset_index(drop=True)
    merged.to_csv(OUTPUT_FILE, index=False)

    print(f"Forbes rows (US citizens, 1996-2025): {len(forbes)}")
    print(f"CA billionaires: {len(ca_names)}")
    print(f"Removed {removed} rows for billionaires who moved out of CA: {MOVED_OUT_OF_CA}")
    print(f"Merged rows written to {OUTPUT_FILE.name}: {len(merged)}")


if __name__ == "__main__":
    main()
