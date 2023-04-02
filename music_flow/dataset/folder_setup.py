from music_flow.core.utils import (
    path_data,
    path_features,
    path_dataset,
    path_results,
    path_reports,
    path_data_lake,
    path_raw,
    path_data_lake_success,
    path_data_lake_failed,
)
from music_flow.core.utils import create_folder


def setup_folders():

    path_folders = [
        path_data,
        path_features,
        path_dataset,
        path_results,
        path_reports,
        path_data_lake,
        path_raw,
        path_data_lake_success,
        path_data_lake_failed,
    ]
    for path_folder in path_folders:
        _ = create_folder(path_folder)

    print("Folder setup completed!")


if __name__ == "__main__":
    setup_folders()