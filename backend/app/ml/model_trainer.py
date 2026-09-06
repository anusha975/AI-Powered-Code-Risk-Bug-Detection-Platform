"""
Model Training and Synthetic Dataset Generation for Code Risk Scoring.

Constructs synthetic training data across distinct security risk profiles,
fits a Scikit-learn RandomForestRegressor, and validates evaluation metrics.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from app.ml.feature_extractor import FEATURE_NAMES
from app.ml.preprocessor import FeaturePreprocessor


class RiskModelTrainer:
    """Manages synthetic data generation, model fitting, and evaluation metrics."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.preprocessor = FeaturePreprocessor()
        self.model: RandomForestRegressor = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_split=4,
            random_state=self.random_state
        )
        self.is_trained: bool = False
        self.evaluation_metrics: Dict[str, float] = {}

    def generate_synthetic_dataset(self, n_samples: int = 1200) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic feature vectors and target risk scores (0-100).

        Synthetic profiles:
        1. Pristine / Clean Code (Score: 0 - 15)
        2. Low-Risk / Minor Quality Smells (Score: 15 - 35)
        3. Medium-Risk / Complexity & Error Handling (Score: 35 - 65)
        4. High-Risk / Known Vulnerabilities (Score: 65 - 85)
        5. Critical-Risk / Remote Code Execution & Exposed Secrets (Score: 85 - 100)
        """
        np.random.seed(self.random_state)
        samples_per_profile = n_samples // 5

        X_list = []
        y_list = []

        # Profile 1: Pristine
        for _ in range(samples_per_profile):
            crit = 0.0
            high = 0.0
            med = 0.0
            low = np.random.choice([0.0, 1.0], p=[0.8, 0.2])
            sec = 0.0
            comp = 0.0
            err = 0.0
            style = low
            ast_f = low
            bandit_f = 0.0
            max_c = 0.5 if low > 0 else 0.0
            avg_c = max_c
            cyclo = float(np.random.randint(1, 4))
            depth = float(np.random.randint(0, 3))
            density = float(low * np.random.uniform(0.5, 2.0))
            secret = 0.0

            score = np.clip(np.random.normal(5.0, 3.0), 0.0, 15.0)
            X_list.append([crit, high, med, low, sec, comp, err, style, ast_f, bandit_f, max_c, avg_c, cyclo, depth, density, secret])
            y_list.append(score)

        # Profile 2: Low Risk
        for _ in range(samples_per_profile):
            crit = 0.0
            high = 0.0
            med = np.random.choice([0.0, 1.0], p=[0.7, 0.3])
            low = float(np.random.randint(1, 4))
            sec = 0.0
            comp = float(np.random.choice([0.0, 1.0]))
            err = float(np.random.choice([0.0, 1.0]))
            style = low
            ast_f = float(np.random.randint(1, 3))
            bandit_f = float(np.random.choice([0.0, 1.0]))
            max_c = float(np.random.uniform(0.6, 0.8))
            avg_c = float(np.random.uniform(0.5, 0.7))
            cyclo = float(np.random.randint(3, 8))
            depth = float(np.random.randint(2, 4))
            density = float(np.random.uniform(2.0, 6.0))
            secret = 0.0

            score = np.clip(np.random.normal(25.0, 5.0), 16.0, 35.0)
            X_list.append([crit, high, med, low, sec, comp, err, style, ast_f, bandit_f, max_c, avg_c, cyclo, depth, density, secret])
            y_list.append(score)

        # Profile 3: Medium Risk
        for _ in range(samples_per_profile):
            crit = 0.0
            high = np.random.choice([0.0, 1.0], p=[0.8, 0.2])
            med = float(np.random.randint(2, 6))
            low = float(np.random.randint(1, 5))
            sec = float(np.random.randint(1, 3))
            comp = float(np.random.randint(1, 4))
            err = float(np.random.randint(1, 3))
            style = float(np.random.randint(1, 4))
            ast_f = float(np.random.randint(2, 6))
            bandit_f = float(np.random.randint(1, 4))
            max_c = float(np.random.uniform(0.7, 0.9))
            avg_c = float(np.random.uniform(0.65, 0.85))
            cyclo = float(np.random.randint(8, 20))
            depth = float(np.random.randint(3, 7))
            density = float(np.random.uniform(6.0, 15.0))
            secret = 0.0

            score = np.clip(np.random.normal(50.0, 7.0), 36.0, 65.0)
            X_list.append([crit, high, med, low, sec, comp, err, style, ast_f, bandit_f, max_c, avg_c, cyclo, depth, density, secret])
            y_list.append(score)

        # Profile 4: High Risk
        for _ in range(samples_per_profile):
            crit = np.random.choice([0.0, 1.0], p=[0.7, 0.3])
            high = float(np.random.randint(2, 5))
            med = float(np.random.randint(2, 8))
            low = float(np.random.randint(2, 6))
            sec = float(np.random.randint(2, 7))
            comp = float(np.random.randint(1, 5))
            err = float(np.random.randint(1, 4))
            style = float(np.random.randint(1, 5))
            ast_f = float(np.random.randint(3, 8))
            bandit_f = float(np.random.randint(2, 6))
            max_c = float(np.random.uniform(0.85, 0.98))
            avg_c = float(np.random.uniform(0.75, 0.92))
            cyclo = float(np.random.randint(15, 35))
            depth = float(np.random.randint(4, 9))
            density = float(np.random.uniform(12.0, 25.0))
            secret = np.random.choice([0.0, 1.0], p=[0.6, 0.4])

            score = np.clip(np.random.normal(75.0, 5.0), 66.0, 85.0)
            X_list.append([crit, high, med, low, sec, comp, err, style, ast_f, bandit_f, max_c, avg_c, cyclo, depth, density, secret])
            y_list.append(score)

        # Profile 5: Critical Risk
        for _ in range(samples_per_profile):
            crit = float(np.random.randint(1, 4))
            high = float(np.random.randint(2, 7))
            med = float(np.random.randint(2, 9))
            low = float(np.random.randint(1, 8))
            sec = float(np.random.randint(3, 10))
            comp = float(np.random.randint(1, 6))
            err = float(np.random.randint(1, 5))
            style = float(np.random.randint(1, 6))
            ast_f = float(np.random.randint(4, 10))
            bandit_f = float(np.random.randint(3, 8))
            max_c = float(np.random.uniform(0.9, 1.0))
            avg_c = float(np.random.uniform(0.82, 0.96))
            cyclo = float(np.random.randint(20, 50))
            depth = float(np.random.randint(5, 12))
            density = float(np.random.uniform(18.0, 45.0))
            secret = np.random.choice([0.0, 1.0], p=[0.2, 0.8])

            score = np.clip(np.random.normal(92.0, 4.0), 86.0, 100.0)
            X_list.append([crit, high, med, low, sec, comp, err, style, ast_f, bandit_f, max_c, avg_c, cyclo, depth, density, secret])
            y_list.append(score)

        X = np.array(X_list, dtype=np.float64)
        y = np.array(y_list, dtype=np.float64)
        return X, y

    def train(self, n_samples: int = 1200) -> Dict[str, float]:
        """
        Generate synthetic data, fit preprocessor and model, and record evaluation metrics.
        """
        X, y = self.generate_synthetic_dataset(n_samples=n_samples)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )

        X_train_scaled = self.preprocessor.fit_transform(X_train)
        X_test_scaled = self.preprocessor.transform(X_test)

        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test_scaled)
        mse = float(mean_squared_error(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        self.evaluation_metrics = {
            "r2_score": round(r2, 4),
            "mae": round(mae, 4),
            "rmse": round(np.sqrt(mse), 4),
            "training_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
        }

        return self.evaluation_metrics

    def predict(self, feature_vector: np.ndarray) -> float:
        """
        Predict continuous risk score (0-100) using the trained Scikit-learn model.
        """
        if not self.is_trained:
            self.train()

        scaled_vector = self.preprocessor.transform(feature_vector)
        pred = float(self.model.predict(scaled_vector)[0])
        return float(np.clip(pred, 0.0, 100.0))


# Global singleton trainer for cached inference
_TRAINER_INSTANCE: Optional[RiskModelTrainer] = None


def get_risk_model_trainer() -> RiskModelTrainer:
    """Retrieve or initialize the singleton RiskModelTrainer instance."""
    global _TRAINER_INSTANCE
    if _TRAINER_INSTANCE is None:
        _TRAINER_INSTANCE = RiskModelTrainer()
        _TRAINER_INSTANCE.train()
    return _TRAINER_INSTANCE
