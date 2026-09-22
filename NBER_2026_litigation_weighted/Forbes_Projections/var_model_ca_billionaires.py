"""
VAR model on the aggregated CA-billionaire Forbes panel (1996-2025), extended
with one additional real observation for 2026, then forecast one year ahead
to 2027.

Pipeline:
  1. Aggregate Forbes_CA_Billionaires_1996_2025.csv (output of
     merge_forbes_ca_billionaires.py) into annual series: total wealth,
     average wealth, and count of CA billionaires appearing on the Forbes
     list each year.
  2. Append a 2026 observation built from the net_worth_usd column of
     "CA Billionaires Assets.csv" (the Domestic list), which is treated as a
     2026 snapshot (there is no Forbes 2026.csv). This makes the last
     historical year 2026, so the model's one-step-ahead forecast lands on
     2027.
  3. Pre-estimation diagnostics on each level series: ADF (stationarity),
     KPSS (stationarity, opposite null), Durbin-Watson and Ljung-Box
     (autocorrelation). Difference any series that fails to reject a unit
     root, and re-test.
  4. Pick VAR lag order via information criteria (AIC/BIC/HQIC/FPE).
  5. Fit the VAR model on the stationary (possibly differenced) series.
  6. Post-estimation diagnostics: residual autocorrelation (Durbin-Watson,
     Ljung-Box per equation) and stability check (roots of the reverse
     characteristic polynomial).

Note: total_wealth = avg_wealth * count by construction, so all three are
never used together in the VAR (perfectly collinear). The final model uses
total_wealth and count; avg_wealth is reported in the diagnostics for
reference but dropped before fitting.

Also note: the 2026 point uses all 212 people in CA Billionaires Assets.csv
(ranked 1 through David Sacks), not just the subset that historically
matched Forbes -- it's the best available stand-in for "what a Forbes 2026
list would show for CA billionaires," not a like-for-like continuation of
the fluctuating Forbes-matched cohort used in 1996-2025.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Forbes_CA_Billionaires_1996_2025.csv"
ASSETS_FILE = BASE_DIR / "CA Billionaires Assets.csv"
VAR_SERIES_FILE = BASE_DIR / "CA_Billionaires_VAR_Annual_Series.csv"
FORECAST_FILE = BASE_DIR / "CA_Billionaires_VAR_Forecast.csv"

ASSETS_YEAR = 2026  # treated as the current-year snapshot; see module docstring

VAR_COLUMNS = ["total_wealth", "count"]  # columns actually fit in the VAR
SIGNIFICANCE = 0.05


def load_2026_observation() -> dict:
    """Build the 2026 total_wealth/avg_wealth/count row from the net_worth_usd
    column of CA Billionaires Assets.csv (Domestic list; there is no Forbes
    2026.csv to aggregate instead)."""
    df = pd.read_csv(ASSETS_FILE)
    people = df.dropna(subset=["name"]).copy()
    net_worth = pd.to_numeric(people["net_worth_usd"], errors="coerce")
    if net_worth.isna().any():
        bad = people.loc[net_worth.isna(), "name"].tolist()
        raise ValueError(f"Could not parse net_worth_usd for: {bad}")
    total_wealth_b = net_worth.sum() / 1e9  # match Forbes's $1B USD units
    count = len(people)
    return {
        "Year": ASSETS_YEAR,
        "total_wealth": total_wealth_b,
        "avg_wealth": total_wealth_b / count,
        "count": count,
    }


def build_annual_series() -> pd.DataFrame:
    df = pd.read_csv(INPUT_FILE)
    agg = (
        df.groupby("Year")
        .agg(
            total_wealth=("Wealth (in $1B USD)", "sum"),
            avg_wealth=("Wealth (in $1B USD)", "mean"),
            count=("CA Name", "nunique"),
        )
        .reset_index()
        .sort_values("Year")
    )

    row_2026 = load_2026_observation()
    if row_2026["Year"] in set(agg["Year"]):
        raise ValueError(f"{row_2026['Year']} already present in {INPUT_FILE.name}; "
                          f"refusing to overwrite it with the CA Revenues snapshot.")
    agg = pd.concat([agg, pd.DataFrame([row_2026])], ignore_index=True).sort_values("Year")

    full_years = pd.DataFrame({"Year": range(agg["Year"].min(), agg["Year"].max() + 1)})
    agg = full_years.merge(agg, on="Year", how="left").set_index("Year")
    if agg.isna().any().any():
        missing = agg[agg.isna().any(axis=1)].index.tolist()
        raise ValueError(f"Annual series has gaps for year(s): {missing}. "
                          f"VAR requires an unbroken annual index.")
    agg.to_csv(VAR_SERIES_FILE)
    return agg


def adf_report(series: pd.Series, label: str) -> dict:
    stat, pvalue, used_lag, nobs, crit, _ = adfuller(series, autolag="AIC")
    stationary = pvalue < SIGNIFICANCE
    print(f"  ADF  [{label}]: stat={stat:.4f}  p={pvalue:.4f}  lags={used_lag}  "
          f"=> {'stationary' if stationary else 'unit root (non-stationary)'}")
    return {"test": "ADF", "series": label, "stat": stat, "pvalue": pvalue, "stationary": stationary}


def kpss_report(series: pd.Series, label: str) -> dict:
    stat, pvalue, lags, crit = kpss(series, regression="c", nlags="auto")
    # KPSS null is "series IS stationary" -- opposite of ADF's null.
    stationary = pvalue >= SIGNIFICANCE
    print(f"  KPSS [{label}]: stat={stat:.4f}  p={pvalue:.4f}  lags={lags}  "
          f"=> {'stationary' if stationary else 'non-stationary'}")
    return {"test": "KPSS", "series": label, "stat": stat, "pvalue": pvalue, "stationary": stationary}


def autocorrelation_report(series: pd.Series, label: str) -> dict:
    dw = durbin_watson(series - series.mean())
    lb = acorr_ljungbox(series, lags=[min(5, len(series) // 2 - 1)], return_df=True)
    lb_pvalue = lb["lb_pvalue"].iloc[0]
    print(f"  Durbin-Watson [{label}]: {dw:.4f} (~2 = no autocorrelation, "
          f"<2 = positive, >2 = negative)")
    print(f"  Ljung-Box     [{label}]: p={lb_pvalue:.4f}  "
          f"=> {'no significant autocorrelation' if lb_pvalue >= SIGNIFICANCE else 'significant autocorrelation'}")
    return {"series": label, "durbin_watson": dw, "ljung_box_pvalue": lb_pvalue}


def make_stationary(annual: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Difference any column that fails to reject a unit root; report the order used."""
    diff_order = {}
    stationary_cols = {}
    for col in VAR_COLUMNS:
        series = annual[col]
        print(f"\n--- {col} (level) ---")
        adf = adf_report(series, f"{col} level")
        kpss_report(series, f"{col} level")
        autocorrelation_report(series, f"{col} level")

        if adf["stationary"]:
            diff_order[col] = 0
            stationary_cols[col] = series
        else:
            diff = series.diff().dropna()
            print(f"\n--- {col} (1st difference) ---")
            adf_report(diff, f"{col} diff1")
            kpss_report(diff, f"{col} diff1")
            autocorrelation_report(diff, f"{col} diff1")
            diff_order[col] = 1
            stationary_cols[col] = diff

    common_index = None
    for series in stationary_cols.values():
        common_index = series.index if common_index is None else common_index.intersection(series.index)
    stationary_df = pd.DataFrame({col: s.loc[common_index] for col, s in stationary_cols.items()})
    return stationary_df, diff_order


