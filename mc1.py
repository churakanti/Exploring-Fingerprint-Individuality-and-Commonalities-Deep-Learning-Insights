
import tensorflow as tf
import numpy as np
import tensorflow.keras

import os
from google.colab import drive
drive.mount('/content/drive', force_remount=True)

base_dir = '/content/drive/MyDrive/FPD/FPD_MC1_ALL'

train_dir = os.path.join(base_dir, 'train')
vali_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')

from tensorflow.keras.utils import image_dataset_from_directory
# shuffle is True by default
train_dataset = image_dataset_from_directory(
    train_dir,
    image_size=(180, 180),
    batch_size=32)
validation_dataset = image_dataset_from_directory(
    vali_dir,
    image_size=(180, 180),
    batch_size=20) # was 32
test_dataset = image_dataset_from_directory(
    test_dir,
    image_size=(180, 180),
    batch_size=10, # was 32
    shuffle=True)

from tensorflow import keras
from keras import layers

inputs = keras.Input(shape=(180, 180, 3))
x = layers.Rescaling(1./255)(inputs)
x = layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.MaxPooling2D(pool_size=2)(x)
x = layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
x = layers.Flatten()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(17, activation="softmax")(x)

CNN_model = tf.keras.Model(inputs, outputs)

CNN_model.compile(optimizer="adam",
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
CNN_model.summary()

callbacks = [
    tf.keras.callbacks.ModelCheckpoint("best_model.h5", monitor='val_accuracy', save_best_only=True),
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=10),
    tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.1, patience=5, min_lr=1e-6)
]

# Initialize lists to store results
results = []
histories = []

# Fit the model
history = CNN_model.fit(train_dataset,batch_size=64, epochs=30, validation_data=validation_dataset, callbacks=callbacks)
# Store history
histories.append(history)
# Evaluate the model
evaluation = CNN_model.evaluate(test_dataset)

# Collect evaluation metrics
accuracy = evaluation[1]  # Assuming accuracy is the second element in the evaluation result

from sklearn.metrics import confusion_matrix

# Initialize lists for true labels and predicted labels
true_labels = []
pred_labels = []

# Iterate over the test dataset to collect true labels and predicted labels
for data, label in test_dataset:
    true_labels.append(label.numpy())  # Append true label
    pred_labels.append(np.argmax(CNN_model.predict(data), axis=1))  # Append predicted label

# Concatenate true labels and predicted labels into numpy arrays
y_true = np.concatenate(true_labels)
test_pred = np.concatenate(pred_labels)

# Compute confusion matrix
cm = confusion_matrix(y_true=y_true, y_pred=test_pred)
print(cm)

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator # to show all tick labels
fig, ax = plt.subplots(figsize=(5, 5)) # one subplot with size 5x5
ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.3) # alpha make the Blue light blue
ax.yaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
ax.xaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(x=j, y=i,s=cm[i, j], va='center', ha='center', size='medium')

plt.xlabel('Predictions', fontsize=16)
plt.ylabel('Actuals', fontsize=16)
plt.title('Confusion Matrix', fontsize=20)
plt.show()

from sklearn.metrics import precision_score, recall_score, f1_score

precision = precision_score(y_true, test_pred, average='weighted')
recall = recall_score(y_true, test_pred, average='weighted')
f1 = f1_score(y_true, test_pred, average='weighted')

results.append({'Model': "CNN", 'Accuracy': accuracy, 'F1-Score': f1, 'Precision': precision, 'Recall': recall})

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

# Input layer remains the same
inputs = tf.keras.Input(shape=(180, 180, 3))

x = tf.keras.applications.resnet.preprocess_input(inputs)

