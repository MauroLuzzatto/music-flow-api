import hashlib
import json
import os


def create_folder(path):
    """
    create folder, if it doesn't already exist
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


path = os.getcwd()
path_base = os.path.join(path, "music_flow")

path_data_lake = create_folder(os.path.join(path, "data_lake"))

path_data = create_folder(os.path.join(path, "data"))
path_features = create_folder(os.path.join(path_data, "features"))
path_dataset = create_folder(os.path.join(path_data, "dataset"))

path_reports = os.path.join(path, "reports")
path_results = create_folder(os.path.join(path, "results"))
path_env = os.path.join(path, ".env")
