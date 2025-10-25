import json
import pickle
import numpy as np
import tensorflow as tf
import nltk
from nltk.stem import WordNetLemmatizer
import random
import os

def train_model():
    lemmatizer = WordNetLemmatizer()

    # Load intents
    intents_path = os.path.join(os.path.dirname(__file__), '../../data/intents.json')
    with open(intents_path, 'r') as file:
        intents = json.load(file)

    words = []
    classes = []
    documents = []
    ignore_letters = ['!', '?', ',', '.']

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))

    # Create training data
    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = []
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1
        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training, dtype=object)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    # Build model
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(64, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(len(train_y[0]), activation='softmax'))

    sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    # Train model
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

    # Save model and data
    model_dir = os.path.join(os.path.dirname(__file__), '../../data')
    os.makedirs(model_dir, exist_ok=True)

    model.save(os.path.join(model_dir, 'chatbot_model.h5'), hist)

    with open(os.path.join(model_dir, 'words.pkl'), 'wb') as f:
        pickle.dump(words, f)
    with open(os.path.join(model_dir, 'classes.pkl'), 'wb') as f:
        pickle.dump(classes, f)

    print("Model trained and saved!")

if __name__ == "__main__":
    train_model()
