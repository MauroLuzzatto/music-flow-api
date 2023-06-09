import os

import pandas as pd
from pandas_profiling import ProfileReport

from music_flow.core.utils import create_folder, path_dataset, path_reports

dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0)
profile = ProfileReport(dataset, title="Pandas Profiling Report", explorative=True)
create_folder(path_reports)
profile.to_file(os.path.join(path_reports, "dataset_report.html"))
