from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

def train_predictor(df: pd.DataFrame) -> float:
    df = df.dropna()
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    X = df[['rsi', '20dma', '50dma']]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = DecisionTreeClassifier().fit(X_train, y_train)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return accuracy