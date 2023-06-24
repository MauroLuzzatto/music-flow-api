from typing import Dict


def map_score_to_emoji(score) -> Dict[str, str]:
    values = [
        (0.3, "😐", "This song needs to grow on me!"),
        (0.5, "🙂", "Nice track!"),
        (1.0, "😃", "Cool track!"),
        (2.0, "😄", "OMG, how did I not know this song?"),
        (100.0, "😍", "What a banger!"),
    ]
    emoji = ""
    text = ""
    for threshold, emoji, text in values:
        if score < threshold:
            break

    return {"emoji": emoji, "text": text}


def prepare_raw_features_response(raw_features, status_code):
    # Do we need this function?
    keys = ["status", "failure_type", "description"]
    detail = {key: raw_features[key] for key in keys}
    detail["status_code"] = status_code
    return detail
