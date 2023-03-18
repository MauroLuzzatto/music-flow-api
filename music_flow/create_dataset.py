from music_flow.dataset.collect_spotify_streams import collect_streams
from music_flow.dataset.create_audio_features_dataset import (
    create_audio_features_dataset,
)
from music_flow.dataset.download_audio_features import download_audio_features
from music_flow.dataset.get_target_values import get_df_target_values
from music_flow.dataset.prepare_dataset import merge_dataset

df_streams = collect_streams()
df_target_values = get_df_target_values()

# shall the functions be merge?
download_audio_features()
df_audio_features = create_audio_features_dataset()

df_dataset = merge_dataset()

# collect streams
# create target values
# features features
# create dataset
