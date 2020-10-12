from joblib import dump
import pandas
import numpy as np
from sklearn.decomposition import PCA
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline

dataset_path = "Dataset.csv"

raw_dataset = pandas.read_csv(dataset_path)
label = np.array(raw_dataset['label'])
dataset = raw_dataset.to_numpy()[0:, 1:-1]

X_train, X_test, y_train, y_test = train_test_split(
    dataset, label, random_state=2)

pipe = Pipeline([("pca", PCA(n_components=20)),
                 ("knn", neighbors.KNeighborsClassifier(n_neighbors=3))])

pipe.fit(X_train, y_train)

print("Test score: {:.2f}".format(pipe.score(X_test, y_test)))

dump(pipe, "model.joblib")
