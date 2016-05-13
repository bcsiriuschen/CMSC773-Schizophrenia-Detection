import numpy as np
import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import zero_one_loss
from sklearn.ensemble import AdaBoostClassifier
from sklearn.datasets import load_svmlight_file


def get_data(filename):
    data = load_svmlight_file(filename)
    return data[0], data[1]

n_estimators = 600
# A learning rate of 1. may not be optimal for both SAMME and SAMME.R
learning_rate = 0.1

file_path = './early/'

# early real 0.208797280237
# early discrete 0.19912499489

dt_stump_err_list = []
dt_err_list = []
ada_discrete_err_ave = np.zeros((n_estimators,))
ada_discrete_err_train_ave = np.zeros((n_estimators,))
ada_real_err_ave = np.zeros((n_estimators,))
ada_real_err_train_ave = np.zeros((n_estimators,))

for fold in range(10):
    X_test, y_test = get_data('%searly.test.%s.scale.data' % (file_path, str(fold)))
    X_train, y_train = get_data('%searly.train.%s.scale.data' % (file_path, str(fold)))

    dt_stump = DecisionTreeClassifier(max_depth=1, min_samples_leaf=1)
    dt_stump.fit(X_train, y_train)
    dt_stump_err = 1.0 - dt_stump.score(X_test, y_test)
    dt_stump_err_list.append(dt_stump_err)

    dt = DecisionTreeClassifier(max_depth=9, min_samples_leaf=1)
    dt.fit(X_train, y_train)
    dt_err = 1.0 - dt.score(X_test, y_test)
    dt_err_list.append(dt_err)

    ada_discrete = AdaBoostClassifier(
        base_estimator=dt_stump,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        algorithm="SAMME")
    ada_discrete.fit(X_train, y_train)

    ada_real = AdaBoostClassifier(
        base_estimator=dt_stump,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        algorithm="SAMME.R")
    ada_real.fit(X_train, y_train)

    ada_discrete_err = np.zeros((n_estimators,))
    for i, y_pred in enumerate(ada_discrete.staged_predict(X_test)):
        ada_discrete_err[i] = zero_one_loss(y_pred, y_test)/10.
    ada_discrete_err_ave += ada_discrete_err

    ada_discrete_err_train = np.zeros((n_estimators,))
    for i, y_pred in enumerate(ada_discrete.staged_predict(X_train)):
        ada_discrete_err_train[i] = zero_one_loss(y_pred, y_train)/10.
    ada_discrete_err_train_ave += ada_discrete_err_train

    ada_real_err = np.zeros((n_estimators,))
    for i, y_pred in enumerate(ada_real.staged_predict(X_test)):
        ada_real_err[i] = zero_one_loss(y_pred, y_test)/10.
    ada_real_err_ave += ada_real_err

    ada_real_err_train = np.zeros((n_estimators,))
    for i, y_pred in enumerate(ada_real.staged_predict(X_train)):
        ada_real_err_train[i] = zero_one_loss(y_pred, y_train)/10.
    ada_real_err_train_ave += ada_real_err_train

print min(ada_real_err_ave)
print min(ada_discrete_err_ave)

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot([1, n_estimators], [sum(dt_stump_err_list)/len(dt_stump_err_list)] * 2, 'k-',
        label='Decision Stump Error')
ax.plot([1, n_estimators], [sum(dt_err_list)/len(dt_err_list)] * 2, 'k--',
        label='Decision Tree Error')

ax.plot(np.arange(n_estimators) + 1, ada_discrete_err_ave,
        label='Discrete AdaBoost Test Error',
        color='red')
ax.plot(np.arange(n_estimators) + 1, ada_discrete_err_train_ave,
        label='Discrete AdaBoost Train Error',
        color='blue')
ax.plot(np.arange(n_estimators) + 1, ada_real_err_ave,
        label='Real AdaBoost Test Error',
        color='orange')
ax.plot(np.arange(n_estimators) + 1, ada_real_err_train_ave,
        label='Real AdaBoost Train Error',
        color='green')

ax.set_ylim((0.0, 0.5))
ax.set_xlabel('n_estimators')
ax.set_ylabel('error rate')

leg = ax.legend(loc='upper right', fancybox=True)
leg.get_frame().set_alpha(0.7)

plt.show()
