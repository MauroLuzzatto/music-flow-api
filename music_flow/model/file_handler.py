import os
import logging
import json
from typing import Optional


def save_json(name: str, data: dict, path: Optional[str] = None) -> None:
    """
    Save dictionary to json using the provided name
    """
    assert name.endswith(".json"), "name must end with .json"

    full_path = os.path.join(path, name) if path else name
    with open(full_path, "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)

    logging.info(f"Save: {full_path}")
