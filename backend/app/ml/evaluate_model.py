import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix, roc_curve, precision_recall_curve, brier_score_loss

def evaluate(y, p, threshold=.5):
    predicted = np.asarray(p) >= threshold
    fpr, tpr, _ = roc_curve(y, p)
    precision, recall, _ = precision_recall_curve(y, p)
    return dict(accuracy=accuracy_score(y,predicted), precision=precision_score(y,predicted,zero_division=0), recall=recall_score(y,predicted,zero_division=0), f1=f1_score(y,predicted,zero_division=0), roc_auc=roc_auc_score(y,p), pr_auc=average_precision_score(y,p), brier=brier_score_loss(y,p), confusion_matrix=confusion_matrix(y,predicted).tolist(), roc={'x':fpr[::max(1,len(fpr)//100)].tolist(),'y':tpr[::max(1,len(tpr)//100)].tolist()}, pr={'x':recall[::max(1,len(recall)//100)].tolist(),'y':precision[::max(1,len(precision)//100)].tolist()})
