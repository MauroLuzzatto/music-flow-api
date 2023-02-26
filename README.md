# music-flow

Use your spotify streaming history to create a machine learning model that predicts the number of future plays of a song using the spotify audio features.


## Plan
- request streaming history from spotify
- find some random tracks (e.g kaggle datasets)
- calculate the numer of streams per track (=target values)
- download features for the tracks
- create the dataset containg the features and the number of streams
- train model using GridSearch
- save different model versions
- use API to serve model
- use API to predict number of streams per track



## Features
- danceability
- energy
- key
- loudness
- mode
- speechiness
- acousticness
- instrumentalness
- liveness
- valence
- tempo
- type
- id
- uri
- track_href
- analysis_url
- duration_ms
- time_signature
- ms_played
- end_time
- track
- artist
- error


column_names: ['number_of_available_markets', 'release_year', 'release_month', 'release_day', 'date_is_complete', 'num_artists', 'duration_ms', 'explicit', 'popularity', 'danceability', 'energy', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature', 'A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'Unknown', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']


## TODO:

Ml project:
- Version model
- Add logging
- Allow for continous training
- Use data classes for sample
- Make better feature processing pipeline
- Improve api reponse for formatted feature
- Deep learning
