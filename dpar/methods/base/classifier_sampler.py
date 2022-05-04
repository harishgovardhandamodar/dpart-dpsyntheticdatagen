import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

from dpar.methods.base import CategorySampler
from dpar.methods.utils.sklearn_encoder import SklearnEncoder


class LogisticRegression(CategorySampler):
    clf_class = None

    def __init__(self, epsilon=None, *args, **kwargs):
        super().__init__(epsilon=epsilon)
        self.label_encoder = None
        self.X_encoder = None
        self.clf = None
        self.args = args
        self.kwargs = kwargs

    def preprocess_X(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.X_encoder is None:
            # X Processor
            self.X_encoder = SklearnEncoder()
            self.X_encoder.fit(X)

        return self.X_encoder.transform(X)

    def preprocess_y(self, y: pd.Series) -> pd.Series:
        if self.label_encoder is None:
            # y Processor
            self.label_encoder = OrdinalEncoder()
            self.label_encoder.fit(y.to_frame())

        return pd.Series(
            self.label_encoder.transform(y.to_frame()).squeeze(),
            index=y.index,
            name=y.name,
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.clf = self.clf_class(epsilon=self.epsilon, *self.args, **self.kwargs)
        self.clf.fit(X, y)

    def postprocess_y(self, y: pd.Series) -> pd.Series:
        return pd.Series(
            self.label_encoder.inverse_transform(y.to_frame()).squeeze(),
            index=y.index,
            name=y.name,
        )

    def sample(self, X: pd.DataFrame) -> pd.Series:
        y_proba = self.clf.predict_proba(X)

        uniform_noise = np.random.uniform(size=[X.shape[0], 1])
        y = np.sum(uniform_noise > np.cumsum(y_proba, axis=1), axis=1).astype(int)
        return pd.Series(y, index=X.index)