from dataclasses import dataclass


@dataclass
class ResponseFailures:
    failure_type: str
    description: str


formating_failure = ResponseFailures(
    failure_type="formatting",
    description="Could not format the features",
)
prediction_failure = ResponseFailures(
    failure_type="prediction",
    description="Failed to make a prediction",
)
spotify_failure = ResponseFailures(
    failure_type="spotify",
    description="Could not fetch the song or audio features from Spotify API",
)
