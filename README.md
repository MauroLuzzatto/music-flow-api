# music-flow

Use your spotify streaming history to create a machine learning model that predicts the number of future plays of a song using the spotify audio features.


## Plan
- download features from streaming-history
- download features from random tracks
- calculate target values
    - number of plays
    - time listend to a song
    - buckets:
        - yes, no
        - low, medium, high, very high
- train model using GridSearch
- save different model versions
- use API to serve model
- use interface to predict output per song and artist name



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