def select_lag_order(stationary_df: pd.DataFrame) -> int:
    model = VAR(stationary_df)
    # With ~30 annual observations, testing up to 8 lags leaves too few
    # degrees of freedom (2 vars x 8 lags + const = 18 params on ~21 usable
    # rows) and tends to pick the search ceiling rather than a genuine
    # interior minimum. Cap the search modestly for this sample size.
    max_lags = max(1, min(4, (len(stationary_df) - 1) // 5))
    selection = model.select_order(maxlags=max_lags)
    print(selection.summary())
    print(f"Criteria picks -- AIC: {selection.aic}, BIC: {selection.bic}, HQIC: {selection.hqic}")

    # AIC/BIC/HQIC pick the best in-sample fit, but a lag order can fit well
    # and still be an unstable (explosive) model when there are this few
    # observations per parameter -- useless for forecasting. Only choose
    # among lag orders that are actually stable.
    print(f"\nChecking stability at each candidate lag order (1..{max_lags}):")
    stable_candidates = []
    for p in range(1, max_lags + 1):
        fitted = model.fit(p)
        stable = fitted.is_stable()
        print(f"  VAR({p}): stable={stable}  AIC={fitted.aic:.4f}")
        if stable:
            stable_candidates.append((p, fitted.aic))

    if not stable_candidates:
        raise RuntimeError(
            f"No stable VAR found for lag orders 1..{max_lags}. Refusing to "
            f"pick an unstable model -- an unstable VAR's forecasts diverge "
            f"and shouldn't be used. Consider a different variable set or "
            f"transformation."
        )

    chosen = min(stable_candidates, key=lambda pair: pair[1])[0]
    print(f"Selected lag order (lowest AIC among STABLE candidates): {chosen}")
    return chosen


def fit_var(stationary_df: pd.DataFrame, lag_order: int):
    model = VAR(stationary_df)
    results = model.fit(lag_order)
    print(results.summary())
    return results


def post_estimation_diagnostics(results, stationary_df: pd.DataFrame):
    print("\n=== Residual diagnostics ===")
    resid = results.resid
    for col in stationary_df.columns:
        autocorrelation_report(resid[col], f"{col} residuals")

    print("\n=== Stability check ===")
    print(f"Is stable (all eigenvalues inside unit circle): {results.is_stable()}")

    print("\n=== Granger causality ===")
    cols = list(stationary_df.columns)
    for target in cols:
        causing = [c for c in cols if c != target]
        gc = results.test_causality(target, causing, kind="f")
        print(f"  {causing} -> {target}: F={gc.test_statistic:.4f}  p={gc.pvalue:.4f}  "
              f"=> {'significant' if gc.pvalue < SIGNIFICANCE else 'not significant'}")


def forecast_one_step(results, stationary_df: pd.DataFrame, annual: pd.DataFrame,
                       diff_order: dict, lag_order: int):
    """Forecast 1 step ahead, invert differencing back to levels, and save to CSV."""
    last_obs = stationary_df.values[-lag_order:]
    point = results.forecast(last_obs, steps=1)[0]
    _, lower, upper = results.forecast_interval(last_obs, steps=1, alpha=0.05)
    lower, upper = lower[0], upper[0]

    next_year = int(annual.index[-1]) + 1
    print(f"\n=== One-year-ahead forecast: {next_year} ===")
    row = {"Year": next_year}
    for i, col in enumerate(stationary_df.columns):
        last_level = annual[col].iloc[-1]
        if diff_order[col] == 1:
            # forecast is a change; add it back to the last observed level.
            level_point = last_level + point[i]
            level_lower = last_level + lower[i]
            level_upper = last_level + upper[i]
        else:
            level_point, level_lower, level_upper = point[i], lower[i], upper[i]
        row[f"{col}_point"] = level_point
        row[f"{col}_lower"] = level_lower
        row[f"{col}_upper"] = level_upper
        print(f"  {col}: {level_point:,.2f}  (95% CI: {level_lower:,.2f} to {level_upper:,.2f})  "
              f"[{annual.index[-1]} level was {last_level:,.2f}]")

    forecast_df = pd.DataFrame([row]).set_index("Year")
    forecast_df.to_csv(FORECAST_FILE)
    print(f"\nForecast written to {FORECAST_FILE.name}")
    return forecast_df


def main():
    annual = build_annual_series()
    print("Annual series (levels):")
    print(annual)

    print("\n=== Pre-estimation stationarity & autocorrelation diagnostics ===")
    stationary_df, diff_order = make_stationary(annual)
    print(f"\nDifferencing applied per series: {diff_order}")

    print("\n=== Lag order selection ===")
    lag_order = select_lag_order(stationary_df)

    print(f"\n=== Fitting VAR({lag_order}) on {list(stationary_df.columns)} ===")
    results = fit_var(stationary_df, lag_order)

    post_estimation_diagnostics(results, stationary_df)

    forecast_one_step(results, stationary_df, annual, diff_order, lag_order)


if __name__ == "__main__":
    main()