# Use a pre-trained model as the base
x = tf.keras.applications.ResNet50(include_top=False)(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(17, activation='softmax')(x)

# Create the model
Resnet_model = tf.keras.Model(inputs, outputs)

# Compile the model with the same parameters
Resnet_model.compile(loss='sparse_categorical_crossentropy', optimizer="adam", metrics=['accuracy'])

Resnet_model.summary()

# Fit the model
history = Resnet_model.fit(train_dataset,batch_size=64, epochs=30, validation_data=validation_dataset, callbacks=callbacks)
# Store history
histories.append(history)
# Evaluate the model
evaluation = Resnet_model.evaluate(test_dataset)

# Collect evaluation metrics
accuracy = evaluation[1]  # Assuming accuracy is the second element in the evaluation result

# Initialize lists for true labels and predicted labels
true_labels = []
pred_labels = []

# Iterate over the test dataset to collect true labels and predicted labels
for data, label in test_dataset:
    true_labels.append(label.numpy())  # Append true label
    pred_labels.append(np.argmax(Resnet_model.predict(data), axis=1))  # Append predicted label

# Concatenate true labels and predicted labels into numpy arrays
y_true = np.concatenate(true_labels)
test_pred = np.concatenate(pred_labels)

# Compute confusion matrix
cm = confusion_matrix(y_true=y_true, y_pred=test_pred)
print(cm)

fig, ax = plt.subplots(figsize=(5, 5)) # one subplot with size 5x5
ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.3) # alpha make the Blue light blue
ax.yaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
ax.xaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(x=j, y=i,s=cm[i, j], va='center', ha='center', size='medium')

plt.xlabel('Predictions', fontsize=16)
plt.ylabel('Actuals', fontsize=16)
plt.title('Confusion Matrix', fontsize=20)
plt.show()

precision = precision_score(y_true, test_pred, average='weighted')
recall = recall_score(y_true, test_pred, average='weighted')
f1 = f1_score(y_true, test_pred, average='weighted')

results.append({'Model': "Rsenet50", 'Accuracy': accuracy, 'F1-Score': f1, 'Precision': precision, 'Recall': recall})

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

# Adding a data augmentation stage and a classifier to the convolutional base
conv_base  = tf.keras.applications.vgg16.VGG16(
    weights="imagenet",
    include_top=False)
conv_base.trainable = False

inputs = tf.keras.Input(shape=(180, 180, 3))
x = tf.keras.applications.vgg16.preprocess_input(inputs)
x = conv_base(x)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
x = layers.Dense(256, activation='relu')(x)

outputs = layers.Dense(17, activation="softmax")(x)

Vgg_model = tf.keras.Model(inputs, outputs)

Vgg_model.compile(loss="sparse_categorical_crossentropy",
              optimizer='adam',
              metrics=["accuracy"])
Vgg_model.summary()

# Fit the model
history = Vgg_model.fit(train_dataset,batch_size=64, epochs=30, validation_data=validation_dataset, callbacks=callbacks)
# Store history
histories.append(history)
# Evaluate the model
evaluation = Vgg_model.evaluate(test_dataset)

# Collect evaluation metrics
accuracy = evaluation[1]  # Assuming accuracy is the second element in the evaluation result

# Initialize lists for true labels and predicted labels
true_labels = []
pred_labels = []

# Iterate over the test dataset to collect true labels and predicted labels
for data, label in test_dataset:
    true_labels.append(label.numpy())  # Append true label
    pred_labels.append(np.argmax(Vgg_model.predict(data), axis=1))  # Append predicted label

# Concatenate true labels and predicted labels into numpy arrays
y_true = np.concatenate(true_labels)
test_pred = np.concatenate(pred_labels)

# Compute confusion matrix
cm = confusion_matrix(y_true=y_true, y_pred=test_pred)
print(cm)

fig, ax = plt.subplots(figsize=(5, 5)) # one subplot with size 5x5
ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.3) # alpha make the Blue light blue
ax.yaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
ax.xaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(x=j, y=i,s=cm[i, j], va='center', ha='center', size='medium')

plt.xlabel('Predictions', fontsize=16)
plt.ylabel('Actuals', fontsize=16)
plt.title('Confusion Matrix', fontsize=20)
plt.show()

precision = precision_score(y_true, test_pred, average='weighted')
recall = recall_score(y_true, test_pred, average='weighted')
f1 = f1_score(y_true, test_pred, average='weighted')

results.append({'Model': "Vgg16", 'Accuracy': accuracy, 'F1-Score': f1, 'Precision': precision, 'Recall': recall})

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

from tensorflow.keras.applications import EfficientNetB1

# Load the pre-trained EfficientNetB1 model without the top classification layer
base_model = EfficientNetB1(weights='imagenet', include_top=False, input_shape=(180, 180, 3))

# Freeze the weights of the pre-trained layers
for layer in base_model.layers:
    layer.trainable = False

# Add a custom classification head
x = layers.GlobalAveragePooling2D()(base_model.output)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(17, activation='softmax')(x)

# Create the final model
EfficientNet_model = tf.keras.Model(inputs=base_model.input, outputs=outputs)

