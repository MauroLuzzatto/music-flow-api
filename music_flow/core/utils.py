import hashlib
import os
from typing import Dict


def create_folder(path):
    """
    create folder, if it doesn't already exist
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


path = os.getcwd()
path_base = os.path.join(path, "music_flow")

path_data_lake = create_folder(os.path.join(path, "data_lake"))

path_data = create_folder(os.path.join(path, "data"))
path_features = create_folder(os.path.join(path_data, "features"))
path_dataset = create_folder(os.path.join(path_data, "dataset"))

path_reports = os.path.join(path, "reports")
path_results = create_folder(os.path.join(path, "results"))
path_env = os.path.join(path, ".env")


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


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
    for threshold, emoji, text in values:
        if score < threshold:
            break

    return {"emoji": emoji, "text": text}
