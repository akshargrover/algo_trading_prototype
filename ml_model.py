from config import LOG
from typing import  Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

class MLModel:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy().dropna()

    def prepare_features(self) -> Tuple[pd.DataFrame, pd.Series]:
        d = self.df
        # features: rsi, macd, macd_signal, hist, volume, sma20, sma50, returns
        d["return_1d"] = d["Close"].pct_change().shift(-1)  # what we want to predict
        d = d.dropna()
        X = d[["rsi", "macd", "signal", "hist", "Volume", "sma20", "sma50"]]
        y = (d["return_1d"] > 0).astype(int)  # 1 if price goes up next day
        return X, y

    def train(self, model_type: str = "tree") -> Tuple[object, float]:
        X, y = self.prepare_features()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        if model_type == "tree":
            model = DecisionTreeClassifier(max_depth=5)
        else:
            model = LogisticRegression(max_iter=500)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        LOG.info(f"ML model ({model_type}) accuracy: {acc:.4f}")
        return model, acc
