import hashlib
import os

path = os.getcwd()
path_base = os.path.join(path, "track_recommender")

path_data = os.path.join(path, "data")
path_data_lake = os.path.join(path, "data_lake")
path_features = os.path.join(path_data, "features")
path_dataset = os.path.join(path_data, "dataset")
path_results = os.path.join(path, "results")
dotenv_path = os.path.join(path, ".env")


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()
