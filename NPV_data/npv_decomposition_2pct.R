# Billionaire Tax Act: NPV Decomposition -- 5% vs 2%, sunk departures
# Date: June 2026
# Purpose: Convey the central intuition of the 2% supplement: once the
#          confirmed departures are sunk, the present value of permanently lost
#          income tax is IDENTICAL across rates, while the upfront wealth-tax
#          revenue collapses. Lowering the rate forfeits collections without
#          recovering any of the permanent loss.
# =============================================================================
library(ggplot2)
library(ggthemes)

plot_dir <- "../NPV_plots"

# Central scenario: departures sunk at the paper's preferred fraction (55.4%),
# midpoint income, 3% real rate. This reproduces the paper's published central
# 5% NPV of -$42.0B, so BOTH rates show a negative NPV and 2% is simply worse.
base_full <- 94.20 / 0.05   # 1884
f_sunk    <- 0.554          # central/preferred departure fraction
C         <- 4.55           # midpoint annual billionaire income tax ($B)
rg        <- 0.03           # central real discount rate (r - g)

pv_lost <- f_sunk * C / rg                       # identical across rates
wt_5    <- (1 - f_sunk) * 0.05 * base_full        # 42.0
wt_2    <- (1 - f_sunk) * 0.02 * base_full        # 16.8

df <- data.frame(
  rate      = factor(rep(c("5% rate", "2% rate (union offer)"),
                         each = 3),
                     levels = c("5% rate", "2% rate (union offer)")),
  component = factor(rep(c("Upfront wealth-tax\nrevenue",
                           "PV of permanently\nlost income tax",
                           "Net present value"), 2),
                     levels = c("Upfront wealth-tax\nrevenue",
                                "PV of permanently\nlost income tax",
                                "Net present value")),
  value     = c(wt_5, -pv_lost, wt_5 - pv_lost,
                wt_2, -pv_lost, wt_2 - pv_lost)
)

cols <- c("Upfront wealth-tax\nrevenue"   = "#2C5F8A",
          "PV of permanently\nlost income tax" = "#B3173C",
          "Net present value"             = "#6B6B6B")

p <- ggplot(df, aes(x = component, y = value, fill = component)) +
  geom_col(width = 0.65, alpha = 0.9) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("%+.1f", value),
                vjust = ifelse(value >= 0, -0.4, 1.3)),
            fontface = "bold", size = 3.6) +
  facet_wrap(~ rate) +
  scale_fill_manual(values = cols, guide = "none") +
  labs(
    title = "Once the base has fled, a lower rate forfeits revenue for the same loss",
    subtitle = "Central scenario, departures sunk (f = 55.4%); midpoint income C = $4.55B; (r-g) = 3%. Both rates negative; 2% is worse.",
    x = NULL, y = "Present value ($B)"
  ) +
  theme_few() +
  theme(plot.title = element_text(face = "bold", size = 13),
        plot.subtitle = element_text(size = 9.5, color = "gray40"),
        axis.text.x = element_text(size = 8),
        strip.text = element_text(face = "bold", size = 11))

ggsave(file.path(plot_dir, "npv_decomposition_2pct.png"), p, width = 10, height = 6, dpi = 300)
ggsave(file.path(plot_dir, "npv_decomposition_2pct.pdf"), p, width = 10, height = 6)

cat(sprintf("PV lost income tax (both rates): $%.1fB\n", pv_lost))
cat(sprintf("5%% : WT $%.1fB  ->  NPV %+.1fB\n", wt_5, wt_5 - pv_lost))
cat(sprintf("2%% : WT $%.1fB  ->  NPV %+.1fB\n", wt_2, wt_2 - pv_lost))
cat("Saved npv_decomposition_2pct.{png,pdf}\n")
