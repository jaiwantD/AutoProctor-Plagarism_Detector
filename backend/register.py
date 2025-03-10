import cv2
from os import system



# Open camera to capture video
cam = cv2.VideoCapture(0)

cam.set(3, 1280) # set video width
cam.set(4, 720)  # set video height

# Path to inbuilt face detection model

cascadePath = 'models/haarcascade_frontalface_default.xml'
face_detector = cv2.CascadeClassifier(cascadePath)

print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# Count of the number of pics clicked
count = 0

while(True):

    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    #x, y is the top left coordinate of the face and w and h are wight and height of the rectangle containing the face
    for (x,y,w,h) in faces:
        # Draws a rectangle around the image
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     

        # Save the captured image into the datasets folder
        cv2.imwrite("./dataset/true_labels/1." + str(count) + ".jpg", gray[y:y+h,x:x+w])

        # increment num of pics clicked
        count += 1

    # Display processed pic
    cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

    elif count >= 45: # Take 50 face sample and stop video
         break

# Do a bit of cleanup
cam.release()
cv2.destroyAllWindows()

print("\n [INFO] Dataset created. Training Model.")


import numpy as np
from PIL import Image
import os

# Path for face image database
recognizer = cv2.face.LBPHFaceRecognizer_create()

def getImagesAndLabels():

    def getImagePaths(dir_path):
        return [os.path.join(dir_path,f) for f in os.listdir(dir_path)]     

    # List comprehension to generate a list of all image paths
    otherImagePaths = getImagePaths('dataset/false_labels')
    candidateImagePaths = getImagePaths('dataset/true_labels')

    faceSamples=[]
    ids = []

    def collectImageAndIds(imagePaths):
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')
            # Extracts the image id from its file name.
            id = int(os.path.split(imagePath)[-1].split(".")[0])
            faceSamples.append(img_numpy)
            ids.append(id)

    collectImageAndIds(otherImagePaths)
    collectImageAndIds(candidateImagePaths)

    return faceSamples,ids
# function to get the images and label data


print("\n [INFO] Mapping face. It will take a few seconds. Wait ...")

faces,ids = getImagesAndLabels()
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write('models/candidate_verification.yml') 

print("\n [INFO] Face mapped. Exiting Program")