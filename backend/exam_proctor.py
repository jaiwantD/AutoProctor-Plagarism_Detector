# import cv2
# import time
# from os import system

# font = cv2.FONT_HERSHEY_SIMPLEX

# # Initialize and start realtime video capture
# cam = cv2.VideoCapture(0)
# cam.set(3, 1280) # set video width
# cam.set(4, 720) # set video height

# def getFaces(img):
#     faces = getFaces.face_detector.detectMultiScale(
#         img_gray,
#         scaleFactor = 1.2,
#         minNeighbors = 5,
#         minSize = (getFaces.minW, getFaces.minH),
#        )
#     return faces

# getFaces.face_detector = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml');
# # Define min window size to be recognized as a face
# getFaces.minW = int(0.1*cam.get(3))
# getFaces.minH = int(0.1*cam.get(4))

# def matchFace(img_gray, face):
#     x, y, w, h = face
#     id, loss = matchFace.recognizer.predict(img_gray[y:y+h,x:x+w])
#     return id == 1

# matchFace.recognizer = cv2.face.LBPHFaceRecognizer_create()
# matchFace.recognizer.read('./models/candidate_verification.yml')

# def record_infringement(time_point, nature , img):
#     cv2.imwrite("./Exam_infringement_record/{}_{}.jpg".format(nature, time_point) , img[:])

# def logFaceMismatch(img, face):
#     draw_rectangle(img, face)
#     record_infringement(time.time(), "FaceMismatch", img)

#     # Visualization.
#     display_status(img, "FACE MISMATCH")


# def logMultipleFacesDetected(img, faces):
#     for face in faces: 
#         draw_rectangle(img, face)

#     record_infringement(time.time(), "MultipleFacesDetected", img)

#     # Visualization.
#     display_status(img, "MULTIPLE FACES DETECTED")



# def logNoFaceDetected(img):
#     record_infringement(time.time(), "NoFaceFound", img)

#     # Visualization.
#     display_status(img, "NO FACE DETECTED")

# def logNormalBehaviour(img, face):

#     # Visualization.
#     green = (0,204,0)
#     draw_rectangle(img, face, green)
#     display_status(img, "CLEAR", green)

# def draw_rectangle(img, face, color=(0,0,255)):
#     x, y, w, h = face
#     cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)

# def display_status(img, status, color=(0,0,255)):
#     cv2.putText(img, status, (20, 50),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)





# print("[INFO] Enter the proctoring period(seconds) -- ")
# period = int(input())
# start = time.time()

# while time.time() < period + start:
#     ret, img = cam.read()
#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     faces = getFaces(img_gray)

#     if(len(faces) == 0):
#         logNoFaceDetected(img)
#     elif(len(faces) > 1):
#         logMultipleFacesDetected(img, faces)
#     elif matchFace(img_gray, faces[0]) == False:
#         logFaceMismatch(img, faces[0])
#     else:
#         logNormalBehaviour(img, faces[0])

#     # Visualization.
#     # Display processed images as a vid
#     cv2.imshow('camera',img) 

#     k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
#     if k == 27:
#         break

#     time.sleep(0.10)

# # Do a bit of cleanup
# print("\n [INFO] Exiting Program and cleanup stuff")
# cam.release()
# cv2.destroyAllWindows()


# import cv2
# import time

# font = cv2.FONT_HERSHEY_SIMPLEX

# # Initialize and start realtime video capture
# cam = cv2.VideoCapture(0)
# cam.set(3, 1280)  # set video width
# cam.set(4, 720)  # set video height

# # Load Haar cascade classifiers
# face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
# eye_cascade = cv2.CascadeClassifier('./models/haarcascade_eye.xml')

# # Load Face Recognizer
# recognizer = cv2.face.LBPHFaceRecognizer_create()
# recognizer.read('./models/candidate_verification.yml')

# # Define min window size to be recognized as a face
# minW = int(0.1 * cam.get(3))
# minH = int(0.1 * cam.get(4))

# def record_infringement(nature, img):
#     cv2.imwrite(f"./Exam_infringement_record/{nature}_{int(time.time())}.jpg", img)

