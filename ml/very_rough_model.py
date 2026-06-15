#!/usr/bin/env python3

# currently commenting out tf as it makes stuff take forever to compile (We love JIT)

from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
from sklearn.utils import shuffle

binary_classes = {
                    "object_binary" : {"object": 0, "no_object": 1},
                    "noise_vs_data_binary" : {"noise": 0, "data": 1}
                  }

BATCH_SIZE = 16
EPOCHS = 16
NSAMP = (128, 2813, 1) #TODO
KERNEL_SIZE = 3

def create_model():
    model = keras.Sequential()
    model.add(layers.Input(shape=NSAMP))
    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=3))
    model.add(layers.Dropout(0.25))

    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=3))
    model.add(layers.Dropout(0.25)) 

    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.Conv2D(16, kernel_size = KERNEL_SIZE, activation='relu'))
    model.add(layers.MaxPooling2D(pool_size=3))
    model.add(layers.Dropout(0.25))

    model.add(layers.GlobalAveragePooling2D())
    model.add(layers.Dense(16, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation='sigmoid'))

    print("compiling model...")

    model.compile(loss=keras.losses.binary_crossentropy, 
                  optimizer=keras.optimizers.Adam(), metrics = ['accuracy']
                  )

    return model

def fit_model(model, x_train, y_train, verbose: int = 0):
    print("beginning to fit model...")
    history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose = verbose)
    return history

def score_model(model, x_test, y_test, verbose: int = 0):
    print("beginning to score model")
    return model.evaluate(x_test, y_test, verbose=verbose)

def save_model(model, file_dir: str):
    model.save(file_dir)


if __name__ == "__main__":
    
    print("Loading np arrays...")
    print("Loading data array...")
    train_data   = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_noise_vs_sound_spectros.npy")
    
    print("Loaded data. Now loading labels...")
    train_labels = np.load("c:/Users/Tyler/Desktop/SURI-Project/ml/npy_files/distance_noise_vs_sound_labels.npy")

    
    print("shuffling arrays...")
    train_data, train_labels = shuffle(train_data, train_labels)

    train_labels = train_labels.astype("float32")

    split_point = (int)(len(train_labels) * .8)

    print("creating test arrays as splice of train arrays...")

    test_data   = train_data[split_point:]
    test_labels = train_labels[split_point:]
    
    train_data   = train_data[:split_point]
    train_labels = train_labels[:split_point]
    

    print("creating model...")
    test_model = create_model()

    print("fitting model...")
    history = fit_model(test_model, train_data, train_labels, 1)

    print("scoring model...")
    score = score_model(test_model, test_data, test_labels, 1)
    print("score=%0.3f%%" % (100.0*score[1],))

    if score[1] > .70:
        print("considering model a success... saving")
        save_model(test_model, "first_model.keras")


    else:
        print("model wasn't so hot... do you want to save?")
        user_input = input("Type yes to save: ")
        if user_input.lower() in ["yes", "y"]:
             save_model(test_model, "first_model.keras")


