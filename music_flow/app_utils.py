from typing import Dict


def map_score_to_emoji(score) -> Dict[str, str]:

    values = [
        (0.3, "😐", "This song needs to grow on me!"),
        (0.5, "🙂", "Nice track!"),
        (1.0, "😃" "Cool track!"),
        (2.0, "😄", "How did I not know this song?"),
        (100.0, "😍", "What a banger!"),
    ]
    emoji = ""
    description = ""
    for (
        threshold,
        emoji,
        description,
    ) in values:
        if score < threshold:
            break

    return {"emoji": emoji, "description": description}
