from ..state import ImageState

class PipelineAdapter:
    def __init__(self, preprocess_fn, detect_fn):
        self.preprocess_fn = preprocess_fn
        self.detect_fn = detect_fn

    def preprocess(self, image: ImageState):
        image.preprocessed = self.preprocess_fn(
            image.original,
            image.preprocess_params
        )

    def detect(self, image: ImageState):
        image.detected = self.detect_fn(
            image.preprocessed,
            image.detect_params
        )