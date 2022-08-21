# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 17:44:13 2021

@author: maurol
"""
import json
import os

import pandas as pd

path = os.getcwd()


files = []
for folder in os.listdir(path):
    path_folder = os.path.join(path, folder)
    if os.path.isdir(path_folder):
        if "MyData" in os.listdir(path_folder):
            for file in os.listdir(os.path.join(path_folder, "MyData")):
                if "StreamingHistory" in file:
                    files.append(os.path.join(path_folder, "MyData", file))
                    print(files)

full_data = []

for file in files:

    with open(file, mode="r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    full_data.extend(data)
df = pd.DataFrame(full_data)
df.to_csv("streams.csv")

