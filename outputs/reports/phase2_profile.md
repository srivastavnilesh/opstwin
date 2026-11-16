# OpsTwin Phase 2A - Bronze to Silver Defect Ledger

Generated: 2026-11-16T17:33:39.630577+00:00

## Row reconciliation

| Stage | Rows |
|---|---|
| Bronze | 633,243 |
| Duplicates removed | 2,523 |
| Deduped | 630,720 |
| Quarantined (null) | 9,363 |
| Silver (clean) | 621,357 |
| Balances | True |

## Defect resolution

| Defect | Expected rate | Observed in bronze | Remaining in silver |
|---|---|---|---|
| Nulls | 1.500% | 9,404 | 0 |
| Duplicates | 0.400% | 2,523 | 0 |
| Unit drift (F) | 1.000% | 1,552 | 0 |
| Late arrivals | 2.000% | 12,673 | flagged: 12,437 |
| Outliers | 0.200% | n/a | flagged: 4,384 |

## Silver metric ranges

| Metric | Rows | Min | Avg | Max |
|---|---|---|---|---|
| humidity | 155,348 | 23.26 | 55.39 | 423.48 |
| power | 103,525 | -0.18 | 6.71 | 74.39 |
| temperature | 155,334 | 10.54 | 24.18 | 201.72 |
| vibration | 103,624 | 0.19 | 2.01 | 20.85 |
| water | 103,526 | 1.14 | 12.09 | 100.08 |
