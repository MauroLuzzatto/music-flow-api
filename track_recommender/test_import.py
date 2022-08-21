

import os

print(os.environ.get('PYTHONPATH', ''))
from track_recommender.model import config


print(config.path_base)
