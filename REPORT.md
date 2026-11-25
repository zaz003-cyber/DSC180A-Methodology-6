## Results

The forecast is the total number of Capital Bikeshare rides on a given day. Yesterday's count is available at forecast time. The comparison uses the starter's same-day weather fields, so its accuracy assumes weather inputs of comparable quality are available when the forecast is issued. A dispatch forecast made the night before would need a separate evaluation with archived weather forecasts.

All eight rows use the same dates. Reindexing the calendar before constructing lags left 348 training days in 2011, 182 validation days in January through June 2012, and 184 test days in July through December 2012. Each estimator was fit on 2011 only. R² measures performance against the mean of the scored period. Mean absolute error (MAE) is in rides per day. The mean baseline below always predicts the **training** mean.

| Feature set | Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Before | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | hgb | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| After | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | ridge | 0.6645 | 815.5 | 0.5825 | 939.7 |
| After | hgb | 0.2687 | 1256.6 | -0.4210 | 1921.4 |

The added predictor is the median count on calendar days *d*−7 through *d*−1. It summarizes the recent level while limiting the influence of one exceptional day. January 20, 2011 provides a hand check. The seven previous counts sort to 683, 1000, 1204, **1248**, 1406, 1421, and 1650. Changing the target on January 20 and all later dates leaves that day's feature unchanged.

## Headline finding

Ridge with the median reached test R² 0.5825. The untransformed boosted tree fell from 0.2687 on validation to −0.4210 on test, although it still beat the training-mean baseline (−2.1441). Training counts ranged from 431 to 6,043 rides. Test counts ranged from 22 to 8,714, and 104 of 184 days exceeded the entire training range on the high side. The fitted tree's test predictions topped out at 5,678. Once lagged demand exceeds its learned split thresholds, a tree keeps routing those observations to the same leaves. Ridge can continue increasing its prediction with its lag inputs. The median was retained because validation R² rose by 0.0170 for ridge and 0.0502 for the tree. On test it reduced ridge MAE by 7.4 rides, while ridge R² dipped by 0.0008.

## Exercise 4: target transformation

The alternative tree predicts the log of today's count divided by yesterday's. Its prediction is converted to rides by exponentiating and multiplying by yesterday's observed count. For example, a predicted log change of zero means demand will hold steady. This gives the model a baseline that grows with recent demand and asks the trees to estimate a proportional change. Every training pair had positive counts, and the baseline is known one day ahead.

With the median included, validation R² rose from 0.2687 to 0.6095 and MAE fell from 1256.6 to 843.2. Ridge still had a lower validation MAE of 815.5. The feature and transformation were frozen using validation. The starter's original quality test had already read the test partition during setup. It was moved to validation before feature selection. The frozen comparison subsequently used the test partition, and reproduction reran that same specification.

The transformed tree reached test R² 0.5209 and MAE 967.6. This makes proportional changes a defensible target for one-day-ahead forecasting, but the observed MAE gives little reason to deploy it here. The default pipeline continues to report the untransformed target. The separate transformation run retains the ordinary mean, persistence, and ridge comparisons.

## Exercise 5: ridge vs persistence

For routine dispatch I would use yesterday's ridership. It missed by 840.1 rides per day on average during the test period, versus 939.7 for ridge with the median, a saving of 99.6 rides per day by the metric I care about. Ridge had the higher R² (0.5825 versus 0.5099), which means it reduced squared error over those same days. If a small number of very large misses drove operating costs, that would favor evaluating ridge under that cost function. For daily scheduling, average absolute deviation is the stated priority. Persistence wins on that measure and requires only the last observed count.

## Attribution

Claude Code used local Qwen3 4B through Ollama with a 65,536-token context. A 9B download was started and set aside for speed before inference. The Claude Code exercises used the 4B model throughout. OpenAI Codex also assisted.

**Agent contributions**

- Codex wrote the median tests first, added the raw-column classification check, implemented the training comparisons and target transformation, and ran the reproduction checks. Claude Code invoked the feature workflow and wrote the shifted median expression. Its edit introduced an indentation error that the hook caught. Codex corrected the indentation and ran the complete suite.
- Codex prepared the parameterized fault exercise. Qwen made and repaired the three source edits in Claude Code. Their actual hook outputs are recorded in `docs/SEEDED_FAULTS.md`. Codex measured the effect of a raw-data replacement in a disposable checkout. Qwen repeated the replacement using Bash in a separate fixture, with zero edit-hook events. Codex added the checksum check and prepared the results table and report text. The local Claude Agent SDK audit returned no findings across its four checks (leakage, time ordering, baselines, reproducibility). Its original JSON result is in `reports/audit.jsonl`.
- For the peer audit, Claude Code returned the verdict quoted in `docs/AUDIT.md`. Codex reproduced the peer's scores and repeated the ridge comparison on identical dates. I reviewed those checks and agreed with the main conclusion.

**Student decisions**

- I selected the previous seven days' median from the proposed features. Its inputs would all be observed by the forecast date. The validation improvements supported keeping it.
- I chose average daily absolute error as the decision criterion for dispatch and selected persistence. The chronological splits and two baseline definitions came from the starter. The log-relative target was an agent-proposed experiment.
