class MLModel:
    """Dummy ML model returning average of data."""

    def predict(self, data: list[float]) -> float:
        if not data:
            raise ValueError("data cannot be empty")
        return sum(data) / len(data)
