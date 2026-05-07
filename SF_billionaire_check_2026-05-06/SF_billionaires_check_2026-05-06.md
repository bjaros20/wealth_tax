# SF Billionaire Count — Reproduction and Status Notes

**Date:** 2026-05-06
**Author:** Ben Jaros
**Re:** Two questions on the "59 billionaires in San Francisco" figure cited from the SSRN paper

---

## TL;DR

- **The 59 figure reproduces from the source Excel.** File: `wealth_tax/NPV_data/CA_Billionaires_Revenues_and_Migration_final.xlsx`, sheet `Calculations_Preferred`, column E ("Residence") = exactly `"San Francisco"`. Data as-of approximately early March 2026 (file mtime 2026-03-09).
- **Methodology rule (important):** SF *proper* only. Atherton, Palo Alto, Woodside, Hillsborough, Menlo Park, Los Altos, Burlingame, etc. are excluded. This is why our number is lower than Wealth-X's metro-area figures (~72/75 Bay Area).
- **Scope of this brief:** I am NOT producing an apples-to-apples 2019/2020 comparison or a full residency re-audit. I'm reporting what's in the dataset, flagging the small number of post-cutoff signals I'm aware of, and pointing to our public data.

---

## 1. Source file and reproduction of the 59 figure

**File path:** `/Users/benjaros/Documents/GitHub/wealth_tax/NPV_data/CA_Billionaires_Revenues_and_Migration_final.xlsx`
**Sheet used for the headline:** `Calculations_Preferred` (and `Calculations_Expanded`, which agree)
**Column E:** `Residence`
**Filter:** rows where `Residence == "San Francisco"` (exact string)
**Result:** **59 rows**

Notes on internal consistency:

- The `Raw_Data_Collection` sheet (and the standalone `Raw_Data_Collection.xlsx`) shows **58** SF rows over 214 names. The `Calculations_Preferred` and `Calculations_Expanded` sheets (212 names) show **59** SF rows. The deltas are: `Calculations_Preferred` adds Jack Clark and David Sacks and drops Drew Houston relative to `Raw_Data_Collection`. The 59 figure used in the paper corresponds to `Calculations_Preferred`, which is the version the `Summary_Preferred` pivot table reads from.
- The `Summary_Preferred` sheet's residence-frequency table (cell N2:O2) literally lists `San Francisco | 59`, confirming the cited figure matches what the workbook computes.
- As-of date: best estimate is **early March 2026** based on file mtime (`2026-03-09 21:57`) and the latest article URLs cited in the workbook (multiple 2026-01 sources for moves; one 2026-01-19 source is the latest dated URL). The dataset has no single "as-of" cell — that's a workbook hygiene gap.

The full 59-name list with ranks and net worths is saved at:
`/Users/benjaros/Documents/GitHub/wealth_tax/SF_billionaire_check_2026-05-06/sf_billionaires_59.json`

---

## 2. Post-cutoff status notes

I did NOT do a full residency audit of all 59. I did targeted searches on the high-profile names and known relocators. Findings:

**Already coded as moving in our dataset (1):**
- **David Sacks** — `moving=Y`. Austin, TX. Source: SF Standard / TechCrunch coverage of Craft Ventures' Austin office, late 2025.

**Known prior-period mover that Forbes still tags "San Francisco" (1):**
- **Marc Benioff** — public reporting (SF Standard, Oct 2025) indicates he switched CA voter registration to Hawaii in 2021. Forbes still lists his residence as San Francisco. Whether to re-classify him depends on whether you anchor on Forbes' field (which we did) or on voter-registration / actual primary residence (where he'd come out as HI).

**Possible reclassifications, weak signal (2):**
- **Laurene Powell Jobs** — Forbes lists San Francisco; multiple recent profiles describe Palo Alto as primary residence and the Pacific Heights mansion as a secondary SF property. Reasonable people could code this either way; we coded SF.
- **Mark Pincus** — long-standing Chicago (Lincoln Park) family residence; recent SF property churn. Reasonable people could code this either way; we coded SF.

**Confirmed still in SF (specific, recent evidence):**
- Sam Altman (Russian Hill — confirmed via April 2026 SF Standard coverage)
- Jack Dorsey, Brian Chesky, Dustin Moskovitz, Tom Steyer (Sea Cliff, running for CA governor 2026), Chris Larsen, Michael Moritz, Aneel Bhusri, Dylan Field, Tony Xu, Max Levchin, Ben Silbermann, Kevin Systrom, Evan Williams, Tom Preston-Werner — no public departure signals; multiple recent SF-resident-coded references.

