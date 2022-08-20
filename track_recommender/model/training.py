# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 20:35:34 2021

@author: maurol
"""

import os
import sys

from xgboost import XGBRegressor  # type: ignore

sys.path.insert(
    0,
    r"C:\Users\maurol\OneDrive\Dokumente\Python_Scripts\algorithmic-explanations",
)

from src.model.config import path_base
from src.model.DataConfig import DataConfig
from src.model.ModelClass import ModelClass, cv_settings, param_distributions
from src.model.utils import get_dataset, setup_dataset

path_load = os.path.join(path_base, "dataset", "training")
path_model = os.path.join(path_base, "model")
path_config = os.path.join(path_base, "src", "resources")

# dataset_name = r"applications-website-up-to-20April-clean.csv_postprocessed.csv"
dataset_name = r"All-applications-clean_full_data.csv_postprocessed.csv"


data = DataConfig(path_config)
data_config = data.create_data_config(path_load, dataset_name)
data.save_config(data_config)


for field in ["all"]:
    print(field)

    config = data_config[field]

    if not config["target"]:
        continue

    X, y = get_dataset(
        path_load=path_load,
        name=data_config["dataset"],
        target=config["target"],
        features=config["features"],
    )

    X, y = setup_dataset(field, X, y)

    # train model
    estimator = XGBRegressor()
    model = ModelClass(estimator, X, y, path_model, folder=field)
    model.train(param_distributions, cv_settings, config)
