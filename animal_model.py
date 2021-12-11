import keras
import tensorflow as tf
import cv2
import numpy as np

model = keras.models.load_model('model.h5')
animals = {0: 'Cats', 1: 'Dogs', 2: 'Other'}


def classifyAnimal(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (64, 64))/ 255
    image = image.reshape(-1, 64, 64, 3)
    result = np.argmax(model(image))
    print(animals[result])
    print(result)
