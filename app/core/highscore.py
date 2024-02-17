from typing import List, Tuple

secret_key = "highscore"


class Highscore:
    def __init__(self, request, is_reset: bool = False, max_values: int = 4):
        self.session = request.session
        self.max_values = max_values

        scores = {} if is_reset else self.session.get(secret_key)
        if not scores:
            # save an empty scores dict in the session
            scores = self.session[secret_key] = {}
        self.scores = scores

    def add_score(self, id: str, prediction: str, header: str) -> None:
        """_summary_

        Args:
            id (_type_): _description_
            prediction (_type_): _description_
            header (_type_): _description_
        """
        if id not in self.scores:
            self.scores[id] = {
                "prediction": prediction,
                "header": header,
            }

    def get_highscore(self) -> List[Tuple[float, str]]:
        """_summary_

        Returns:
            List[Tuple[float, str]]: _description_
        """
        highscore = sorted(
            self.scores.values(), key=lambda x: x["prediction"], reverse=True
        )[: self.max_values]
        return highscore
