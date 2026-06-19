# Billionaire Tax Act: NPV Distribution -- 2% RATE, SUNK-DEPARTURE FRAMING
# Date: June 2026
# Purpose: Supplement analysis. Re-estimate the NPV distribution under a 2%
#          one-time wealth tax (the union counter-proposal).
#
#          Key modeling choice: the 6 publicly confirmed departures (28.3% of
#          the base) have already physically left. Their lost income tax is
#          therefore PERMANENT and independent of the rate now levied. Because
#          the rate-induced response at 2% (<=25% under every elasticity in the
#          main paper) is fully contained within the 28.3% already gone, the
#          departure fraction is pinned at the sunk floor f = 28.3%, and the
#          stayers simply pay 2%.
# =============================================================================
library(ggplot2)
library(ggthemes)

set.seed(2026)
plot_dir <- "../NPV_plots"

# ---- Fixed parameters ----
base_full   <- 94.20 / 0.05      # 1884.0  full no-behavioral base ($B)
tau2        <- 0.02
baseline2   <- tau2 * base_full  # 37.68   2% no-behavioral baseline

# Sunk departure fraction is UNCERTAIN: the 6 confirmed (28.3%) are a lower
# bound; we do not know how many left quietly. We keep the same departure-
# fraction range the main paper used (28.3%-62.8%, i.e. its WT ~ U[$35,$67.5B]),
# but here those departures are already gone and the stayers pay only 2%.
f_min <- 0.283   # confirmed floor (best case for the tax)
f_max <- 0.628   # aggressive (paper's $35B end), all already departed

# Income tax + discount rate ranges (unchanged from the main 5% analysis)
c_min <- 3.3; c_max <- 5.8
r_min <- 0.015; r_max <- 0.045

n_sims <- 100000

# ---- Monte Carlo: vary the sunk departure fraction, income, and discount ----
f          <- runif(n_sims, f_min, f_max)
c_income   <- runif(n_sims, c_min, c_max)
r_discount <- runif(n_sims, r_min, r_max)

wt      <- (1 - f) * baseline2               # stayers' base x 2%
pv_lost <- f * c_income / r_discount         # PV of permanently lost income tax
npv     <- wt - pv_lost

results <- data.frame(f, c_income, r_discount, wt, pv_lost, npv)

cat("=== 2% NPV Distribution (sunk-departure framing, f uncertain) ===\n")
cat(sprintf("  Revenue range:          $%.1fB to $%.1fB\n", min(wt), max(wt)))
cat(sprintf("  Departure fraction:     %.1f%%-%.1f%% (sunk; 6 confirmed = floor)\n", 100*f_min, 100*f_max))
cat(sprintf("  Mean NPV:               $%.1fB\n", mean(npv)))
cat(sprintf("  Median NPV:             $%.1fB\n", median(npv)))
cat(sprintf("  Std Dev:                $%.1fB\n", sd(npv)))
cat(sprintf("  P5 / P95:               $%.1fB / $%.1fB\n", quantile(npv,.05), quantile(npv,.95)))
cat(sprintf("  Pct Negative NPV:       %.1f%%\n", 100*mean(npv < 0)))

pct_negative <- round(100 * mean(npv < 0), 1)

p <- ggplot(results, aes(x = npv)) +
  geom_histogram(aes(fill = npv < 0), bins = 80, alpha = 0.85,
                 color = "white", linewidth = 0.1) +
  scale_fill_manual(
    values = c("TRUE" = "#B3173C", "FALSE" = "#2C5F8A"),
    labels = c("TRUE" = "Negative NPV", "FALSE" = "Positive NPV"),
    name = NULL
  ) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "black", linewidth = 0.7) +
  annotate("text", x = -150, y = 3000, hjust = 0,
           label = paste0(pct_negative, "% of draws\nyield negative NPV"),
           size = 4.5, fontface = "bold", color = "#B3173C") +
  labs(
    title = "Distribution of Net Present Value: 2% Billionaire Tax",
    subtitle = "Departures sunk, f ~ U[28.3%, 62.8%]; WT $14-27B; C ~ U[$3.3B, $5.8B], r ~ U[1.5%, 4.5%]",
    x = "Net Present Value ($B)", y = "Count"
  ) +
  theme_few() +
  theme(plot.title = element_text(face = "bold", size = 14),
        plot.subtitle = element_text(size = 10, color = "gray40"),
        legend.position = "inside",
        legend.position.inside = c(0.16, 0.90),
        legend.background = element_rect(fill = "white", color = "gray80"))

ggsave(file.path(plot_dir, "npv_distribution_2pct_sunk.png"), p, width = 10, height = 6, dpi = 300)
ggsave(file.path(plot_dir, "npv_distribution_2pct_sunk.pdf"), p, width = 10, height = 6)
cat("\nSaved npv_distribution_2pct_sunk.{png,pdf}\n")
