secret_key = "highscore"


class Highscore:
    def __init__(self, request):
        self.session = request.session
        scores = self.session.get(secret_key)

        if not scores:
            # save an empty scores dict in the session
            scores = self.session[secret_key] = {}

        self.scores = scores

    def add_score(self, id, song, artist, prediction):
        if id not in self.scores:
            self.scores[id] = {
                "song": song,
                "artist": artist,
                "prediction": prediction,
            }

    def get_highscore(self):
        highscore = sorted(
            self.scores.values(), key=lambda x: x["prediction"], reverse=True
        )[:5]
        return highscore
