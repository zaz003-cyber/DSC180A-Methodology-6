"""Stage 3: temporal split, fit, evaluate, write metrics.

Two baselines and two models, on purpose.

  baseline_mean         predict the 2011 average for every day
  baseline_persistence  predict yesterday's count (cnt_lag_1)
  ridge                 standardised linear model on the audited features
  hgb                   gradient-boosted trees on the same features

The mean baseline shows what "the distribution moved" costs. Persistence
is the baseline that actually matters: ridge's features are dominated by
lagged demand, so if it cannot beat "yesterday again" it has learned
nothing worth reporting. The booster is there because it fails, and the
reason it fails is the headline result.

Run: python -m src.train
"""
import argparse
import json

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import METRICS, PROCESSED, TARGET, TRAIN_END, VALID_END
from src.features import feature_columns


class PersistenceBaseline(BaseEstimator, RegressorMixin):
    """Predict a single lagged column unchanged. Nothing is fit."""

    def __init__(self, column: str = "cnt_lag_1"):
        self.column = column

    def fit(self, X, y=None):
        if self.column not in X.columns:
            raise ValueError(f"persistence baseline needs column {self.column!r}")
        return self

    def predict(self, X):
        return X[self.column].to_numpy(dtype=float)


MODELS = {
    "baseline_mean": DummyRegressor(strategy="mean"),
    "baseline_persistence": PersistenceBaseline("cnt_lag_1"),
    "ridge": make_pipeline(StandardScaler(), Ridge(alpha=1.0)),
    "hgb": HistGradientBoostingRegressor(random_state=0, max_iter=300),
}


def temporal_split(df: pd.DataFrame):
    """Split by date, never at random. A random split on a time series
    puts tomorrow in train and today in test."""
    train = df[df.dteday <= TRAIN_END]
    valid = df[(df.dteday > TRAIN_END) & (df.dteday <= VALID_END)]
    test = df[df.dteday > VALID_END]
    return train, valid, test


def score_feature_set(df, cols, validation_only=False, target_transform="none"):
    train, valid, test = temporal_split(df)

    results = {
        "n_features": len(cols),
        "features": cols,
        "n_train": len(train),
        "n_valid": len(valid),
        "n_test": len(test),
    }
    partitions = [("valid", valid)]
    if not validation_only:
        partitions.append(("test", test))
    for name, estimator in MODELS.items():
        model = clone(estimator)
        relative = name == "hgb" and target_transform == "log-relative"
        y_train = train[TARGET]
        if relative:
            if (y_train <= 0).any() or (train.cnt_lag_1 <= 0).any():
                raise ValueError("log-relative targets require positive counts and lags")
            y_train = np.log(y_train / train.cnt_lag_1)
        model.fit(train[cols], y_train)

        def predict(part):
            prediction = model.predict(part[cols])
            if relative:
                prediction = part.cnt_lag_1.to_numpy() * np.exp(prediction)
            return prediction

        results[name] = {
            split: {
                "r2": round(float(r2_score(part[TARGET], predict(part))), 4),
                "mae": round(float(mean_absolute_error(part[TARGET], predict(part))), 1),
            }
            for split, part in partitions
        }
    return results


def fit_and_score(validation_only=False, target_transform="none") -> dict:
    df = pd.read_parquet(PROCESSED)
    cols = feature_columns(df)
    results = score_feature_set(df, cols, validation_only, target_transform)
    if not validation_only and target_transform == "none":
        before = [col for col in cols if col != "cnt_median_7"]
        results["before_feature"] = score_feature_set(df, before)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation-only", action="store_true")
    parser.add_argument("--target-transform", choices=["none", "log-relative"], default="none")
    args = parser.parse_args()
    res = fit_and_score(args.validation_only, args.target_transform)
    output = METRICS.with_name("validation.json") if args.validation_only else METRICS
    if args.target_transform != "none":
        suffix = "validation" if args.validation_only else "final"
        output = METRICS.with_name(f"target-transform-{suffix}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "features"}, indent=2))
