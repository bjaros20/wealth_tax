# Billionaire Tax Act: NPV as a function of the wealth-tax rate (sunk departures)
# Date: June 2026
# Purpose: Second supplemental figure. Conditional on the confirmed departures
#          being permanent, the PV of lost income tax is fixed and only upfront
#          revenue varies with the rate, so NPV rises monotonically in tau.
#          The 2% union offer sits below the break-even rate; 5% is above it.
#          The irony: after triggering the exodus, a LOWER rate is worse.
# =============================================================================
library(ggplot2)
library(ggthemes)

plot_dir <- "../NPV_plots"

base_full <- 94.20 / 0.05   # 1884
f_sunk    <- 0.283
C         <- 4.55           # midpoint income tax

taus <- seq(0, 0.06, by = 0.0005)
grid <- do.call(rbind, lapply(c(0.015, 0.030, 0.045), function(rg) {
  data.frame(tau = taus, rg = rg,
             npv = (1 - f_sunk) * taus * base_full - f_sunk * C / rg)
}))
grid$rg_lab <- factor(sprintf("(r-g) = %.1f%%", 100 * grid$rg))

# Break-even rate at the central 3% discount rate
tau_be <- (f_sunk * C / 0.03) / ((1 - f_sunk) * base_full)

p <- ggplot(grid, aes(tau * 100, npv, color = rg_lab)) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "black") +
  geom_line(linewidth = 1) +
  geom_vline(xintercept = 2, color = "#B3173C", linewidth = 0.6) +
  geom_vline(xintercept = 5, color = "gray40", linewidth = 0.6) +
  annotate("text", x = 2, y = min(grid$npv), label = "2% union offer",
           color = "#B3173C", angle = 90, vjust = -0.4, hjust = 0,
           fontface = "bold", size = 3.4) +
  annotate("text", x = 5, y = min(grid$npv), label = "5% original",
           color = "gray40", angle = 90, vjust = -0.4, hjust = 0,
           fontface = "bold", size = 3.4) +
  scale_color_manual(values = c("#B3173C", "#2C5F8A", "#3C8A5F"), name = NULL) +
  labs(
    title = "After the exodus, a lower wealth-tax rate lowers the NPV",
    subtitle = "Confirmed departures sunk (f = 28.3%); income loss fixed, so NPV rises with the rate. Midpoint income C = $4.55B.",
    x = "Wealth-tax rate (%)", y = "Net present value ($B)"
  ) +
  theme_few() +
  theme(plot.title = element_text(face = "bold", size = 13),
        plot.subtitle = element_text(size = 9.5, color = "gray40"),
        legend.position = "inside",
        legend.position.inside = c(0.15, 0.82),
        legend.background = element_rect(fill = "white", color = "gray80"))

ggsave(file.path(plot_dir, "npv_vs_rate_2pct.png"), p, width = 10, height = 6, dpi = 300)
ggsave(file.path(plot_dir, "npv_vs_rate_2pct.pdf"), p, width = 10, height = 6)

cat(sprintf("Break-even rate at 3%% discount: %.2f%%\n", 100 * tau_be))
cat("Saved npv_vs_rate_2pct.{png,pdf}\n")
