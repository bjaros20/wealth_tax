# Billionaire Tax Act: NPV Distribution (Section 5.4, Figure 3)
# Litigation-risk-weighted approach
# =============================================================================
#   NPV = WT - f*C/(r-g), 100,000 draws:
#   * WT ~ U[$0B, $72B]   wealth tax revenue (0 = Act struck down;
#                         72 = ceiling after confirmed departures)
#   * f ~ U[0.30, 0.60]   fraction of billionaire income tax base that departs
#   * C ~ U[$3.3B, $5.8B] annual billionaire income tax
#   * (r-g) ~ U[1.5%, 4.5%]
# =============================================================================
library(ggplot2)
library(ggthemes)

set.seed(2026)
plot_dir <- "../NPV_plots"

# ---- Parameters ----
n_sims <- 100000
wt_min <- 0;    wt_max <- 72      # wealth-tax revenue ($B), embeds litigation range
f_min  <- 0.30; f_max  <- 0.60    # fraction of income-tax base that departs
c_min  <- 3.3;  c_max  <- 5.8     # annual billionaire income tax ($B)
rg_min <- 0.015; rg_max <- 0.045  # net real discount rate (r - g)

# ---- Draws ----
wt <- runif(n_sims, wt_min, wt_max)
f  <- runif(n_sims, f_min,  f_max)
c_income    <- runif(n_sims, c_min,  c_max)
rg_discount <- runif(n_sims, rg_min, rg_max)

# ---- NPV ----
npv <- wt - (f * c_income) / rg_discount
results <- data.frame(wt, f, c_income, rg_discount, npv)

# ---- Summary ----
cat("=== NPV Distribution Summary ===\n")
cat(sprintf("  Simulations:      %d\n", n_sims))
cat(sprintf("  Mean NPV:         $%.1fB\n", mean(npv)))
cat(sprintf("  Median NPV:       $%.1fB\n", median(npv)))
cat(sprintf("  Std Dev:          $%.1fB\n", sd(npv)))
cat(sprintf("  P5 / P25 / P75 / P95: $%.1f / $%.1f / $%.1f / $%.1fB\n",
            quantile(npv,.05), quantile(npv,.25), quantile(npv,.75), quantile(npv,.95)))
cat(sprintf("  Pct Negative:     %.1f%%\n", 100*mean(npv < 0)))

pct_negative <- round(100 * mean(npv < 0), 1)

# ---- Plot ----
p <- ggplot(results, aes(x = npv)) +
  geom_histogram(aes(fill = npv < 0), bins = 100, alpha = 0.85,
                 color = "white", linewidth = 0.1) +
  scale_fill_manual(
    values = c("TRUE" = "#B3173C", "FALSE" = "#2C5F8A"),
    labels = c("TRUE" = "Negative NPV", "FALSE" = "Positive NPV"),
    name = NULL
  ) +
  geom_vline(xintercept = 0, linetype = "dashed", color = "black", linewidth = 0.7) +
  annotate("text", x = -160, y = Inf, vjust = 2, hjust = 0,
           label = paste0(pct_negative, "% of draws\nyield negative NPV"),
           size = 4.3, fontface = "bold", color = "#B3173C") +
  labs(
    title = "Distribution of Net Present Value: Billionaire Tax Act",
    subtitle = "100,000 draws: WT ~ U[$0B, $72B],  f ~ U[0.30, 0.60],  C ~ U[$3.3B, $5.8B],  (r-g) ~ U[1.5%, 4.5%]",
    x = "Net Present Value ($B)",
    y = "Count"
  ) +
  theme_few() +
  theme(
    plot.title    = element_text(face = "bold", size = 14, margin = margin(b = 14)),
    plot.subtitle = element_text(size = 9.5, color = "gray40", margin = margin(t = 0, b = 16)),
    legend.position = c(0.88, 0.85),
    legend.background = element_rect(fill = "white", color = "gray80"),
    plot.margin = margin(t = 12, r = 12, b = 10, l = 10)
  )

ggsave(file.path(plot_dir, "npv_distribution_v8.png"), p, width = 10, height = 6, dpi = 300)
ggsave(file.path(plot_dir, "npv_distribution_v8.pdf"), p, width = 10, height = 6)
cat("\nSaved npv_distribution_v8.{png,pdf}\n")