# Compile the model
EfficientNet_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Print model summary
EfficientNet_model.summary()

# Fit the model
history = EfficientNet_model.fit(train_dataset,batch_size=64, epochs=30, validation_data=validation_dataset, callbacks=callbacks)
# Store history
histories.append(history)
# Evaluate the model
evaluation = EfficientNet_model.evaluate(test_dataset)

# Collect evaluation metrics
accuracy = evaluation[1]  # Assuming accuracy is the second element in the evaluation result

# Initialize lists for true labels and predicted labels
true_labels = []
pred_labels = []

# Iterate over the test dataset to collect true labels and predicted labels
for data, label in test_dataset:
    true_labels.append(label.numpy())  # Append true label
    pred_labels.append(np.argmax(EfficientNet_model.predict(data), axis=1))  # Append predicted label

# Concatenate true labels and predicted labels into numpy arrays
y_true = np.concatenate(true_labels)
test_pred = np.concatenate(pred_labels)

# Compute confusion matrix
cm = confusion_matrix(y_true=y_true, y_pred=test_pred)
print(cm)

fig, ax = plt.subplots(figsize=(5, 5)) # one subplot with size 5x5
ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.3) # alpha make the Blue light blue
ax.yaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
ax.xaxis.set_major_locator(MultipleLocator(1))  # to show all tick labels
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(x=j, y=i,s=cm[i, j], va='center', ha='center', size='medium')

plt.xlabel('Predictions', fontsize=16)
plt.ylabel('Actuals', fontsize=16)
plt.title('Confusion Matrix', fontsize=20)
plt.show()

precision = precision_score(y_true, test_pred, average='weighted')
recall = recall_score(y_true, test_pred, average='weighted')
f1 = f1_score(y_true, test_pred, average='weighted')

results.append({'Model': "Efficient", 'Accuracy': accuracy, 'F1-Score': f1, 'Precision': precision, 'Recall': recall})

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

import matplotlib.pyplot as plt

name = ['CNN', 'RESNET50', 'VGG16', 'EfficientNet']
for model_name, history in zip(name, histories):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(len(acc))

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_size_inches(12, 4)

    ax1.plot(epochs, acc, 'bo', label='Training acc')
    ax1.plot(epochs, val_acc, 'b', label='Validation acc')
    ax1.set_title(f'Training and validation accuracy ({model_name})')
    #ax1.set_ylim([0.6, 0.95])
    ax1.legend()

    ax2.plot(epochs, loss, 'bo', label='Training loss')
    ax2.plot(epochs, val_loss, 'b', label='Validation loss')
    #ax2.set_ylim([0.1,0.7]) # To compare with FE1
    ax2.set_title(f'Training and validation loss ({model_name})')
    ax2.legend()

    plt.show()

X_test = []
y_test = []
for images, labels in test_dataset:
    X_test.append(images.numpy())
    y_test.append(labels.numpy())

# Convert lists to numpy arrays
X_test = np.concatenate(X_test)
y_test = np.concatenate(y_test)

from sklearn.metrics import accuracy_score

# Predict probabilities for each model
probs_model1 = CNN_model.predict(X_test)
probs_model2 = Resnet_model.predict(X_test)
probs_model3 = Vgg_model.predict(X_test)
probs_model4 = EfficientNet_model.predict(X_test)

# Define weights for each model
weights = [0.1, 0.2, 0.3, 0.4]

# Combine probabilities from all models with weights
weighted_probs = np.average([probs_model1, probs_model2, probs_model3, probs_model4], axis=0, weights=weights)

# Predict the class with the highest weighted probability
ensemble_predictions = np.argmax(weighted_probs, axis=1)

# Evaluate the accuracy of the ensemble model
accuracy = accuracy_score(y_test, ensemble_predictions)
print("Validation Accuracy:", accuracy)

import seaborn as sns

# Compute confusion matrix
cm = confusion_matrix(y_test, ensemble_predictions)

# Plot confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.title('Confusion Matrix')
plt.show()

precision = precision_score(y_test, ensemble_predictions, average='weighted')
recall = recall_score(y_test, ensemble_predictions, average='weighted')
f1 = f1_score(y_test, ensemble_predictions, average='weighted')

results.append({'Model': "Voting", 'Accuracy': accuracy, 'F1-Score': f1, 'Precision': precision, 'Recall': recall})

print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)

import pandas as pd

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Display results as table
print(df_results)

