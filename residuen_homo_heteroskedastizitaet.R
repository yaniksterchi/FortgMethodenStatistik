# =============================================================================
# Model diagnostics: homoscedasticity vs. heteroscedasticity
# Simulated data, linear regression, diagnostic scatterplots (tidyverse)
# =============================================================================

library(tidyverse)
library(broom)   # augment(): fitted values & residuals as a tibble

set.seed(2026)
n <- 200

# --- 1. Simulate data --------------------------------------------------------
# Same true relationship (y = 2 + 1.5x) in both scenarios, only the error
# variance differs:
#   homoscedastic:   sd = 2 (constant)
#   heteroscedastic: sd grows with x (funnel shape)

sim <- tibble(x = runif(n, 0, 10)) |>
  mutate(
    homo   = 2 + 1.5 * x + rnorm(n, sd = 2),
    hetero = 2 + 1.5 * x + rnorm(n, sd = 0.3 + 0.6 * x)
  ) |>
  pivot_longer(c(homo, hetero), names_to = "szenario", values_to = "y") |>
  mutate(szenario = factor(
    szenario,
    levels = c("homo", "hetero"),
    labels = c("Homoskedastizität", "Heteroskedastizität")
  ))

# --- 2. Fit one model per scenario, extract residuals -----------------------

diag <- sim |>
  nest(data = -szenario) |>
  mutate(
    fit = map(data, \(d) lm(y ~ x, data = d)),
    aug = map(fit, augment)
  ) |>
  select(szenario, aug) |>
  unnest(aug)

# Common look
theme_set(theme_minimal(base_size = 13) +
            theme(strip.text = element_text(face = "bold", size = 13),
                  panel.grid.minor = element_blank()))
col_pts    <- "grey30"
col_line   <- "#2166AC"
col_smooth <- "#D6604D"

# --- 3. Plot A: Raw data with regression line -------------------------------

p_data <- ggplot(sim, aes(x, y)) +
  geom_point(alpha = 0.55, colour = col_pts) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE,
              colour = col_line, linewidth = 1) +
  facet_wrap(~ szenario) +
  labs(title = "Daten mit Regressionsgerade",
       x = "x", y = "y")

# --- 4. Plot B: Residuals vs. fitted values ---------------------------------
# Homoscedastic: even band around 0. Heteroscedastic: funnel.

p_resid <- ggplot(diag, aes(.fitted, .resid)) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey50") +
  geom_point(alpha = 0.55, colour = col_pts) +
  geom_smooth(method = "loess", formula = y ~ x, se = FALSE,
              colour = col_smooth, linewidth = 1) +
  facet_wrap(~ szenario) +
  labs(title = "Residuen vs. angepasste Werte",
       x = "Angepasste Werte (ŷ)", y = "Residuen (e)")

# --- 5. Plot C: Scale-location plot -----------------------------------------
# sqrt(|standardised residuals|) vs. fitted values.
# Flat smoother = constant variance; rising smoother = heteroscedasticity.

p_scale <- ggplot(diag, aes(.fitted, sqrt(abs(.std.resid)))) +
  geom_point(alpha = 0.55, colour = col_pts) +
  geom_smooth(method = "loess", formula = y ~ x, se = FALSE,
              colour = col_smooth, linewidth = 1) +
  facet_wrap(~ szenario) +
  labs(title = "Scale-Location-Plot",
       x = "Angepasste Werte (ŷ)",
       y = expression(sqrt("|standardisierte Residuen|")))

# --- 6. Plot D: Residuals vs. x with ±2 SD envelope ------------------------
# Local spread (rolling SD over 10 x-bins) makes the changing variance visible.

envelope <- diag |>
  mutate(bin = cut_interval(x, 10)) |>
  group_by(szenario, bin) |>
  summarise(x_mid = mean(x), sd_res = sd(.resid), .groups = "drop")

p_env <- ggplot(diag, aes(x, .resid)) +
  geom_ribbon(data = envelope,
              aes(x = x_mid, ymin = -2 * sd_res, ymax = 2 * sd_res),
              inherit.aes = FALSE, fill = col_line, alpha = 0.15) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey50") +
  geom_point(alpha = 0.55, colour = col_pts) +
  facet_wrap(~ szenario) +
  labs(title = "Residuen vs. x mit ±2 SD-Band (lokal geschätzt)",
       x = "x", y = "Residuen (e)")

# --- 7. Show / save ---------------------------------------------------------

p_data
p_resid
p_scale
p_env

# Optional: save for slides
# ggsave("resid_vs_fitted.png", p_resid, width = 10, height = 4.5, dpi = 300)
# ggsave("scale_location.png",  p_scale, width = 10, height = 4.5, dpi = 300)

# Optional: formal test (Breusch-Pagan), package lmtest
# sim |>
#   nest(data = -szenario) |>
#   mutate(bp = map(data, \(d) lmtest::bptest(lm(y ~ x, data = d))),
#          bp = map(bp, tidy)) |>
#   unnest(bp) |>
#   select(szenario, statistic, p.value)
