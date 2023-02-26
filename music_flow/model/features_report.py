import os

import pandas as pd
from pandas_profiling import ProfileReport

from music_flow.core.utils import path, path_dataset

path_reports = os.path.join(path, "reports")
dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0)


profile = ProfileReport(dataset, title="Pandas Profiling Report", explorative=True)
profile.to_file(os.path.join(path_reports, "dataset_report.html"))
