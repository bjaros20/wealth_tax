# NBER Version (2026): Litigation-Risk-Weighted Approach

Replication materials for the NBER working paper version of

**"The Net Present Value of the California Billionaire Tax Act"** (September 2026).
Benjamin Jaros and Joshua Rauh.
[NBER](https://www.nber.org/system/files/chapters/c15504/c15504.pdf)

The paper has two versions, each built on a different approach to estimating the
revenue the Act will collect. Both are published in this repository so the
assumptions behind each can be compared directly:

1. **European wealth tax elasticity approach** (SSRN version, repository root).
   [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6340778)
2. **Litigation-risk-weighted approach** (NBER version, this folder).
   [NBER](https://www.nber.org/system/files/chapters/c15504/c15504.pdf)

This folder holds the materials specific to the second approach. Materials the two
approaches share, such as the income tax Monte Carlo in Section 5.1, are at the
repository root.

## Assumptions under each approach

| | European elasticity approach (SSRN) | Litigation-risk-weighted approach (NBER) |
|---|---|---|
| **Domestic base** | 212 billionaires, $1,894.8B net worth | Same |
| **Valuation vintage** | Snapshot (Jan 1, 2026): $94.20B face value at 5% | Grown 7% to the Dec 31, 2026 valuation date: $100.9B face value |
| **Confirmed pre-snapshot departures** | 7 departures removed; ceiling $67.51B | Same 7 removed at grown vintage; ceiling $72.06B |
| **Unobserved (stealth) departures** | Predicted from the European literature: Brülhart et al. (2022) migration semi-elasticity of 10.32, with 12–13 viewed as plausible for interstate mobility | Not predicted directly; the observed departures are treated as a floor, and the European elasticities serve as an independent check on the final estimate |
| **Litigation risk** | Not applied | Probability the Act survives constitutional challenge, q = 0.50 (ASC 740-10 "more likely than not"), applied to the recognized base |
| **Zuckerberg (left Feb 2026)** | Kept in base | Excluded from the recognized base in the central estimate; included in the upper end of the range |
| **Wealth tax revenue** | ~$40B (range $35–46B) | ~$30B (range $28–36B) |
| **Annual billionaire income tax, C** | $3.3–5.8B | Same |
| **NPV formula** | NPV = WT − f·C / (r − g), a growing perpetuity with (r − g) calibrated to the dividend yield | Same |
| **Departure fraction, f** | Implied by revenue: f = 1 − WT / 94.20 | Drawn independently: f ~ U[0.30, 0.60] |
| **Simulation draws (100,000)** | WT ~ U[$35B, $67.51B]; C ~ U[$3.3B, $5.8B]; (r − g) ~ U[1.5%, 4.5%] | WT ~ U[$0B, $72B] (0 = Act struck down; 72 = ceiling); C ~ U[$3.3B, $5.8B]; (r − g) ~ U[1.5%, 4.5%]; f ~ U[0.30, 0.60] |
| **Mean NPV / share of draws negative** | −$24.7B / 71% | −$38.9B / 85% |
| **Simulation script** | `../NPV_data/NPV_dist.R` | `NPV_data/NPV_dist_v8.R` |

## Contents

| Path | Paper section | Description |
|---|---|---|
| `NPV_data/final.csv` | Sections 3–4 | Person-level tax base: 240 rows (212 domestic, 28 international). Net worth, residential real estate exclusion, taxable base at the snapshot and at 7% growth, 5% face value, and each person's treatment bucket (stayer, confirmed departure, pre-filing departure, ambiguous, Zuckerberg, international) with the reason. |
| `NPV_data/NPV_dist_v8.R` | Section 5.4, Figure 3 | 100,000-draw NPV simulation. |
| `NPV_plots/npv_distribution_v8.{png,pdf}` | Figure 3 | Distribution of NPV. |
| `Forbes_Projections/` | Section 3.2, Appendix C, Figure 4 | California billionaire net worth, 1996–2026, and the 2027 VAR(2) and 7% growth projections. |
| `NPV_data/severability_survey.csv` | Section 2.4, Appendix E | Severability clauses in California tax measures, 2000–2026, with clause text and source. |
| `appendixF_figures.py`, `NPV_plots/F1_unlisted_population.{png,pdf}` | Appendix F, Figure 5 | Reconstructed count of California returns above each wealth threshold, compared with Forbes and the Pareto extrapolation. |

Section 5.1 is shared by both approaches and lives at the repository root in
`../NPV_data/monte_carlo_sim.R`:

- **Figure 1** (Pareto tail fit): calculated in section 1 of the script ("Data and Pareto fit"), an OLS fit of the Pareto survival function to six FTB cumulative filer counts (α̂ = 1.44, R² = 0.999).
- **Figure 2** (income tax Monte Carlo): simulated in sections 2 onward of the same script; the paper uses `../NPV_plots/billionaire_tax_monte_carlo_v3.png`.

## Replication

**NPV simulation (R).** Requires `ggplot2` and `ggthemes`. From `NPV_data/`:

```
Rscript NPV_dist_v8.R
```

Reproduces mean NPV −$38.9B, median −$35.3B, SD $37.6B, P5/P95 −$107.9B/$15.9B, and 85.2% of draws negative (seed 2026).

**Net worth trajectory (Python).** Requires `pandas`, `numpy`, `statsmodels`, `matplotlib`. From `Forbes_Projections/`:

```
python var_model_ca_billionaires.py    # VAR(2): 2027 point $2,036.6B, 95% CI [$1,770.6B, $2,302.6B]
python plot_ca_billionaire_trend.py    # Figure 4
```

`Forbes_CA_Billionaires_1996_2025.csv` is the California-resident subset of the annual Forbes lists. It was built by `merge_forbes_ca_billionaires.py`, which is included for transparency; the full annual Forbes lists it reads are not redistributed here. `CA Billionaires Assets.csv` holds the 2026 net worth of the 212 domestic billionaires and its 7% growth total, used for the 2026 observation and the 7% projection.

**Appendix F figure (Python).** Requires `matplotlib`. From this folder:

```
python appendixF_figures.py
```

Writes `F1_unlisted_population` (Figure 5) to `NPV_plots/`. The series are entered directly in the script; they come from capitalizing California Franchise Tax Board income (Table B-4A, TY 2023) with Survey of Consumer Finances (2022) dispersion.
