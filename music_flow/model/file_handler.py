import os
import logging
import json


def save_json(name: str, data: dict, path: str = None) -> None:
    """
    Save dictionary to json using the provided name
    """
    assert name.endswith(".json"), "name must end with .json"
    if path:
        full_path = os.path.join(path, name)
    else:
        full_path = name

    with open(full_path, "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

    logging.info(f"Save: {full_path}")
