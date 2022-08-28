# https://www.kaggle.com/code/harupy/scikit-learn-autologging-in-mlflow/notebook

import datetime
import json
import os
import pickle
import random

import matplotlib.pyplot as plt  # type: ignore
import pandas as pd  # type: ignore
import sklearn  # type: ignore
from LoggerClass import LoggerClass
from sklearn.base import is_classifier, is_regressor  # type: ignore
from sklearn.datasets import load_diabetes  # type: ignore
from sklearn.metrics import f1_score  # type: ignore
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    precision_score,
    r2_score,
)
from sklearn.model_selection import RandomizedSearchCV  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from xgboost import XGBRegressor  # type: ignore

from utils import create_folder


class ModelClass(object):
    """
    This class provides the funktionality to train a model using
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

    def get_train_test_split(
        self, test_size: float = 0.2, random_state: float = None
    ) -> None:
        """
        Get the train and test split of the features and target values

        Args:
            test_size (float, optional): [description]. Defaults to 0.2.
            random_state ([type], optional): [description]. Defaults to None.
        """

        if not random_state:
            random_state = random.randint(0, 1000)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, random_state=random_state, test_size=test_size
        )

        self.logger.info(f"self.X: {self.X.shape}")
        self.logger.info(f"self.y: {self.y.shape}")
        self.logger.info(f"self.X_train: {self.X_train.shape}")
        self.logger.info(f"self.y_train: {self.y_train.shape}")
        self.logger.info(f"self.X_test: {self.X_test.shape}")
        self.logger.info(f"self.y_test: {self.y_test.shape}")
        self.logger.info(f"test_size: {test_size}")
        self.logger.info(f"random_state: {test_size}")
        self.logger.info(f"column_names: {self.column_names}")

    def hyperparamter_tuning(
        self, param_distributions: dict, cv_settings: dict
    ) -> None:
        """
        Execute a random grid search using the distribution of hyperparemeter values
        and CV values

        Args:
            param_distributions (dict): dictionary with distribution of values per hyperparameter
            cv_settings (dict): dictionary CV settings
        """
        random_search = self.build_CV_search(param_distributions, cv_settings)
        random_search.fit(self.X_train, self.y_train)
        self.get_CV_results(random_search, sort_by="rank_test_score")

        self.best_estimator = random_search.best_estimator_
        self.best_params = random_search.best_params_

        self.save_parameters(param_distributions, "param_distributions")
        self.save_parameters(cv_settings, "cv_settings")

    def save_parameters(self, variable: dict, name: str) -> None:
        """
        Save dictionary to json using the provided name
        """
        with open(os.path.join(self.path_save, f"{name}.json"), "w") as fp:
            json.dump(variable, fp)

    def build_pipeline(self, estimator=None):
        """
        Build the pipeline for processing the data before model training
        """
        return Pipeline(
            steps=[
                ("scale", StandardScaler(with_mean=True, with_std=True)),
                ("estimator", estimator),
            ]
        )

    def build_CV_search(
        self, param_distributions: dict, param_cv: dict
    ) -> sklearn.model_selection.RandomizedSearchCV:
        """
        Setup the random search cross validation object

        Args:
            param_distributions (dict): [description]
            param_cv (dict): [description]

        Returns:
            sklearn.RandomizedSearchCV: [description]
        """
        random_search = RandomizedSearchCV(
            estimator=self.estimator,
            param_distributions=param_distributions,
            n_iter=param_cv["n_iter"],
            scoring=param_cv["scoring"],
            cv=param_cv["cv"],
            return_train_score=False,
            n_jobs=param_cv["n_jobs"],
            verbose=param_cv["verbose"],
            random_state=param_cv["random_state"],
        )

        return random_search

    def get_CV_results(
        self,
        random_search: sklearn.model_selection.RandomizedSearchCV,
        sort_by: str,
        ascending: bool = True,
        n_rows: int = 1000,
    ) -> None:
        """
        Extract the results from the random search Cross Validation

        Args:
            random_search (sklearn.model_selection.RandomizedSearchCV): DESCRIPTION.
            sort_by (str): DESCRIPTION.
            ascending (bool, optional): DESCRIPTION. Defaults to True.
            n_rows (int, optional): DESCRIPTION. Defaults to 1000.
             (TYPE): DESCRIPTION.

        Returns:
            None: DESCRIPTION.

        """
        df_results = (
            pd.DataFrame(random_search.cv_results_)
            .sort_values(by=sort_by, ascending=ascending)
            .head(n_rows)
        )

        df_results.to_csv(
            os.path.join(self.path_save, "cv_results.csv"),
            index=False,
            sep=";",
            float_format="%.3f",
        )

        self.logger.info(f"Training score: \n{random_search.best_score_:.2f}")
        self.logger.info(f"Best hyperparameters: \n{random_search.best_params_}")

    def full_data_training(self) -> None:
        """
        Train the model on the the full dataset and on the best hyperparameters

        Returns:
            None: DESCRIPTION.

        """
        self.final_model = self.estimator.set_params(**self.best_params)
        self.final_model.fit(self.X, self.y)

    def evaluate(self) -> None:
        """
        Evaluate the model with the best performing hyperparamters,
        use the test set to the metrics for the model

        Returns:
            None: DESCRIPTION.

        """
        self.y_pred = self.best_estimator.predict(self.X_test)

        if is_regressor(self.estimator):
            methods = [
                r2_score,
                mean_absolute_error,
                mean_squared_error,
                mean_absolute_percentage_error,
            ]
        else:
            methods = [accuracy_score, precision_score, f1_score]

        results = {}
        for method in methods:
            score = method(self.y_test, self.y_pred)
            results[method.__name__] = score
            self.logger.info(f"{method.__name__}: {score:.2f}")

        pd.DataFrame(results, index=[self.time_stamp]).to_csv(
            os.path.join(self.path_save, "best_score.csv"),
            float_format="%.2f",
            sep=";",
        )

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

    def visualize(self, image_name: str = "results.png"):
        """
        plot the predictions versus the true values

        Args:
            image_name (str, optional): DESCRIPTION. Defaults to "results.png".

        Returns:
            None.

        """
        fig = plt.figure(figsize=(4, 5))
        # Plot Real vs Predict
        plt.scatter(self.y_pred, self.y_test, alpha=0.5)
        plt.xlabel("y_pred")
        plt.ylabel("y_test")
        plt.show(block=False)
        fig.savefig(os.path.join(self.path_save, image_name))

    def save_config(self, config):
        """
        save the configurations of the dataset

        Args:
            config (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        with open(
            os.path.join(self.path_save, "config.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def train(self, param_distributions, cv_settings, config=None):
        """
        wrapper function to execute the full training process end-to-end,
        including hyperparameter tuning, evaluation, visualization
        and model saving

        Args:
            param_distributions (TYPE): DESCRIPTION.
            cv_settings (TYPE): DESCRIPTION.
            config (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        self.hyperparamter_tuning(param_distributions, cv_settings)
        self.evaluate()
        self.visualize()
        self.full_data_training()
        self.save_pickle()

        if config:
            self.save_config(config)


param_distributions = {
    "learning_rate": [0.001, 0.01, 0.1, 0.25],
    "max_depth": [3, 5, 7],
    "min_child_weight": [1, 3, 5],
    "subsample": [0.5, 0.8, 1.0],
    "colsample_bytree": [0.25, 0.5, 0.7],
    "n_estimators": [100, 200],
    "objective": ["reg:squarederror"],
}

cv_settings = {
    "n_iter": 50,  # total combinations testes
    "scoring": "r2",
    "cv": 3,
    "random_state": 0,
    "n_jobs": -1,
    "verbose": 3,
}

if __name__ == "__main__":

    path_model = r"model"

    diabetes = load_diabetes()
    X = diabetes.data
    y = diabetes.target

    estimator = XGBRegressor()
    config = {"target": list(y)[0], "features": list(X)}
    model = ModelClass(estimator, X, y, path_model)
    model.train(param_distributions, cv_settings, config)
