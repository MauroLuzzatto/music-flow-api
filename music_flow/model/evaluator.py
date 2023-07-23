import matplotlib.pyplot as plt  # type: ignore
import os
from sklearn.metrics import f1_score  # type: ignore
from sklearn.metrics import (
    accuracy_score,  # type: ignore
    mean_absolute_error,  # type: ignore
    mean_absolute_percentage_error,  # type: ignore
    mean_squared_error,  # type: ignore
    precision_score,  # type: ignore
    r2_score,  # type: ignore
)

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Evaluator:
    def __init__(self, y_test: np.ndarray, y_pred: np.ndarray):
        self.y_test = y_test
        self.y_pred = y_pred

    def evaluate(self, is_regressor: bool = True) -> dict[str | float]:
        """
        Evaluate the model with the best performing hyperparamters,
        use the test set to the metrics for the model
        """
        if is_regressor:
            methods = [
                r2_score,
                mean_absolute_error,
                mean_squared_error,
                mean_absolute_percentage_error,
            ]
        else:
            methods = [
                accuracy_score,
                precision_score,
                f1_score,
            ]
        score_dict = {}
        for method in methods:
            score = method(self.y_test, self.y_pred)
            score_dict[method.__name__] = score
            logger.info(f"{method.__name__}: {score:.2f}")
        return score_dict

    def visualize(self, path_save: Optional[str] = None):
        """
        plot the predictions versus the true values

        Args:
            path_save (str, optional):..

        Returns:
            None.
        """
        residuals = self.y_pred - self.y_test

        image_name = "pred_versus_test.png"
        fig = plt.figure(figsize=(4, 5))
        # Plot Real vs Predict
        plt.scatter(self.y_pred, self.y_test, alpha=0.5)
        plt.plot(self.y_pred, self.y_pred, color="r")
        plt.xlabel("predictions")
        plt.ylabel("test values")
        plt.show(block=False)
        plt.tight_layout()

        if path_save:
            fig.savefig(os.path.join(path_save, image_name))

        image_name = "residuals_versus_predictions.png"
        fig = plt.figure(figsize=(4, 5))
        plt.scatter(self.y_pred, residuals, alpha=0.5)
        plt.ylabel("residuals")
        plt.xlabel("predictions")
        plt.show(block=False)
        plt.tight_layout()

        if path_save:
            fig.savefig(os.path.join(path_save, image_name))

        image_name = "residuals_histogram.png"
        fig = plt.figure(figsize=(4, 5))
        plt.hist(residuals, alpha=0.5)
        plt.ylabel("residuals")
        plt.show(block=False)
        plt.tight_layout()
        if path_save:
            fig.savefig(os.path.join(path_save, image_name))
