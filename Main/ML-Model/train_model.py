import csv
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV


def find_best_param(X_train, X_test, y_train, y_test):
    estimator = RandomForestClassifier()
    random_grid = {'criterion': ['entropy', 'gini'],
                   'n_estimators': [100, 200],
                   'max_features': ['auto'],
                   'max_depth': [2, 5],
                   'min_samples_split': [2, 4],
                   'min_samples_leaf': [1],
                   'bootstrap': [True, False],
                   'warm_start': [True],
                   'oob_score': [True],
                   'min_impurity_decrease': [0, 0.0006, 0.0012, 0.0025, 0.005, 0.01, 0.05, 0.1]}
    clf = RandomizedSearchCV(estimator=estimator, param_distributions=random_grid, n_iter=400, cv=2, verbose=3,
                             random_state=42, n_jobs=6)
    clf.fit(X_train, y_train)
    params = clf.best_params_
    print(params)
    print(clf.score(X_train, y_train))
    y_pred = clf.predict(X_test)
    print("Accuracy", metrics.accuracy_score(y_test, y_pred))
    return params

def train_on_complete_data(X_all, Y_all, X_prediction, best_params):
    classifier = RandomForestClassifier(warm_start = best_params['warm_start'],
                                        oob_score = best_params['oob_score'],
                                        n_estimators = best_params['n_estimators'],
                                        min_samples_split = best_params['min_samples_split'],
                                        min_samples_leaf = best_params['min_samples_leaf'],
                                        min_impurity_decrease = best_params['min_impurity_decrease'],
                                        max_features = best_params['max_features'],
                                        max_depth = best_params['max_depth'],
                                        criterion = best_params['criterion'],
                                        bootstrap = best_params['bootstrap'])
    classifier.fit(X_all, Y_all)
    predictions = classifier.predict(X_prediction)
    return predictions

def create_blacklist(predictions, new_ip_data):
    blacklist = []
    del new_ip_data[0]
    for x, line in enumerate(new_ip_data):
        if predictions[x] == 1:
            blacklist.append(line[0])
        else:
            continue
    return blacklist


# random_grid = {'criterion': ['entropy', 'gini'],
#                    'n_estimators': [100, 200, 300, 400, 500, 600],
#                    'max_features': ['auto', 'sqrt', 'log2'],
#                    'max_depth': [2, 5, 10, 20, 30, 40],
#                    'min_samples_split': [2, 4, 6, 8],
#                    'min_samples_leaf': [1, 2, 3, 4],
#                    'bootstrap': [True, False],
#                    'warm_start': [True, False],
#                    'oob_score': [True, False],
#                    'min_impurity_decrease': [0, 0.0006, 0.0012, 0.0025, 0.005, 0.01, 0.05, 0.1]}