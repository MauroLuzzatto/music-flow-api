from music_flow.dataset.create_audio_features_dataset import (
    create_audio_features_dataset,
)
from music_flow.dataset.create_dataset import create_dataset
from music_flow.dataset.create_target_values import create_target_values
from music_flow.dataset.download_audio_features import download_audio_features
from music_flow.dataset.helper.folder_setup import setup_folders
from music_flow.dataset.read_streams import read_streams


def main():
    setup_folders()
    read_streams()
    create_target_values()
    download_audio_features()
    create_audio_features_dataset()
    create_dataset()


if __name__ == "__main__":
    main()
