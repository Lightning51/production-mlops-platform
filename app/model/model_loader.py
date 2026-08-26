from pathlib import Path
from threading import Lock
from typing import Any

import joblib

from app.config.settings import get_settings


class ModelLoader:
    """
    Responsible for loading and providing access to the trained ML model.

    The model is loaded lazily and cached in memory so that prediction
    requests do not repeatedly load the model from disk.
    """

    def __init__(self) -> None:
        self._model: Any | None = None
        self._lock = Lock()
        self._settings = get_settings()

    def load_model(self) -> Any:
        """
        Load the model into memory if it has not already been loaded.

        Returns:
            The trained ML pipeline.

        Raises:
            FileNotFoundError: If the configured model file doesn't exist.
            RuntimeError: If the model cannot be loaded.
        """

        if self._model is not None:
            return self._model

        with self._lock:
            if self._model is not None:
                return self._model

            model_path = Path(self._settings.model_local_path)

            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            try:
                self._model = joblib.load(model_path)
            except Exception as exc:
                raise RuntimeError(f"Failed to load model from {model_path}") from exc

        return self._model

    def is_loaded(self) -> bool:
        """
        Return whether the model is currently loaded.
        """

        return self._model is not None

    def get_model(self) -> Any:
        """
        Return the loaded model.

        Loads the model if it has not been loaded yet.
        """

        return self.load_model()


model_loader = ModelLoader()
