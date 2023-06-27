import sys

# sys.path.append("/Users/mauroluzzatto/Documents/python_scripts/track-recommender")


print(sys.path)

from music_flow.dataset.read_streams import read_streams
from music_flow.dataset.create_audio_features_dataset import (
    create_audio_features_dataset,
)
from music_flow.dataset.download_audio_features import download_audio_features
from music_flow.dataset.helper.folder_setup import setup_folders
from music_flow.dataset.create_target_values import create_target_values
from music_flow.dataset.create_dataset import create_dataset


def main():
    setup_folders()
    _ = read_streams()
    _ = create_target_values()
    # shall these functions be merge?
    download_audio_features()
    _ = create_audio_features_dataset()
    _ = create_dataset()


if __name__ == "__main__":
    main()
