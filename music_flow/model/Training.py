# https://www.kaggle.com/code/harupy/scikit-learn-autologging-in-mlflow/notebook

import datetime
import json
import os
import pickle
from typing import Optional

import matplotlib.pyplot as plt  # type: ignore
import mlflow
import pandas as pd  # type: ignore
import sklearn  # type: ignore
from sklearn.base import is_regressor  # type: ignore
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
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor  # type: ignore

from music_flow.config.core import model_settings
from music_flow.core.features.preprocessing import reverse_prediction
from music_flow.core.utils import create_folder
from music_flow.model.Logger import Logger
from music_flow.model.TrainingData import TrainingData

# enable autologging
mlflow.sklearn.autolog()


class Training(object):
    """
    This class provides the funktionality to train a model using
    a random grid search and evaluate the results
    """

    def __init__(
        self,
        estimator: sklearn.base.BaseEstimator,
        X: pd.DataFrame,
        y: pd.Series,
        model_version: str,
        path_model: str,
        folder: Optional[str] = None,
    ) -> None:
        """
        Initialize the class and setup the logger and define the paths to save the results to

        Args:
            estimator (sklearn.BaseEstimator): [description]
            X (pd.DataFrame): [description]
            y (pd.Series): [description]
            path_model (str): [description]
            folder (str): add a folder extension in the save folder
        """
        self.X = X
        self.y = y
        self.path_model = path_model
        self.estimator = estimator
        self.model_version = model_version
        self.column_names: List[str] = list(X)  # type: ignore

        self.save_name = f"{model_settings.MODEL_NAME}.pickle"
        self.estimator_name = estimator.__class__.__name__
        self.is_regressor = is_regressor(self.estimator)

        self.set_paths(folder)

        data = TrainingData(X, y, self.path_logs)
        data.get_train_test_split()
        self.X_train, self.y_train = data.get_training_data()
        self.X_test, self.y_test = data.get_test_data()
        self.data_version = "0.1.0"

        logger = Logger()
        self.logger = logger(self.path_logs, stage="training")
        self.logger.info(f"column_name: {self.column_names}")

    def set_paths(self, folder):
        """
        Define the neceneeded paths for saving the results
        """
        self.time_stamp = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

        if folder:
            folder_name = f"{self.time_stamp} - {folder}"
        else:
            folder_name = self.time_stamp

        self.path_model = create_folder(os.path.join(self.path_model, folder_name))
        self.path_save = create_folder(os.path.join(self.path_model, "results"))
        self.path_plots = create_folder(os.path.join(self.path_model, "plots"))
        self.path_logs = create_folder(os.path.join(self.path_model, "logs"))

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

        # mlflow.set_tracking_uri("file:///tmp/my_tracking")
        # tracking_uri = mlflow.get_tracking_uri()
        # print("Current tracking uri: {}".format(tracking_uri))

        random_search = self.build_CV_search(param_distributions, cv_settings)

        with mlflow.start_run() as run:
            random_search.fit(self.X_train, self.y_train)

        mlflow_logs = self.get_mlflow_logs(run)
        self.logger.info(f"mlflow_logs: {dict(mlflow_logs)}")

        self.get_CV_results(random_search, sort_by="rank_test_score")

        self.best_estimator = random_search.best_estimator_
        self.best_params = random_search.best_params_

        self.save_json(name="param_distributions.json", data=param_distributions)
        self.save_json(name="cv_settings.json", data=cv_settings)
        self.save_json(name="mlflow_logs.json", data=mlflow_logs)

    @staticmethod
    def get_mlflow_logs(run) -> dict:
        """Get the mlflow logs from the run

        Args:
            run (mlflow.entities.Run): mlflow run object

            Returns:
                dict: dictionary with the mlflow logs
        """
        print(type(run))
        run_id = run.info.run_id
        client = mlflow.tracking.MlflowClient()
        data = client.get_run(run_id).data
        tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
        artifacts = [f.path for f in client.list_artifacts(run_id, "model")]

        mlflow_logs = {
            "run_id": run_id,
            "params": data.params,
            "metrics": data.metrics,
            "tags": tags,
            "artifacts": artifacts,
        }

        return mlflow_logs

    def build_pipeline(self, estimator=None):
        """
        Build the pipeline for processing the data before model training
        """
        # TODO: this pipeline function is currently not used
        return Pipeline(
            steps=[
                ("scale", StandardScaler(with_mean=True, with_std=True)),
                ("estimator", estimator),
            ]
        )

    def build_CV_search(
        self, param_distributions: dict, param_cv: dict
    ) -> sklearn.model_selection.RandomizedSearchCV:  # type: ignore
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
            error_score="raise",  # type: ignore
        )

        return random_search

    def get_CV_results(
        self,
        random_search: sklearn.model_selection.RandomizedSearchCV,  # type: ignore
        sort_by: str,
        ascending: bool = True,
        n_rows: int = 10,
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

    def train_on_all_data(self) -> None:
        """
        Train the model on the the full dataset and on the best hyperparameters

        Returns:
            None: DESCRIPTION.

        """
        self.final_model = self.estimator.set_params(**self.best_params)
        self.final_model.fit(self.X, self.y)  # type: ignore

    def evaluate(self) -> None:
        """
        Evaluate the model with the best performing hyperparamters,
        use the test set to the metrics for the model
        """
        self.y_pred = self.best_estimator.predict(self.X_test)

        if self.is_regressor:
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

        self.score_dict = {}
        for method in methods:
            score = method(self.y_test, self.y_pred)
            self.score_dict[method.__name__] = score
            self.logger.info(f"{method.__name__}: {score:.2f}")

    def save_metadata(self) -> None:
        """
        Save the metadata of the model
        """
        results = {}
        results["timestamp"] = self.time_stamp

        model_metadata = {
            "name": self.save_name,
            "model_version": self.model_version,
            "sklearn_version": sklearn.__version__,
            "estimator_name": self.estimator_name,
            "best_params": self.best_params,
            "score": self.score_dict,
        }
        data_metadata = {"features": self.column_names, "version": self.data_version}
        results["model"] = model_metadata
        results["data"] = data_metadata

        self.save_json(
            name="metadata.json",
            data=results,
            path=self.path_model,
        )

    def save_json(self, name, data: dict, path=None) -> None:
        """
        Save dictionary to json using the provided name
        """
        assert name.endswith(".json"), "name must end with .json"

        if not path:
            path = self.path_save

        full_path = os.path.join(path, name)
        with open(full_path, "w") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)

        self.logger.info(f"Save: {full_path}")

    def save_pickle(self) -> None:
        """
        save the estimator into a pickle file

        Returns:
            None: DESCRIPTION.

        """
        path = os.path.join(self.path_model, self.save_name)
        with open(path, "wb") as handle:
            pickle.dump(self.final_model, handle, protocol=pickle.HIGHEST_PROTOCOL)

        self.logger.info(f"Save: {path}")

    def save_predictions(self):
        self.df_test = pd.DataFrame(self.X_test, columns=self.column_names)
        self.df_test["predictions"] = self.y_pred
        self.df_test["targets"] = self.y_test
        self.df_test.to_csv(os.path.join(self.path_save, "df_test.csv"), sep=";")

    def visualize(self):
        """
        plot the predictions versus the true values

        Args:
            image_name (str, optional): DESCRIPTION. Defaults to "results.png".

        Returns:
            None.

        """
        self.y_pred_reversed = reverse_prediction(self.y_pred)
        self.y_test_reversed = reverse_prediction(self.y_test)

        image_name = "pred_versus_test.png"
        fig = plt.figure(figsize=(4, 5))
        # Plot Real vs Predict
        plt.scatter(self.y_pred_reversed, self.y_test_reversed, alpha=0.5)
        plt.plot(self.y_pred_reversed, self.y_pred_reversed, color="r")
        plt.xlabel("predictions")
        plt.ylabel("test values")
        plt.show(block=False)
        fig.savefig(os.path.join(self.path_plots, image_name))

        image_name = "residuals_versus_predictions.png"
        fig = plt.figure(figsize=(4, 5))
        plt.scatter(
            self.y_pred_reversed, self.y_pred_reversed - self.y_test_reversed, alpha=0.5
        )
        plt.ylabel("residuals")
        plt.xlabel("predictions")
        plt.show(block=False)
        fig.savefig(os.path.join(self.path_plots, image_name))

        image_name = "residuals_histogram.png"
        fig = plt.figure(figsize=(4, 5))
        plt.hist(self.y_pred_reversed - self.y_test_reversed, alpha=0.5)
        plt.ylabel("residuals")
        plt.show(block=False)
        fig.savefig(os.path.join(self.path_plots, image_name))

    def train(self, param_distributions, cv_settings, config=None, save=False):
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
        self.save_metadata()
        self.visualize()
        self.train_on_all_data()
        self.save_pickle()

        if save:
            self.save_predictions()

        if config:
            self.save_json(name="config.json", data=config)


if __name__ == "__main__":
    path_model = r"model"
    model_version = "0.0.1"

    diabetes = load_diabetes()
    X = diabetes.data  # type: ignore
    y = diabetes.target  # type: ignore

    estimator = XGBRegressor()
    config = {"target": list(y)[0], "features": list(X)}
    trainer = Training(estimator, X, y, model_version, path_model)
    # model.train(param_distributions, cv_settings, config)
