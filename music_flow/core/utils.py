import hashlib
import os
from typing import Dict

path = os.getcwd()
path_base = os.path.join(path, "music_flow")

path_data = os.path.join(path, "data")
path_data_lake = os.path.join(path, "data_lake")
path_features = os.path.join(path_data, "features")
path_dataset = os.path.join(path_data, "dataset")
path_results = os.path.join(path, "results")
dotenv_path = os.path.join(path, ".env")


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def create_folder(path):
    """
    create folder, if it doesn't already exist
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def map_score_to_emoji(score) -> Dict[str, str]:

    values = [
        (0.3, "😐", "This song needs to grow on me!"),
        (0.5, "🙂", "Nice track!"),
        (1.0, "😃", "Cool track!"),
        (2.0, "😄", "How did I not know this song?"),
        (100.0, "😍", "What a banger!"),
    ]
    emoji = ""
    text = ""
    for (threshold, emoji, text) in values:
        if score < threshold:
            break

    return {"emoji": emoji, "text": text}
