#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import os


# In[ ]:


feature_type = 0 #If it is for eyes, use 0 if it is for mouth use 1


# In[ ]:


Traindataset = []
Testdataset = []
traindirect = "Traindataset/"
testdirect = "Testdataset/"
difftypes = ["Closed", "Opened"] #Arrange according to mouth or eyes since for eyes closing is unwanted while for mouth opening is unwanted


# In[ ]:


def preparedataset(directory, dataset):
    for catalog in difftypes:
        path = os.path.join(directory,catalog)
        class_type = difftypes.index(catalog)
        for sample_image in os.listdir(path):
            img_array = cv2.imread(os.path.join(path,sample_image), cv2.IMREAD_GRAYSCALE)
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            updated_arr = cv2.resize(img_rgb, (32, 32))
            dataset.append([updated_arr,class_type])


# In[ ]:


preparedataset(traindirect, Traindataset)
preparedataset(testdirect, Testdataset)


# In[ ]:


rnd.shuffle(Traindataset)
rnd.shuffle(Testdataset)


# In[ ]:


X_train = []
X_test = []
Y_train = []
Y_test = []


# In[ ]:


def createXY(xset,yset, tra_or_te):
    for features, label in tra_or_te:
        xset.append(features)
        yset.append(label)


# In[ ]:


createXY(X_train, Y_train,Traindataset)
createXY(X_test, Y_test, Testdataset)


# In[ ]:


X_train = np.array(X_train).reshape(-1, 32, 32, 3)
X_train = X_train / 255.0
Y_train = np.array(Y_train)

X_test = np.array(X_test).reshape(-1, 32, 32, 3)
X_test = X_test / 255.0
Y_test = np.array(Y_test)


# In[ ]:


model = tf.keras.applications.mobilenet.MobileNet()
model.summary()


# In[ ]:


startingpoint = model.layers[0].input
endingpoint = model.layers[-4].input


# In[ ]:


flattening = layers.Flatten()(endingpoint)
result_model = layers.Dense(1)(flattening)
result_model = layers.Activation('sigmoid')(result_model)


# In[ ]:


final_model = keras.Model(inputs = startingpoint, outputs = endingpoint)
final_model.compile(loss="binary_crossentropy", optimizer = "adam", metrics = ["accuracy"])
final_model.fit(X_train, Y_train, epochs=1, validation_data=(X_test, Y_test))


# In[ ]:


if feature_type == 0:
    final_model.save("eye_model.h5")
elif feature_type == 1:
    final_model.save("mouth_model.h5")

