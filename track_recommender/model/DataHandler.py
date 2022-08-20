import os
import pickle
from typing import Tuple

import numpy as np


class DataHandler:
    def __init__(self, path):
        self.path = path

    def save_data(self, X: np.array, y: np.array) -> None:
        """save the features and target values to pickle files

        Args:
            X ([type]): [description]
            y ([type]): [description]
        """
        self.save_pickle(X, "X.pickle")
        self.save_pickle(y, "y.pickle")

    def save_pickle(self, variable, name):

        assert name.endswith(".pickle")

        with open(os.path.join(self.path, name), "wb") as handle:
            pickle.dump(variable, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_pickle(self, name):

        assert name.endswith(".pickle")

        with open(os.path.join(self.path, name), "rb") as handle:
            variable = pickle.load(handle)
        return variable

    def load_data(self) -> Tuple[np.array, np.array]:
        """load  the features and target values from pickle files

        Returns:
            [type]: [description]
        """
        X = self.load_pickle("X.pickle")
        y = self.load_pickle("y.pickle")
        return X, y
