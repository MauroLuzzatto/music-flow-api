import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))

print(parent_dir_path)
sys.path.insert(0, parent_dir_path)

path = os.getcwd()
path_data = os.path.join(path, "data")
path_features = os.path.join(path_data, "features")


print(path_features)
