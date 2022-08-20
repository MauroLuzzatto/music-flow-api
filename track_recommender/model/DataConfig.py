# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 17:25:59 2021

@author: maurol
"""
import json
import os

import pandas as pd
from model.config import path_base
from model.utils import get_column_selection


class DataConfig(object):
    def __init__(self, path_config):
        self.path_config = path_config

    def create_data_config(self, path_load, dataset_name):
        """
        generate the data configuration dictionary
        """
        exclude_list = ["FirstName", "LastName", "Email"]
        print(os.path.join(path_load, dataset_name))
        df = pd.read_csv(
            os.path.join(path_load, dataset_name),
            sep=";",
            encoding="utf-8-sig",
            index_col=0,
        )
        columns = list(df)

        data_config = {}
        data_config["dataset"] = dataset_name

        targets_all = (
            ["academic.player"] + ["essay.player"] + ["extracurricular.player"]
        )
        features_all = [
            col for col in columns if "player" not in col and col not in exclude_list
        ]
        print([col for col in columns if "player" in col])

        data_config["all"] = get_column_selection(targets_all, features_all, columns)
        return data_config

    def load_config(self):
        with open(
            os.path.join(self.path_config, "data_config.json"),
            "r",
            encoding="utf-8",
        ) as f:
            data_config = json.load(f)
        return data_config

    def save_config(self, data_config):
        with open(
            os.path.join(self.path_config, "data_config.json"),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(data_config, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    path_load = os.path.join(path_base, "dataset", "training")
    path_config = os.path.join(path_base, "src", "resources")
    dataset_name = r"applications-website-up-to-20April-clean.csv_postprocessed.csv"

    data = DataConfig(path_config)
    data_config = data.create_data_config(path_load, dataset_name)
