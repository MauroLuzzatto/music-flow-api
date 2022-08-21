

import os

from track_recommender.model import config

print(os.environ.get('PYTHONPATH', '').split(os.pathsep))

print(config.path_base)