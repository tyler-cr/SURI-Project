#!/usr/bin/env python3

from math import sqrt
import numpy as np
from numpy.typing import NDArray
#from sklearn.metrics import roc_auc_score, roc_curve
#import matplotlib as plt

import random

# Currently just an example of a binary model
def tally_predictions(classifier, test: NDArray, answer_key: NDArray) -> list: 
    """
    Computes binary classification metrics (TP, TN, FP, FN) and model accuracy.

    Args:
        classifier: Trained classifier with predict() and score() methods
        test: Test dataset features (NDArray)
        answer_key: Ground truth labels (NDArray, 0 or 1)

    Returns:
        list: [true_positives, true_negatives, false_positives, false_negatives, accuracy_score]
    """

    predictions = classifier.predict(test)
    score = classifier.score(test,answer_key)

    true_positives = true_negatives = false_positives = false_negatives = 0

    for i in range(len(answer_key)):
        if (predictions[i] == 0) and (answer_key[i] == 0): 
            true_negatives += 1
        elif (predictions[i] == 0) and (answer_key[i] == 1): 
            false_negatives += 1
        elif (predictions[i] == 1) and (answer_key[i] == 0): 
            false_positives += 1
        else:
            true_positives += 1
    return [true_positives, true_negatives, false_positives, false_negatives, score]

# This still assumes a binary model
def basic_metrics(tally: list):
    """
    Computes binary classification performance metrics from confusion matrix counts.

    Args:
        tally: Output from tally_predictions() containing [TP, TN, FP, FN, accuracy]

    Returns:
        dict: Classification metrics including TPR, TNR, PPV, NPV, FPR, FNR
    
    Notes:
        • TPR/Sensitivity: True Positive Rate
        • TNR/Specificity: True Negative Rate
        • PPV/Precision: Positive Predictive Value
        • FPR = 1 - TNR
        • FNR = 1 - TPR
    """

    tp, tn, fp, fn, _ = tally
    return {
        "TPR": tp / (tp + fn),  
        "TNR": tn / (tn + fp),  
        "PPV": tp / (tp + fp),  
        "NPV": tn / (tn + fn),  
        "FPR": fp / (fp + tn),  
        "FNR": fn / (fn + tp)   
    }

def advanced_metrics(tally: list, basic_metrics: dict): 
    """
    Computes advanced binary classification performance metrics.

    Args:
        tally: Output from tally_predictions() containing [TP, TN, FP, FN, accuracy]
        basic_metrics: Output from basic_metrics() containing TPR, TNR, PPV, NPV

    Returns:
        dict: Advanced metrics including F1, MCC, Kappa, Informedness, Markedness

    Notes:
        • F1: Range from 0 to 1. Harmonic mean of precision and recall. Doesn't take into account true negatives.
        • MCC: Geometric mean of informedness and markedness. Basically a combo of the two, and takes full confusion matrix into account. Range: -1 to 1.
        • Kappa: Tries to account for model putting input in correct class by accident. Lots of numbers involved. Negative is bad, positive is good; usually around 0 to 1.
        • Informedness: Combination of sensitivity and specificity. -1 means everything is wrong. 0 means essentially guessing. 1 means perfect.
        • Markedness: How well the model is doing at being correct when it claims particular labels for particular inputs. Same numerically as Informedness.

    Raises:
        ZeroDivisionError: If denominators are zero (e.g., empty predictions or perfect class imbalance)
        KeyError: If required keys missing from basic_metrics dict
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
    """
    Generates a Receiver Operating Characteristics (ROC) curve and calculates AUC.

    Args:
        labels: Path to .npy file containing ground truth labels
        probs: Path to .npy file containing predicted probabilities
        pname: Filename/path for saving the output plot

    Notes:
        • ROC stands for Receiver Operating Characteristics (curve)
        • AUC: Area Under Curve - overall model performance metric
        • Plots TPR vs FPR with perfect classification line (diagonal)
        • Saves figure at 300 DPI resolution
    
    Raises:
        FileNotFoundError: If input .npy files don't exist
        ValueError: If shapes of labels and probs don't match or probs[:,1] invalid
    """

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

def confusion_matrix(y_test, y_predict, n=10):
    """
    Constructs a multi-class confusion matrix from ground truth and predictions.

    Args:
        y_test: Ground truth labels (array-like of class indices)
        y_predict: Predicted labels (array-like of class indices)
        n: Number of classes (default 10); defines matrix dimensions

    Returns:
        np.ndarray: nxn confusion matrix with dtype uint32
            Rows = actual class, Columns = predicted class
            Cell [i, j] = count of instances with true label i, predicted as j

    Notes:
        • Main diagonal (i==j) represents correct classifications
        • Off-diagonal elements show misclassification patterns
        • Each row sum equals total instances of that true class
        • Each column sum equals total instances predicted as that class
    
    Raises:
        IndexError: If any label exceeds n-1 (class index out of bounds)
        ValueError: If y_test and y_predict have mismatched lengths
    """
    con_mat = np.zeros((n,n), dtype="uint32")
    for i, y in enumerate (y_test):
        con_mat[y, y_predict[i]] += 1
    return con_mat


if __name__ == "__main__":

    con_mat = np.zeros((10,10))
    for x in range(10):
        for y in range(10):
            for z in range(10):
                con_mat[x][y] = random.randint(0,9)

    print(con_mat)