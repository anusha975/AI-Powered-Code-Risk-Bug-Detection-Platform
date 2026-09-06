"""
Feature Preprocessing and Scaling Pipeline for Code Risk Scoring.

Provides data normalization, bound clipping, and scaling transformations
for 16-dimensional static analysis feature vectors.
"""

from typing import List, Dict, Any, Union, Optional
import numpy as np
from sklearn.preprocessing import StandardScaler

from app.ml.feature_extractor import FEATURE_NAMES, feature_dict_to_vector


class FeaturePreprocessor:
    """Standardizes feature vectors and enforces consistent dimensional bounds."""

    def __init__(self) -> None:
        self.scaler: StandardScaler = StandardScaler()
        self.is_fitted: bool = False
        self.feature_names: List[str] = list(FEATURE_NAMES)

    def fit(self, X: Union[np.ndarray, List[List[float]]]) -> "FeaturePreprocessor":
        """
        Fit the StandardScaler on training matrix X.

        Args:
            X: 2D array or list of shape (n_samples, 16)
        """
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        self.scaler.fit(arr)
        self.is_fitted = True
        return self

    def transform(self, X: Union[np.ndarray, List[List[float]], Dict[str, float]]) -> np.ndarray:
        """
        Transform feature vectors using the fitted scaler.

        Args:
            X: Single dict, 1D vector, or 2D array of shape (n_samples, 16)

        Returns:
            Standardized numpy array of shape (n_samples, 16)
        """
        if isinstance(X, dict):
            vector = feature_dict_to_vector(X)
            arr = np.asarray([vector], dtype=np.float64)
        else:
            arr = np.asarray(X, dtype=np.float64)
            if arr.ndim == 1:
                arr = arr.reshape(1, -1)

        # Replace any NaN or Inf with 0.0
        arr = np.nan_to_num(arr, nan=0.0, posinf=100.0, neginf=0.0)

        if not self.is_fitted:
            # Fallback identity transform if not yet fitted
            return arr

        return self.scaler.transform(arr)

    def fit_transform(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """Fit scaler and transform matrix in a single step."""
        return self.fit(X).transform(X)
