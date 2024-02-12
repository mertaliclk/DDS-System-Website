#!/usr/bin/env python
# coding: utf-8

# In[12]:


import cv2
import imutils
from imutils import face_utils
import dlib
import os
from scipy.spatial import distance
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import pygame
import numpy as np
import math


pygame.mixer.init()
pygame.mixer.music.load('alarm.mp3')


def EyeAR(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear


def MouthAR(mouth):
	A = distance.euclidean(mouth[0], mouth[6])
	B = distance.euclidean(mouth[2], mouth[10])
	C = distance.euclidean(mouth[4], mouth[8])
	mar = (B + C) / (2.0 * A)
	return mar


def calculate_slope_and_angle(left_eye, right_eye):
    mean_xl = np.mean(left_eye[:, 0])
    mean_yl = np.mean(left_eye[:, 1])
    mean_xr = np.mean(right_eye[:, 0])
    mean_yr = np.mean(right_eye[:, 1])
    pointl = (mean_xl, mean_yl)
    pointr = (mean_xr, mean_yr)
    slope = (pointr[1] - pointl[1]) / (pointr[0] - pointl[0])
    angle_radians = math.atan(slope)
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees

def operator_model(face_part, frame, model):
    min_x = np.min(face_part[:, 0])  # Minimum X value
    max_x = np.max(face_part[:, 0])  # Maximum X value
    min_y = np.min(face_part[:, 1])  # Minimum Y value
    max_y = np.max(face_part[:, 1])  # Maximum Y value
    cropped_img = frame[min_x:max_x, min_y:max_y]
    cropped_img = cv2.cvtColor(cropped_img,cv2.COLOR_BGR2GRAY)
    cropped_img = cv2.resize(cropped_img,(32,32))
    cropped_img= cropped_img/255
    cropped_img=  cropped_img.reshape(32,32,-1)
    cropped_img = np.expand_dims(cropped_img,axis=0)
    img_pred = model.predict_classes(cropped_img)
    if(img_pred[0]==1):
        return 1
    else:
        return 0

status_message = ""
status1= "You are okay"
status2= "You look tired!"
status3= "You are drowsy!!"
status4= "Wake up!!!"
current_status = 1


eye_threshold = 0.25
mouth_threshold = 0.50
count_eye_close = 0
count_mouth_open = 0
check_blink = 0
check_yawn = 0
total_blink = 0
total_yawn = 0
iteration_no = 0
check_tired_blink = 0


def update_eye_values(ear, eye_threshold):         #Add check_eye too for CNN model
    global count_eye_close, check_blink, total_blink
    if ear < eye_threshold: # or check_eye == 0
        count_eye_close+= 1
        check_blink = 1
    else:
        count_eye_close = 0
        if check_blink ==1:
            check_blink = 0
            total_blink+=1


def update_mouth_values(mouar, mouth_threshold):         #Add check_mouth too for CNN model
    global count_mouth_open, check_yawn, total_yawn
    if mouar > mouth_threshold: # or check_mouth == 1
        count_mouth_open+= 1
        check_yawn = 1
    else:
        count_mouth_open = 0
        if check_yawn == 1:
            check_yawn = 0
            total_yawn+=1


def update_alarm(current_status):
    if (current_status != 4) and (pygame.mixer.music.get_busy() == True):
        pygame.mixer.music.stop()
    elif (current_status == 4) and (pygame.mixer.music.get_busy() == False):
        pygame.mixer.music.play(-1)


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
#model_eye = load_model('model_eye.h5')
#model_mouth = load_model('model_mouth.h5')
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

#vs= VideoStream(usePiCamera=True).start()
cap=cv2.VideoCapture(0)
while True:
    _, frame=cap.read()
    frame = imutils.resize(frame, width=750)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 0)
    iteration_no+=1
    total_face_no = len(faces)
    face_message = str(total_face_no) + " face(s) detected"
    cv2.putText(frame, face_message, (30, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    if (iteration_no >= 3000) and total_blink < 10:
        check_tired_blink  = 1
    if iteration_no >= 5000:
        iteration_no = 0
        check_tired_blink = 0
    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)
        
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        mouth = shape[mStart:mEnd]


        #check_left = operator_model(leftEye, frame, model_eye)
        #check_right = operator_model(rightEye, frame, model_eye)
        #check_mouth = operator_model(mouth, frame, model_mouth)
        #check_eye = check_left + check_right
        
        leftEAR = EyeAR(leftEye)
        rightEAR = EyeAR(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        mouar = MouthAR(mouth)
        
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        mouthHull = cv2.convexHull(mouth)
        
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
        
        headdegree = calculate_slope_and_angle(leftEye, rightEye)


        if (headdegree > 20) or (headdegree < -20) or (count_eye_close >=50):    
            status_message = status4
            current_status = 4          
            update_alarm(current_status)
            update_eye_values(ear, eye_threshold)        #Add check_eye too for CNN model
            update_mouth_values(mouar, mouth_threshold)         #Add check_mouth too for CNN model


        
        elif (count_mouth_open >= 20 ) or (count_eye_close >=20):
            status_message = status3
            current_status = 3       
            update_alarm(current_status)
            update_eye_values(ear, eye_threshold)         #Add check_eye too for CNN model
            update_mouth_values(mouar, mouth_threshold)         #Add check_mouth too for CNN model


        
        elif total_yawn >= 10 or  check_tired_blink == 1:            
            status_message = status2
            current_status = 2       
            update_alarm(current_status)
            update_eye_values(ear, eye_threshold)         #Add check_eye too for CNN model
            update_mouth_values(mouar, mouth_threshold)         #Add check_mouth too for CNN model


             
        else:
            status_message = status1
            current_status = 1    
            update_alarm(current_status)
            update_eye_values(ear, eye_threshold)         #Add check_eye too for CNN model
            update_mouth_values(mouar, mouth_threshold)         #Add check_mouth too for CNN model


        if -20 < headdegree < 20:
            degree_message = "Vertical: " + str(abs(int(headdegree))) + " degrees"

        elif headdegree >= 20:
            degree_message = "Left tilt: " + str(abs(int(headdegree))) + " degrees"

        else: 
            degree_message = "Right tilt: " + str(abs(int(headdegree))) + " degrees"

        cv2.putText(frame, degree_message, (30, 450),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (52, 210, 235), 3)

        
        iteration_message = "Iteration no: " + str(iteration_no) 
        cv2.putText(frame, iteration_message, (550, 400),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 247, 82), 3) 

        blink_message = "Total blink no: " + str(total_blink) 
        cv2.putText(frame, blink_message, (550, 450),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 247, 82), 3)

        yawn_message = "Total yawn no: " + str(total_yawn) 
        cv2.putText(frame, yawn_message, (550, 500),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 247, 82), 3)

        
        if current_status ==1:
            cv2.putText(frame, status_message, (40, 100),cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 4)
        elif current_status ==2 or current_status == 3:
            cv2.putText(frame, status_message, (40, 100),cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 4)
        else:
            cv2.putText(frame, status_message, (40, 100),cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 4)


    cv2.imshow("Drowsiness detection system", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("f"):
        break
cv2.destroyAllWindows()
cap.release() 


# In[ ]:




