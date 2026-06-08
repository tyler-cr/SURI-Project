#!/usr/bin/env python3

from math import sqrt
import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib as plt

import random

# Currently just an example of a binary model
def tally_predictions(classifier, test: NDArray, answer_key: NDArray) -> list: 

    predictions = classifier.predict(test)
    score = classifier.score(test,answer_key)

    true_positives = true_negatives = false_positives = false_negatives = 0

    for i in range(len(answer_key)):
        if (predictions[i] == 0) and (predictions[i] == 0): 
            true_negatives += 1
        elif (predictions[i] == 0) and (predictions[i] == 1): 
            false_negatives += 1
        elif (predictions[i] == 1) and (predictions[i] == 0): 
            false_positives += 1
        else:
            true_positives += 1
    return [true_positives, true_negatives, false_positives, false_negatives, score]

# This still assumes a binary model
def basic_metrics(tally: list):
    tp, tn, fp, fn, _ = tally
    return {
        "TPR": tp / (tp + fn),  # True Positive Rate (Sensitivity): Prob that instance of class 1 correctly identified
        "TNR": tn / (tn + fp),  # True Negative Rate (Specificity): Prob that instance of class 0 correctly identified
        "PPV": tp / (tp + fp),  # Positive Predictive Value (Precision): Prob that when model says instance is class 1, it's correct
        "NPV": tn / (tn + fn),  # Negative Predictive Value: Prob that when model says instance is class 0, it's correct
        "FPR": fp / (fp + tn),  # False Positive Rate: 1 - PPV
        "FNR": fn / (fn + tp)   # False Negative Rate: 1 - FPR
    }

def advanced_metrics(tally: list, basic_metrics: dict): 
    """
    F1: Range from 0 to 1. Harmonic mean of the precision and recall. Doesn't take into account true negatives

    MCC: Geometric mean of informedness and markedness. Basically combo of the two, and takes full confusion matrix into account. -1 to 1

    Kappa: Tries to account for model putting input in correct class by accident. Lots of numbers. Negative bad, positive good. usually around 0 to 1

    Informedness: Combination of Sensitivity and Specificity. -1 means everything is wrong. 0 means essentially guessing. 1 means perfect

    Markedness: How well the model is doing at being correct correct when it claims particilar labels for particular inputs. Same numerically as Informedness
    """

    tp, tn, fp, fn, _ = tally
    n = tp+tn+fp+fn
    po = (tp+tn)/n # Observed accuracy
    pe = (tp+fn)*(tp+fp)/n**2 + (tn+fp)*(tn+fn)/n**2 # Accuracy expected by chance

    return {
        "F1": 2.0*basic_metrics["PPV"]*basic_metrics["TPR"] / (basic_metrics["PPV"] + basic_metrics["TPR"]),
        "MCC": (tp*tn - fp*fn) / sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)),
        "Kappa": (po - pe) / (1.0 - pe),
        "Informedness": basic_metrics["TPR"] + basic_metrics["TNR"] - 1.0,
        "Markedness": basic_metrics["PPV"] + basic_metrics["NPV"] - 1.0 
    }

# ROC stands for Reciever Operating Characteristics (curve)
def ROC_curve(labels, probs, pname):
    labels = np.load(labels)
    probs  = np.load(probs)

    # Area Under Curve
    auc = roc_auc_score(labels, probs[:,1])

    # Reciever Operating Characteristics
    roc = roc_curve(labels, probs[:,1])

    print(f"AUC: {auc:.6f}")

    plt.plot(roc[0], roc[1], color = 'r')
    plt.plot([0,1], [0,1], color = 'k', linestyle= ':')

    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.tight_layout(pad=0, w_pad=0, h_pad=0)
    plt.savefig(pname, dpi=300)
    plt.show()

def confusion_matrix(y_test, y_predict, n=10):
    con_mat = np.zeros((n,n), dtype="uint32")
    for i, y in enumerate (y_test):
        con_mat[y, y_predict[i]] += 1
    return con_mat


if __name__ == "__main__":

    con_mat = np.zeros((10,10), dtype="uint8")
    for x in range(10):
        for y in range(10):
            for z in range(10):
                con_mat[x][y][z] = random.randint(0,9)

    print(con_mat)