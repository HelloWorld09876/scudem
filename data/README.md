# Data provenance

`raw/statage.csv` and `raw/wtage.csv` hold the CDC 2000 growth reference LMS parameters
(stature-for-age, 24–240 months; weight-for-age, 0–240 months).

Columns: `sex` (1 = male, 2 = female), `agemos` (age in months), `L`, `M`, `S`.
The value at z-score `z` is `M·(1 + L·S·z)^(1/L)`, so `z = 0` is the median and `z = ±1.2816` are the 10th/90th centiles.

Source: CDC National Center for Health Statistics, 2000 CDC Growth Charts, percentile data files
(https://www.cdc.gov/growthcharts/percentile_data_files.htm). The values were extracted from the
open-source AnthStat project (github.com/erik1066/anthstat-statistics, `src/CDC2000.data.cs`), which reproduces the CDC files.
Spot check: male stature median at 24.0 months is 86.452 cm, matching the CDC table.

Reference: Kuczmarski RJ et al. (2002). 2000 CDC Growth Charts for the United States: Methods and Development.
Vital Health Stat 11(246).
