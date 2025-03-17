# # import cv2
# # from os import system



# # # Open camera to capture video
# # cam = cv2.VideoCapture(0)

# # cam.set(3, 1280) # set video width
# # cam.set(4, 720)  # set video height

# # # Path to inbuilt face detection model

# # cascadePath = r'C:\Users\kishore giri\Desktop\cpp procted website\AutoProctor-Plagarism_Detector\backend\models\haarcascade_frontalface_default.xml'
# # face_detector = cv2.CascadeClassifier(cascadePath)

# # print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# # # Count of the number of pics clicked
# # count = 0

# # while(True):

# #     ret, img = cam.read()
# #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# #     faces = face_detector.detectMultiScale(gray, 1.3, 5)

# #     #x, y is the top left coordinate of the face and w and h are wight and height of the rectangle containing the face
# #     for (x,y,w,h) in faces:
# #         # Draws a rectangle around the image
# #         cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     

# #         # Save the captured image into the datasets folder
# #         cv2.imwrite("./dataset/true_labels/1." + str(count) + ".jpg", gray[y:y+h,x:x+w])

# #         # increment num of pics clicked
# #         count += 1

# #     # Display processed pic
# #     cv2.imshow('image', img)

# #     k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
# #     if k == 27:
# #         break

# #     elif count >= 45: # Take 50 face sample and stop video
# #          break

# # # Do a bit of cleanup
# # cam.release()
# # cv2.destroyAllWindows()

# # print("\n [INFO] Dataset created. Training Model.")


# # import numpy as np
# # from PIL import Image
# # import os

# # # Path for face image database
# # recognizer = cv2.face.LBPHFaceRecognizer_create()

# # def getImagesAndLabels():

# #     def getImagePaths(dir_path):
# #         return [os.path.join(dir_path,f) for f in os.listdir(dir_path)]     

# #     # List comprehension to generate a list of all image paths
# #     otherImagePaths = getImagePaths('dataset/false_labels')
# #     candidateImagePaths = getImagePaths('dataset/true_labels')

# #     faceSamples=[]
# #     ids = []

# #     def collectImageAndIds(imagePaths):
# #         for imagePath in imagePaths:
# #             PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
# #             img_numpy = np.array(PIL_img,'uint8')
# #             # Extracts the image id from its file name.
# #             id = int(os.path.split(imagePath)[-1].split(".")[0])
# #             faceSamples.append(img_numpy)
# #             ids.append(id)

# #     collectImageAndIds(otherImagePaths)
# #     collectImageAndIds(candidateImagePaths)

# #     return faceSamples,ids
# # # function to get the images and label data


# # print("\n [INFO] Mapping face. It will take a few seconds. Wait ...")

# # faces,ids = getImagesAndLabels()
# # recognizer.train(faces, np.array(ids))

# # # Save the model into trainer/trainer.yml
# # recognizer.write('models/candidate_verification.yml') 

# # print("\n [INFO] Face mapped. Exiting Program")
import cv2
import numpy as np
from PIL import Image
import os
import sys

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create absolute paths for all resources
cascade_path = os.path.join(script_dir, "models", "haarcascade_frontalface_default.xml")
true_labels_dir = os.path.join(script_dir, "dataset", "true_labels")
false_labels_dir = os.path.join(script_dir, "dataset", "false_labels")
model_output_path = os.path.join(script_dir, "models", "candidate_verification.yml")

# Make sure directories exist
os.makedirs(true_labels_dir, exist_ok=True)
os.makedirs(false_labels_dir, exist_ok=True)
os.makedirs(os.path.dirname(model_output_path), exist_ok=True)

# Check if the Haar cascade file exists
if not os.path.exists(cascade_path):
    print(f"Error: Haar cascade file not found at {cascade_path}")
    sys.exit(1)

# Initialize face detector
face_detector = cv2.CascadeClassifier(cascade_path)
if face_detector.empty():
    print("Error: Failed to load Haar cascade classifier")
    sys.exit(1)

print("\n[INFO] Initializing face capture. Look at the camera and wait...")

# Try multiple camera indices
cam = None
for camera_index in range(3):  # Try camera 0, 1, and 2
    cam = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if cam.isOpened():
        print(f"Successfully opened camera {camera_index}")
        break
    else:
        print(f"Failed to open camera {camera_index}")

# Check if any camera was opened
if cam is None or not cam.isOpened():
    print("Error: Could not open any camera. Please check your camera connection and permissions.")
    sys.exit(1)

cam.set(3, 1280)  # set video width
cam.set(4, 720)   # set video height

# Count of the number of pics clicked
count = 0

try:
    while True:
        ret, img = cam.read()
        if not ret or img is None:
            print("Failed to capture image from camera")
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        
        # x, y is the top left coordinate of the face and w and h are width and height of the rectangle containing the face
        for (x, y, w, h) in faces:
            # Draws a rectangle around the image
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Save the captured image into the datasets folder
            save_path = os.path.join(true_labels_dir, f"1.{count}.jpg")
            cv2.imwrite(save_path, gray[y:y+h, x:x+w])
            
            # increment num of pics clicked
            count += 1
        
        # Display processed pic
        cv2.imshow('image', img)
        
        k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        
        elif count >= 20:  # Take 45 face samples and stop video
            break
except Exception as e:
    print(f"Error during image capture: {e}")
finally:
    # Do a bit of cleanup
    if cam is not None:
        cam.release()
    cv2.destroyAllWindows()

print("\n[INFO] Dataset created. Training Model.")

# Path for face image database
try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
except AttributeError:
    # In some versions of OpenCV, the face module needs to be explicitly imported
    print("Trying alternative method to create face recognizer...")
    recognizer = cv2.face_LBPHFaceRecognizer.create()

def getImagesAndLabels():
    def getImagePaths(dir_path):
        if not os.path.exists(dir_path):
            print(f"Warning: Directory {dir_path} does not exist. Creating it.")
            os.makedirs(dir_path, exist_ok=True)
            return []
        return [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    # List comprehension to generate a list of all image paths
    otherImagePaths = getImagePaths(false_labels_dir)
    candidateImagePaths = getImagePaths(true_labels_dir)
    
    if not candidateImagePaths:
        print(f"Warning: No images found in {true_labels_dir}")
    if not otherImagePaths:
        print(f"Warning: No images found in {false_labels_dir}")
    
    faceSamples = []
    ids = []
    
    def collectImageAndIds(imagePaths):
        for imagePath in imagePaths:
            try:
                PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
                img_numpy = np.array(PIL_img, 'uint8')
                # Extracts the image id from its file name.
                id = int(os.path.split(imagePath)[-1].split(".")[0])
                faceSamples.append(img_numpy)
                ids.append(id)
            except Exception as e:
                print(f"Error processing image {imagePath}: {e}")
    
    collectImageAndIds(otherImagePaths)
    collectImageAndIds(candidateImagePaths)
    
    return faceSamples, ids  # function to get the images and label data

print("\n[INFO] Mapping face. It will take a few seconds. Wait...")

try:
    faces, ids = getImagesAndLabels()
    
    if len(faces) == 0 or len(ids) == 0:
        print("Error: No face samples found. Cannot train model.")
        sys.exit(1)
        
    recognizer.train(faces, np.array(ids))
    
    # Save the model into trainer/trainer.yml
    recognizer.write(model_output_path)
    print(f"\n[INFO] Face mapped. Model saved to {model_output_path}")
except Exception as e:
    print(f"Error during model training: {e}")



