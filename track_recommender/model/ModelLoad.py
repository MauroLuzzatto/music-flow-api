# https://www.kaggle.com/code/harupy/scikit-learn-autologging-in-mlflow/notebook

import datetime
import os
import pickle

import pandas as pd  # type: ignore
import sklearn  # type: ignore
from LoggerClass import LoggerClass
from utils import create_folder


class ModelClass(object):
    """
    This class provides the functionality to train a model using
    a random grid search and evaluate the results
    """

    def __init__(
        self,
        estimator: sklearn.base.BaseEstimator,
        X: pd.DataFrame,
        y: pd.DataFrame,
        path_model: str,
        folder: str = None,
    ) -> None:
        """
        Initialize the class and setup the logger and define the paths to save the results to

        Args:
            estimator (sklearn.BaseEstimator): [description]
            X (pd.DataFrame): [description]
            y (pd.DataFrame): [description]
            path_model (str): [description]
            folder (str): add a folder extension in the save folder
        """

        self.X = X.values
        self.y = y.values

        self.column_names = list(X)
        self.path_model = path_model
        self.estimator = estimator
        self.save_name = estimator.__class__.__name__

        self.folder = folder
        self.set_paths()
        Logger = LoggerClass()
        self.logger = Logger(self.path_save, stage="training")

        self.get_train_test_split()

    def set_paths(self):
        """
        Define the neceneeded paths for saving the results
        """
        self.time_stamp = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

        if self.folder:
            folder_name = f"{self.time_stamp} - {self.folder}"
        else:
            folder_name = self.time_stamp

        self.path_model = create_folder(os.path.join(self.path_model, folder_name))
        self.path_save = create_folder(os.path.join(self.path_model, "results"))

    def save_pickle(self) -> None:
        """
        save the estimator into a pickle file

        Returns:
            None: DESCRIPTION.

        """
        name = f"{self.save_name}.pickle"
        with open(os.path.join(self.path_model, name), "wb") as handle:
            pickle.dump(self.final_model, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.logger.info(f"Save: {os.path.join(self.path_model, name)}")

    def save_predictions(self):

        self.df_test = pd.DataFrame(self.X_test, columns=self.column_names)
        self.df_test["predictions"] = self.y_pred
        self.df_test["targets"] = self.y_test
        self.df_test.to_csv(os.path.join(self.path_save, "df_test.csv"), sep=";")

    def load_pickle(self, name: str) -> None:
        """
        Load the estimator from a pickle file

        Args:
            name (str): DESCRIPTION.

        Returns:
            None: DESCRIPTION.

        """
        assert name.endswith(".pickle")

        with open(os.path.join(self.path_model, name), "rb") as handle:
            estimator = pickle.load(handle)

        self.logger.info(f"Load: {os.path.join(self.path_model, name)}")
        return estimator


if __name__ == "__main__":
    pass
