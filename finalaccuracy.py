# -*- coding: utf-8 -*-
"""finalaccuracy.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pnF6K-VdXtl6IFBzeOW-Jhi1rLdWG8G-
"""

import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
from sklearn.svm import SVC
from sklearn.preprocessing import LabelBinarizer
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import recall_score, f1_score, roc_auc_score, log_loss, confusion_matrix
from sklearn.preprocessing import LabelBinarizer


# Function to normalize text
def simple_normalize_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Load the dataset
new_data_latest = pd.read_csv('/content/Dataset.csv')

# Normalize the reviews in the dataset
new_data_latest['normalized_review'] = new_data_latest['Reviews'].apply(simple_normalize_text)

# Clean the dataset by dropping rows with missing sentiments
new_data_latest_cleaned = new_data_latest.dropna(subset=['Sentiment'])

# Ensure the sentiments are numeric and drop rows with non-numeric sentiments
new_data_latest_cleaned = new_data_latest_cleaned[pd.to_numeric(new_data_latest_cleaned['Sentiment'], errors='coerce').notnull()]

# Convert sentiments to integers
new_data_latest_cleaned['Sentiment'] = new_data_latest_cleaned['Sentiment'].astype(int)

# Split the cleaned dataset into features (X) and labels (y)
X_new_latest = new_data_latest_cleaned['normalized_review']
y_new_latest = new_data_latest_cleaned['Sentiment']

# Vectorize the text data
vectorizer_previous = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
X_new_vec_latest = vectorizer_previous.fit_transform(X_new_latest)

# Split the vectorized data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_new_vec_latest, y_new_latest, test_size=0.2, random_state=45)

# Train and evaluate SVM model
model = SVC(kernel='linear', probability=True, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)



accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - Support Vector Machine Classifier")
plt.savefig("SVM_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for SVM')
plt.legend(loc="lower right")
plt.savefig("SVM_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()

import xgboost as xgb

# Initialize and train the XGBoost model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', n_estimators=501, objective='multi:softprob', num_class=3, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - XGBOOST Classifier")
plt.savefig("XGBOOST_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - XGBoost Classifier')
plt.legend(loc="lower right")
plt.savefig("XGBOOST_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()

from sklearn.ensemble import RandomForestClassifier

# Train the model
model = RandomForestClassifier(n_estimators=501, criterion='entropy', random_state = 42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - Random Forest Classifier")
plt.savefig("RandomForestClassifier_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Random Forest Classifier')
plt.legend(loc="lower right")
plt.savefig("RandomForest_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()

from sklearn.neighbors import KNeighborsClassifier

# Train the KNN model
model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - KNN Classifier")
plt.savefig("KNN_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - KNN Classifier')
plt.legend(loc="lower right")
plt.savefig("KNN_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()

from lightgbm import LGBMClassifier

# Train the LGBM model
model = LGBMClassifier(n_estimators=501, random_state=42)
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - LGBM Classifier")
plt.savefig("LGBMClassifier_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.tree import DecisionTreeClassifier

# Train the Decision Tree model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)
# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - Decision Tree Classifier")
plt.savefig("DecisionTree_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Decision Tree Classifier')
plt.legend(loc="lower right")
plt.savefig("DecisionTree_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()

from sklearn.naive_bayes import MultinomialNB

X_train_shifted = X_train - np.min(X_train)
X_test_shifted = X_test - np.min(X_test)

# Train the MultinomialNB model
model = MultinomialNB()
model.fit(X_train_shifted, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - GaussMultinomialNBianNB Classifier")
plt.savefig("MultinomialNB_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

y_prob = model.predict_proba(X_test)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score, log_loss
import matplotlib.pyplot as plt

# Assuming you've already shifted X_train and X_test as shown
X_train_shifted = X_train - np.min(X_train)
X_test_shifted = X_test - np.min(X_test)

# Train the MultinomialNB model
model = MultinomialNB()
model.fit(X_train_shifted, y_train)

# Correct: use shifted X_test for prediction
y_pred = model.predict(X_test_shifted)

accuracy_latest = accuracy_score(y_test, y_pred)
report_latest = classification_report(y_test, y_pred)

# Calculate the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Display the confusion matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Negative", "Neutral", "Positive"])
plt.figure(figsize=[10, 10])
disp.plot(cmap="Greens")
plt.title("Confusion Matrix - MultinomialNB Classifier")
plt.savefig("MultinomialNB_Confusion_Matrix.png", dpi=300, bbox_inches="tight")
plt.show()

# Predict probabilities with shifted X_test
y_prob = model.predict_proba(X_test_shifted)
print("Accuracy on Test Data: {:.2f}%".format(accuracy_latest * 100))
print("Classification Report on Test Data:\n", report_latest)
# Calculate ROC AUC Score
roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
print("ROC AUC Score:", roc_auc)

# Log Loss
logloss = log_loss(y_test, y_prob)
print("Log Loss:", logloss)

error_rate = 1 - accuracy_latest
print("Error Rate:", error_rate)

# Calculate TPR, TNR, FPR, FNR for each class
for i in range(cm.shape[0]):
    class_name = "Class " + str(i)
    tp = cm[i, i]
    fn = sum(cm[i, :]) - tp
    fp = sum(cm[:, i]) - tp
    tn = sum(sum(cm)) - tp - fn - fp

    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    fpr = fp / (fp + tn)
    fnr = fn / (fn + tp)

    print(class_name + ":")
    print("TPR (Sensitivity):", sensitivity)
    print("TNR (Specificity):", specificity)
    print("FPR:", fpr)
    print("FNR:", fnr)

from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt

# Binarize the labels for ROC curve plotting
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
n_classes = y_test_bin.shape[1]

# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Plot ROC curve
plt.figure(figsize=(10, 8))
colors = ['blue', 'red', 'green']
for i, color in enumerate(colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label='ROC curve of class {0} (area = {1:0.2f})'.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - MultinomialNB Classifier')
plt.legend(loc="lower right")
plt.savefig("MultinomialNB_ROC_Curve.png", dpi=300, bbox_inches="tight")
plt.show()