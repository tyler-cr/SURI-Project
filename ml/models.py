#!/usr/bin/env python3

# currently commenting out tf as it makes stuff take forever to compile (We love JIT)

from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
from sklearn.utils import shuffle

import metrics as m

binary_classes = {
                    "object_binary" : {"object": 0, "no_object": 1},
                    "noise_vs_data_binary" : {"noise": 0, "data": 1}
                  }

BATCH_SIZE = 16
EPOCHS = 16
NSAMP = (1025, 1292, 1) #TODO: Automate this
KERNEL_SIZE = 3

def create_model(shape: tuple[int, int, int] = NSAMP, 
                 filter_count: int = 32, 
                 kernel_size: int = KERNEL_SIZE,
                 pool_size: int = 3,
                 output_type: str = "sigmoid",
                 label_count: int = 1):
    """
    Constructs and compiles a sequential CNN model for binary classification.
    
    The architecture consists of three blocks of Conv2D layers with MaxPooling 
    and Dropout, followed by GlobalAveragePooling, Dense layers, and a sigmoid 
    output. Optimized for Adam with binary crossentropy loss.
    
    Returns:
        keras.Model: Compiled Keras Sequential model ready for training.
    """

    model = keras.Sequential()
    model.add(layers.Input(shape=shape))
    model.add(layers.Conv2D(filter_count, kernel_size = (1,9), activation='relu'))
    model.add(layers.Conv2D(filter_count, kernel_size = kernel_size, activation='relu'))
    model.add(layers.Conv2D(filter_count, kernel_size = kernel_size, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=pool_size))
    model.add(layers.Dropout(0.25))

    model.add(layers.Conv2D(2*filter_count, kernel_size = (1,9), activation='relu'))
    model.add(layers.Conv2D(2*filter_count, kernel_size = kernel_size, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=pool_size))
    model.add(layers.Dropout(0.25)) 

    model.add(layers.Conv2D(4*filter_count, kernel_size = (1,9), activation='relu'))
    model.add(layers.Conv2D(4*filter_count, kernel_size = kernel_size, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=pool_size))
    model.add(layers.Dropout(0.25))

    model.add(layers.GlobalMaxPooling2D())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dropout(0.5))

    # this should really just be either sigmoid or softmax. Maybe there are usecases for others
    model.add(layers.Dense(label_count, activation=output_type)) 

    print("compiling model...")

    if label_count == 1:
        loss = keras.losses.BinaryCrossentropy()
    else:
        loss = keras.losses.SparseCategoricalCrossentropy()

    model.compile(loss=loss, #TODO: loss type is dependent on how many labels...
                  optimizer=keras.optimizers.Adam(), metrics = ['accuracy'],
                  )

    return model

def fit_model(model, x_train, y_train, verbose: int = 0):
    """
    Trains the provided model on the given dataset.
    
    Args:
        model (keras.Model): The compiled model to train.
        x_train (np.ndarray): Training input data.
        y_train (np.ndarray): Training labels (binary).
        verbose (int): Verbosity mode for training logs (0=silent).
        
    Returns:
        tf.keras.callbacks.History: Object containing training history metrics.
    """
    print("beginning to fit model...")

    callback = keras.callbacks.EarlyStopping(monitor='val_loss',
                                             patience=2,
                                             start_from_epoch=4,
                                             verbose=verbose,
                                             restore_best_weights=True
                                             )

    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose = verbose, callbacks = [callback], validation_split=0.1)

    print(f"Total epochs called; {len(history.history['loss'])}\n")
    return history

def score_model(model, x_test, y_test, verbose: int = 0):
    """
    Evaluates the model's performance on test data.
    
    Args:
        model (keras.Model): The trained model to evaluate.
        x_test (np.ndarray): Test input data.
        y_test (np.ndarray): Test labels.
        verbose (int): Verbosity mode for evaluation logs.
        
    Returns:
        float: List containing [loss, accuracy] on the test set.
    """
    print("beginning to score model...")
    return model.evaluate(x_test, y_test, verbose=verbose)

def save_model(model, file_dir: str):
    """
    Saves the model to the specified file path in Keras format.
    
    Args:
        model (keras.Model): The model to persist to disk.
        file_dir (str): Destination filepath (e.g., 'model.keras').
    """
    print("saving model...")
    model.save(file_dir)


if __name__ == "__main__":

    print("loading labels and data...")
    training_labels = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_frequency_checking_train_labels.npy").astype(np.int32)
    training_data = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_frequency_checking_train_data.npy").astype(np.float32)

    #testing_labels = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_frequency_checking_test_labels.npy")
    #testing_data = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_frequency_checking_test_data.npy")

    print("Creating model and fitting. Be patient!")
    model = create_model(output_type="softmax", label_count=3)
    history = fit_model(model, training_data, training_labels, 1)
    save_model(model, file_dir="[toy]frequency_checking.keras")

    print("maybe run tests now")


    # if score[1] > .70:
    #     print("considering model a success... saving")
    #     save_model(test_model, "first_model.keras")


    # else:
    #     print("model wasn't so hot... do you want to save?")
    #     user_input = input("Type yes to save: ")
    #     if user_input.lower() in ["yes", "y"]:
    #          save_model(test_model, "first_model.keras")