# def draw_rectangle(img, face, color=(0, 0, 255)):
#     x, y, w, h = face
#     cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

# def display_status(img, status, color=(0, 0, 255)):
#     cv2.putText(img, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

# def process_frame(img):
#     img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(img_gray, 1.2, 5, minSize=(minW, minH))
    
#     if len(faces) == 0:
#         display_status(img, "NO FACE DETECTED")
#         record_infringement("NoFaceFound", img)
#     elif len(faces) > 1:
#         for face in faces:
#             draw_rectangle(img, face)
#         display_status(img, "MULTIPLE FACES DETECTED")
#         record_infringement("MultipleFacesDetected", img)
#     else:
#         x, y, w, h = faces[0]
#         face_roi_gray = img_gray[y:y + h, x:x + w]
        
#         id, loss = recognizer.predict(face_roi_gray)
#         if id != 1:
#             draw_rectangle(img, faces[0])
#             display_status(img, "FACE MISMATCH")
#             record_infringement("FaceMismatch", img)
#         else:
#             eyes = eye_cascade.detectMultiScale(face_roi_gray)
#             if len(eyes) == 0:
#                 draw_rectangle(img, faces[0])
#                 display_status(img, "NO EYES DETECTED")
#                 record_infringement("NoEyesDetected", img)
#             else:
#                 for (ex, ey, ew, eh) in eyes:
#                     cv2.rectangle(img[y:y + h, x:x + w], (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
#                 draw_rectangle(img, faces[0], (0, 204, 0))
#                 display_status(img, "CLEAR", (0, 204, 0))

# while True:
#     ret, img = cam.read()
#     if not ret:
#         break
    
#     process_frame(img)
#     cv2.imshow('Proctoring System', img)
    
#     if cv2.waitKey(10) & 0xFF == 27:  # Press 'ESC' to exit
#         break

# cam.release()
# cv2.destroyAllWindows()


import cv2
import time
import sys  # Import sys for stdout flushing

font = cv2.FONT_HERSHEY_SIMPLEX

cam = cv2.VideoCapture(0)
cam.set(3, 1280)  
cam.set(4, 720)  

face_cascade = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('./models/haarcascade_eye.xml')

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('./models/candidate_verification.yml')

minW = int(0.1 * cam.get(3))
minH = int(0.1 * cam.get(4))

def record_infringement(nature, img):
    cv2.imwrite(f"./Exam_infringement_record/{nature}_{int(time.time())}.jpg", img)

def draw_rectangle(img, face, color=(0, 0, 255)):
    x, y, w, h = face
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

def display_status(img, status, color=(0, 0, 255)):
    cv2.putText(img, status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    print(status)  # <-- Print status to stdout
    sys.stdout.flush()  # <-- Ensure output is sent immediately

def process_frame(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(img_gray, 1.2, 5, minSize=(minW, minH))
    
    if len(faces) == 0:
        display_status(img, "NO FACE DETECTED")
        record_infringement("NoFaceFound", img)
    elif len(faces) > 1:
        for face in faces:
            draw_rectangle(img, face)
        display_status(img, "MULTIPLE FACES DETECTED")
        record_infringement("MultipleFacesDetected", img)
    else:
        x, y, w, h = faces[0]
        face_roi_gray = img_gray[y:y + h, x:x + w]
        
        id, loss = recognizer.predict(face_roi_gray)
        if id != 1:
            draw_rectangle(img, faces[0])
            display_status(img, "FACE MISMATCH")
            record_infringement("FaceMismatch", img)
        else:
            eyes = eye_cascade.detectMultiScale(face_roi_gray)
            if len(eyes) == 0:
                draw_rectangle(img, faces[0])
                display_status(img, "NO EYES DETECTED")
                record_infringement("NoEyesDetected", img)
            else:
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(img[y:y + h, x:x + w], (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                draw_rectangle(img, faces[0], (0, 204, 0))
                display_status(img, "CLEAR", (0, 204, 0))

while True:
    ret, img = cam.read()
    if not ret:
        break
    
    process_frame(img)
    cv2.imshow('Proctoring System', img)
    
    if cv2.waitKey(10) & 0xFF == 27:  
        break

cam.release()
cv2.destroyAllWindows()
