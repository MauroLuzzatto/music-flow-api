# music-flow

MusicFlow is a machine learning-based API that predicts the hypothetical number of song streams on Spotify using the Spotify audio features and track metadata. This API uses a personal Spotify streaming history to train a machine learning model that predicts the number of streams for a given song.

The MusicFlow API is built using the FastAPI framework, which makes it fast, easy to use, and well-documented. The API is based on the OpenAPI standard, which allows for easy integration with other applications.

<!-- ## Features

The MusicFlow API provides the following endpoints:

- `musicflow.link` - The home page of the MusicFlow API.
- `musicflow.link/health` - Returns the health status of the API.
- `musicflow.link/raw_features/?song={song}&artist={artist}` - Returns the raw audio features of a given song on Spotify.
- `musicflow.link/features/?song={song}&artist={artist}` - Returns the processed audio features of a given song on Spotify.
- `musicflow.link/prediction/?song={song}&artist={artist}` - Predicts the hypothetical number of song streams for a given song based on the Spotify audio features and track metadata. -->

## Usage

Once the server is running, you can send a GET request to any of the above endpoints to get the desired output.

This endpoint returns the home page of the MusicFlow API:
```
musicflow.link
```


This endpoint returns the health status of the MusicFlow API. If the API is running and healthy, it will return a JSON response with the status ok.
```
musicflow.link/health
```

This endpoint returns the raw audio features of a given song on Spotify. The input parameters song and artist should be the name of the song and the name of the artist, respectively.

The API will return a JSON response with the raw audio features of the song on Spotify.

```
musicflow.link/raw_features/?song={song}&artist={artist}
```
This endpoint returns the processed audio features of a given song on Spotify. The input parameters song and artist should be the name of the song and the name of the artist, respectively.

The API will return a JSON response with the processed audio features of the song on Spotify.
```
musicflow.link/features/?song={song}&artist={artist}
```

This endpoint predicts the hypothetical number of song streams for a given song based on the Spotify audio features and track metadata. The input parameters song and artist should be the name of the song and the name of the artist, respectively.

The API will return a JSON response with the predicted number of streams for the given song.
```
musicflow.link/prediction/?song={song}&artist={artist}
```


## Getting started

- get spotify API access client id and client secret
- request spotify streaming history
- download data and create dataset
- train ml model
- setup API using aws





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
