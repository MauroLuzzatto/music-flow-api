import random
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split  # type: ignore

from music_flow.model.Logger import Logger


class TrainingData:
    def __init__(self, X: pd.DataFrame, y: pd.Series, path_log) -> None:
        self.X = X.values
        self.y = y.values

        logger = Logger()
        self.logger = logger(path_log, stage="data")

        self.X_train: np.ndarray
        self.X_test: np.ndarray
        self.y_train: np.ndarray
        self.y_test: np.ndarray

    def get_train_test_split(
        self, test_size: float = 0.2, random_state: Optional[float] = None
    ) -> None:
        """
        Get the train and test split of the features and target values

        Args:
            test_size (float, optional): [description]. Defaults to 0.2.
            random_state ([type], optional): [description]. Defaults to None.
        """

        if not random_state:
            random_state = random.randint(0, 1000)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(  # type: ignore
            self.X,
            self.y,
            random_state=random_state,
            test_size=test_size,
        )

        # rewrite logger statements into a dict
        self.data_log = {
            "self.X": self.X.shape,
            "self.y": self.y.shape,
            "self.X_train": self.X_train.shape,  # type: ignore
            "self.y_train": self.y_train.shape,  # type: ignore
            "self.X_test": self.X_test.shape,  # type: ignore
            "self.y_test": self.y_test.shape,  # type: ignore
            "test_size": test_size,
            "random_state": random_state,
        }

        self.logger.info(f"data_log: {self.data_log}")

    def get_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        return self.X_train, self.y_train

    def get_test_data(self) -> Tuple[np.ndarray, np.ndarray]:
        return self.X_test, self.y_test