**Recently-minted billionaires whose personal residence is not publicly disclosed (we tagged SF based on company HQ + bios):**
- Dario Amodei, Daniela Amodei, Tom Brown, Jack Clark, Sam McCandlish (Anthropic — Jan 2026 13-yr 420k sqft SF lease)
- Aman Sanger, Michael Truell (Cursor/Anysphere, North Beach SF office)
- Brendan Foody, Surya Midha, Adarsh Hiremath (Mercor, 181 Fremont SF)
- Alexandr Wang (Scale AI HQ in SF; he is now Meta CAIO so his personal residence in 2026 is ambiguous)

**Not individually re-verified (33 names):** Nathan Blecharczyk, Gordon Getty, Jim Coulter, David Baszucki, Scott Crabill, Holden Spaht, Dagmar Dolby, Sanjit Biswas, John Bicket, John Fisher, Parker Conrad, Jay Paul, Vasily Shikin, Fred Ehrsam, John Pritzker, Jon Winkelried, Robert Fisher, William Fisher, Paul Sciarra, Kevin Marchetti, Michael Cagney, Doris Fisher, Nikil Viswanathan, Mike Speiser, Steve Huffman, Stanley Tang, Jeff Lawson, Evan Wallace, Trae Stephens. Treat the dataset's `moving=N` as the as-of-March-2026 finding for these absent contrary evidence.

**Net change estimate (rough):**
- Strict-from-our-dataset reading: 59 → **58** (back out Sacks, who's already coded as moving).
- If you re-code Benioff to HI: 59 → **57**.
- Plausible range under different judgment calls on dual-residence cases (Powell Jobs, Pincus): **55–58**.

I did not surface any new SF arrivals in 2026 outside the 59 in targeted searches.

---

## 3. Pre-COVID 2019/2020 comparison

**Per the scope decision, I am not producing this.** Reasons:

- A methodology-matched count would require pulling archive.org snapshots of `forbes.com/profile/{name}` from late 2019 / early 2020 for every then-current US billionaire and re-coding the "Residence" field against our SF-proper rule. That's a 1–2 day data-collection task and we are not doing it here.
- Popular-press 2019/2020 counts (Wealth-X "75 in SF", "72 Bay Area", etc.) use metro-area definitions and are systematically higher than ours by ~15–20. They are not directly comparable.

Any pre-COVID/post-COVID comparison should either (a) be done under matched methodology (which we have not done for 2019/2020), or (b) be characterized as anecdotal directional context. The qualitative direction is clearly "up" — Anthropic's five founders, Cursor's two, Mercor's three, Sam Altman, Alexandr Wang, and several others in the 59 did not yet exist as billionaires in 2019/2020 — but I'm not putting a number on the delta.

---

## 4. Methodology note

The "59 San Francisco billionaires" figure in the paper applies a strict residence-coding rule: a name is counted only if Forbes' Real-Time Billionaires "Residence" field is exactly *San Francisco*. Bay Area suburbs (Atherton, Palo Alto, Woodside, Hillsborough, Menlo Park, Los Altos, Burlingame, etc.) are excluded. This is intentionally narrower than the metro-area definitions used by Wealth-X (which produces figures around 72 for the Bay Area), because the underlying question — who would be a California-resident taxpayer for purposes of a city-targeted analysis — turns on city of residence, not CBSA. The figure is as of approximately March 2026 and was hand-coded from public Forbes profiles plus public real-estate and news signals; the underlying Excel and the 59-name list are publicly reproducible from `benjaros/wealth_tax` on GitHub.

---

## 5. Confidence flags

- **High confidence:** 59 reproduces from the workbook; methodology rule is documented and applied consistently; SF-proper exclusion of Peninsula/Marin localities is correct.
- **Medium confidence:** As-of date is "early March 2026" rather than a specific cell in the workbook — derived from file mtime and the latest cited URLs.
- **Lower confidence:** Whether Benioff (HI voter registration since 2021), Powell Jobs (Palo Alto-primary), and Pincus (Chicago-primary) should be coded as SF in a strictly-applied "primary residence" rule. We coded all three SF, in line with Forbes' field. Any reader citing specific names may want to flag these three explicitly.
- **Disclosed but not re-verified:** Personal residences of newly-minted AI-era billionaires (Anthropic 5, Cursor 2, Mercor 3) are inferred from company HQ + public bios, not from voter-registration or property-record evidence. Best characterized as "based in San Francisco" rather than asserted as primary residents.

---

## Files

- `/Users/benjaros/Documents/GitHub/wealth_tax/NPV_data/CA_Billionaires_Revenues_and_Migration_final.xlsx` — source workbook
- `/Users/benjaros/Documents/GitHub/wealth_tax/NPV_data/Raw_Data_Collection.xlsx` — raw collection sheet (58 SF; subset of above)
- `/Users/benjaros/Documents/GitHub/wealth_tax/SF_billionaire_check_2026-05-06/sf_billionaires_59.json` — the 59 names with ranks, net worths, notes
- `/Users/benjaros/Documents/GitHub/wealth_tax/SF_billionaire_check_2026-05-06/SF_billionaires_check_2026-05-06.md` — this brief
