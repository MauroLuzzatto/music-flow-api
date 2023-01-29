# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 21:26:29 2019

@author: mauro
"""
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


def main_dummy_data():
    """
    Load dummy data and train a model for testing purpose

    Returns:
        X (TYPE): DESCRIPTION.
        y (TYPE): DESCRIPTION.
        model (TYPE): DESCRIPTION.

    """

    diabetes = load_diabetes()

    X_train, X_val, y_train, y_val = train_test_split(
        diabetes.data, diabetes.target, random_state=0
    )

    X_train = pd.DataFrame(X_train, columns=diabetes.feature_names)
    model = RandomForestRegressor(random_state=0).fit(X_train, y_train)
    # model = XGBRegressor().fit(X_train.values, y_train.values)
    print(model.score(X_val, y_val))
    # df, based on which importance is checked
    X_val = pd.DataFrame(X_val, columns=diabetes.feature_names)

    X = X_val
    y = y_val
    return X, y, model


def create_folder(path):
    """
    create folder, if it doesn't already exist
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def load_pickle(path_model, model_name):
    """


    Args:
        path_model (TYPE): DESCRIPTION.
        name (TYPE): DESCRIPTION.

    Returns:
        estimator (TYPE): DESCRIPTION.

    """
    assert model_name.endswith(".pickle")
    with open(os.path.join(path_model, model_name), "rb") as handle:
        estimator = pickle.load(handle)
    return estimator


def get_dataset(path_load, name, nrows=None, target=None, features=None):
    """
    Load the dataset based on the path and the name of the dataset
    and select the features and target variables

    Args:
        path_load (TYPE): DESCRIPTION.
        name (TYPE): DESCRIPTION.

    Returns:
        X (TYPE): DESCRIPTION.
        y (TYPE): DESCRIPTION.

    """
    if isinstance(target, str):
        target = [target]

    assert name.endswith(".csv"), "ending is wrong or missing"

    if nrows:
        df = pd.read_csv(
            os.path.join(path_load, name), sep=";", nrows=nrows, index_col=0
        )
    else:
        df = pd.read_csv(os.path.join(path_load, name), sep=";", index_col=0)

    if not target:
        target = ["rating"]
    if not features:
        features = list(df)

    y = df[target]
    X = df[[value for value in features if value not in target]]
    print(f"X.shape: {X.shape}")
    print(f"y.shape: {y.shape}")
    return X, y


def map_index_to_sample(df: pd.DataFrame, index: int) -> int:
    """
    get the row of a particular index in a dataframe

    Args:
        index (int): the index number

    Returns:
        int: the sample row number of the index

    """
    return df.index.get_loc(index)


def column_selection(names, columns):
    """
    select the columns that contain any of the value of names

    Args:
        names (TYPE): DESCRIPTION.
        columns (TYPE): DESCRIPTION.

    Returns:
        features (TYPE): DESCRIPTION.

    """
    features = []
    for col in columns:
        if any([name in col for name in names]):
            features.append(col)
    return features


def get_column_selection(targets, features, columns):
    target = column_selection(targets, columns)
    features = column_selection(features, columns)
    return {"target": target, "features": features}


def shuffle_in_unison(a, b, seed=0):
    """
    shuffle two pandas dataframe in parallel

    Args:
        a (TYPE): DESCRIPTION.
        b (TYPE): DESCRIPTION.

    Returns:
        TYPE: DESCRIPTION.
        TYPE: DESCRIPTION.

    """

    assert len(a) == len(b)
    c = np.arange(len(a))

    np.random.seed(seed)
    np.random.shuffle(c)

    return a.iloc[c], b.iloc[c]
