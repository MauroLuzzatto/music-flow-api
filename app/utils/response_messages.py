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

failure_dict = {
    "formating_failure": formating_failure,
    "prediction_failure": prediction_failure,
    "spotify_failure": spotify_failure,
}


def get_exception_details(exception_type: str, status_code: int) -> dict:
    """return a dictionary with the exception details

    Args:
        exception_type (str): _description_
        status_code (int): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    failure_class = failure_dict.get(exception_type)
    if not failure_class:
        raise ValueError(f"Could not find exception type: {exception_type}")
    failure_type = failure_class.failure_type
    description = failure_class.description
    detail = {
        "status": "failure",
        "failure_type": failure_type,
        "description": description,
        "status_code": status_code,
    }
    return detail
