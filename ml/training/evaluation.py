"""Evaluation Framework — MAE, RMSE, MAPE, R², median AE, residual distribution."""

import math
import statistics
from ml.training.models import EvaluationResult


class ModelEvaluator:
    """Compute evaluation metrics from predictions."""

    def evaluate(self, y_true: list[float],
                 y_pred: list[float]) -> EvaluationResult:
        n = len(y_true)
        if n == 0:
            return EvaluationResult()

        errors = [abs(y_true[i] - y_pred[i]) for i in range(n)]
        squared_errors = [e ** 2 for e in errors]
        pct_errors = [errors[i] / max(abs(y_true[i]), 1) * 100 for i in range(n)]

        mae = sum(errors) / n
        rmse = math.sqrt(sum(squared_errors) / n)
        mape = sum(pct_errors) / n

        # R²
        y_mean = sum(y_true) / n
        ss_res = sum((y_true[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y_true[i] - y_mean) ** 2 for i in range(n))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        med_ae = statistics.median(errors)

        residuals = [y_true[i] - y_pred[i] for i in range(n)]
        sorted_res = sorted(residuals)

        return EvaluationResult(
            mae=round(mae, 2), rmse=round(rmse, 2),
            mape=round(mape, 2), r2=round(r2, 4),
            median_absolute_error=round(med_ae, 2),
            training_rows=0, holdout_rows=n,
            residual_stats={
                "min": round(min(residuals), 2),
                "max": round(max(residuals), 2),
                "p10": round(sorted_res[n // 10], 2) if n >= 10 else 0,
                "p90": round(sorted_res[9 * n // 10], 2) if n >= 10 else 0,
            },
        )
