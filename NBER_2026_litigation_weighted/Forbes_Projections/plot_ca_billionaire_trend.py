"""
Plot the historical CA-billionaire total wealth trend (1996-2026, where 2026
comes from CA Billionaires Assets.csv's net_worth_usd column -- see
var_model_ca_billionaires.py) alongside two different 2027 forecasts:
  1. The VAR point forecast from var_model_ca_billionaires.py.
  2. A flat 7% growth projection, taken from the pre-computed
     sum_net_worth_usd_7%_growth total in "CA Billionaires Assets.csv"
     (trailing totals row, located by matching the "sum_net_worth_usd"
     label rather than a hardcoded row number).
And a third plot showing both forecasts together for comparison.

Reads:
  - CA_Billionaires_VAR_Annual_Series.csv (historical annual levels, 1996-2026)
  - CA_Billionaires_VAR_Forecast.csv      (VAR 2027 point forecast + 95% CI)
  - CA Billionaires Assets.csv            (precomputed
                                            sum_net_worth_usd_7%_growth total)
Writes:
  - CA_Billionaires_VAR_Trend_Forecast.png
  - CA_Billionaires_7pct_Trend_Forecast.png
  - CA_Billionaires_VAR_vs_7pct_Trend_Forecast.png

Note: both forecasts share the same 2026 base -- CA Billionaires Assets.csv's
net_worth_usd total (212 people, last-ranked David Sacks, $1,894.8B) -- so
they land close together. They can still differ because the VAR extrapolates
the 1996-2026 trend's own dynamics, while the 7% figure is a flat assumed
growth rate applied to the same base.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
ANNUAL_FILE = BASE_DIR / "CA_Billionaires_VAR_Annual_Series.csv"
FORECAST_FILE = BASE_DIR / "CA_Billionaires_VAR_Forecast.csv"
ASSETS_FILE = BASE_DIR / "CA Billionaires Assets.csv"

VAR_OUTPUT_FILE = BASE_DIR / "CA_Billionaires_VAR_Trend_Forecast.png"
GROWTH_OUTPUT_FILE = BASE_DIR / "CA_Billionaires_7pct_Trend_Forecast.png"
COMBINED_OUTPUT_FILE = BASE_DIR / "CA_Billionaires_VAR_vs_7pct_Trend_Forecast.png"

HISTORY_COLOR = "#2C6E9E"
VAR_COLOR = "#D9713C"
GROWTH_COLOR = "#4C9F70"

COL = "total_wealth"
YLABEL = "Total Wealth ($B)"


def load_history() -> pd.Series:
    annual = pd.read_csv(ANNUAL_FILE, index_col="Year")
    return annual[COL]


def load_var_forecast() -> tuple[int, float, float, float]:
    forecast = pd.read_csv(FORECAST_FILE, index_col="Year")
    year = forecast.index[0]
    return (year, forecast.loc[year, f"{COL}_point"],
            forecast.loc[year, f"{COL}_lower"], forecast.loc[year, f"{COL}_upper"])


def load_growth_forecast() -> float:
    """Read CA Billionaires Assets.csv's precomputed sum_net_worth_usd_7%_growth
    total, located by matching the "sum_net_worth_usd" label rather than a
    fixed row."""
    raw = pd.read_csv(ASSETS_FILE)
    label_idx = raw.index[raw["net_worth_usd"] == "sum_net_worth_usd"][0]
    total_row = raw.loc[label_idx + 1]
    total_usd = float(total_row["net_worth_usd_7%_growth"])
    return total_usd / 1e9  # convert to $B to match the Forbes-based series


def style_axis(ax):
    ax.set_xlabel("Year")
    ax.set_ylabel(YLABEL)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, loc="upper left")


def plot_var_forecast(history: pd.Series):
    year, point, lower, upper = load_var_forecast()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(history.index, history.values, marker="o", markersize=4,
            color=HISTORY_COLOR, linewidth=1.75, label="Historical")
    ax.plot([history.index[-1], year], [history.iloc[-1], point],
            linestyle="--", color=VAR_COLOR, linewidth=1.5)
    ax.errorbar([year], [point], yerr=[[point - lower], [upper - point]],
                fmt="o", color=VAR_COLOR, markersize=7, capsize=5,
                linewidth=1.5, label=f"{year} VAR forecast (95% CI)")

    ax.set_title("Total Forbes wealth of CA billionaires", fontsize=11, loc="left")
    style_axis(ax)
    fig.suptitle("CA Billionaires: Forbes Wealth Trend & 1-Year-Ahead VAR Forecast",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(VAR_OUTPUT_FILE, dpi=150)
    print(f"Saved plot to {VAR_OUTPUT_FILE.name}")


def plot_growth_forecast(history: pd.Series):
    year, _, _, _ = load_var_forecast()  # reuse the same target year
    growth_point = load_growth_forecast()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(history.index, history.values, marker="o", markersize=4,
            color=HISTORY_COLOR, linewidth=1.75, label="Historical")
    ax.plot([history.index[-1], year], [history.iloc[-1], growth_point],
            linestyle="--", color=GROWTH_COLOR, linewidth=1.5)
    ax.plot([year], [growth_point], marker="o", color=GROWTH_COLOR, markersize=7,
            label=f"{year} 7% growth estimate")

    ax.set_title("Total Forbes wealth of CA billionaires", fontsize=11, loc="left")
    style_axis(ax)
    fig.suptitle("CA Billionaires: Wealth Trend & 7% Growth Forecast",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(GROWTH_OUTPUT_FILE, dpi=150)
    print(f"Saved plot to {GROWTH_OUTPUT_FILE.name}")


def plot_combined_forecast(history: pd.Series):
    year, var_point, var_lower, var_upper = load_var_forecast()
    growth_point = load_growth_forecast()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(history.index, history.values, marker="o", markersize=4,
            color=HISTORY_COLOR, linewidth=1.75, label="Historical")

    # Small x-offsets so the two forecasts for the same year don't overlap.
    var_x, growth_x = year - 0.12, year + 0.12

    ax.plot([history.index[-1], var_x], [history.iloc[-1], var_point],
            linestyle="--", color=VAR_COLOR, linewidth=1.5)
    ax.errorbar([var_x], [var_point], yerr=[[var_point - var_lower], [var_upper - var_point]],
                fmt="o", color=VAR_COLOR, markersize=7, capsize=5,
                linewidth=1.5, label=f"{year} VAR forecast (95% CI)")

    ax.plot([history.index[-1], growth_x], [history.iloc[-1], growth_point],
            linestyle="--", color=GROWTH_COLOR, linewidth=1.5)
    ax.plot([growth_x], [growth_point], marker="o", color=GROWTH_COLOR, markersize=7,
            label=f"{year} 7% growth estimate")

    ax.set_title("Total Forbes wealth of CA billionaires", fontsize=11, loc="left")
    style_axis(ax)
    fig.suptitle("CA Billionaires: Wealth Trend, VAR Forecast vs. 7% Growth Estimate",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(COMBINED_OUTPUT_FILE, dpi=150)
    print(f"Saved plot to {COMBINED_OUTPUT_FILE.name}")


def main():
    history = load_history()
    plot_var_forecast(history)
    plot_growth_forecast(history)
    plot_combined_forecast(history)


if __name__ == "__main__":
    main()
