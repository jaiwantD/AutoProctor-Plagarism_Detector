# from flask import Flask, render_template, request, jsonify, redirect, url_for
# import subprocess
# import os
# import sys
# import threading
# import time
# import queue

# app = Flask(__name__)

# # Global variables to track process status
# process_status = {
#     "running": False,
#     "completed": False,
#     "success": False,
#     "message_queue": queue.Queue(),
#     "final_message": ""
# }

# def reset_status():
#     """Reset the process status"""
#     process_status["running"] = False
#     process_status["completed"] = False
#     process_status["success"] = False
#     process_status["final_message"] = ""
#     # Clear the queue
#     while not process_status["message_queue"].empty():
#         procesaas_status["message_queue"].get()

# @app.route('/')
# def index():
#     """Render the main page"""
#     # Check if models directory exists
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     model_path = os.path.join(script_dir, "models", "candidate_verification.yml")
#     model_exists = os.path.exists(model_path)
    
#     return render_template('index.html', model_exists=model_exists)

# @app.route('/register', methods=['POST'])
# def register():
#     """Start the registration process"""
#     global process_status
    
#     # Check if process is already running
#     if process_status["running"]:
#         return jsonify({"status": "error", "message": "Registration process is already running"})
    
#     # Reset status
#     reset_status()
    
#     # Set process as running
#     process_status["running"] = True
    
#     # Start the registration process in a background thread
#     thread = threading.Thread(target=run_registration)
#     thread.daemon = True
#     thread.start()
    
#     return jsonify({"status": "started"})

# def run_registration():
#     """Run the registration script"""
#     global process_status
    
#     try:
#         # Get the path to register.py
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         register_script_path = os.path.join(script_dir, "register.py")
        
#         # Check if register.py exists
#         if not os.path.exists(register_script_path):
#             process_status["message_queue"].put("Error: register.py not found")
#             process_status["completed"] = True
#             process_status["running"] = False
#             process_status["success"] = False
#             process_status["final_message"] = "Error: register.py not found"
#             return
        
#         # Add initial message
#         process_status["message_queue"].put("Starting face registration process...")
        
#         # Execute the register.py script
#         process = subprocess.Popen(
#             [sys.executable, register_script_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             bufsize=1,
#             universal_newlines=True
#         )
        
#         # Process the output in real-time
#         for line in iter(process.stdout.readline, ''):
#             if line.strip():
#                 process_status["message_queue"].put(line.strip())
        
#         # Wait for the process to complete
#         process.stdout.close()
#         return_code = process.wait()
        
#         # Get any error output
#         errors = process.stderr.read()
#         if errors:
#             for error_line in errors.split('\n'):
#                 if error_line.strip():
#                     process_status["message_queue"].put(f"Error: {error_line.strip()}")
        
#         # Check result
#         if return_code == 0:
#             # Check if the model file was created
#             model_path = os.path.join(script_dir, "models", "candidate_verification.yml")
#             if os.path.exists(model_path):
#                 process_status["success"] = True
#                 process_status["final_message"] = "Registration completed successfully! The model has been created."
#                 process_status["message_queue"].put(process_status["final_message"])
#             else:
#                 process_status["success"] = False
#                 process_status["final_message"] = "Process completed but model file was not created."
#                 process_status["message_queue"].put(process_status["final_message"])
#         else:
#             process_status["success"] = False
#             process_status["final_message"] = f"Process failed with exit code: {return_code}"
#             process_status["message_queue"].put(process_status["final_message"])
    
#     except Exception as e:
#         process_status["success"] = False
#         process_status["final_message"] = f"An error occurred: {str(e)}"
#         process_status["message_queue"].put(process_status["final_message"])
    
#     finally:
#         process_status["completed"] = True
#         process_status["running"] = False
#         if process and hasattr(process, 'stderr') and process.stderr:
#             process.stderr.close()

# @app.route('/status')
# def status():
#     """Return the current status of the registration process"""
#     messages = []
    
#     # Get all available messages from the queue without blocking
#     while not process_status["message_queue"].empty():
#         try:
#             message = process_status["message_queue"].get_nowait()
#             messages.append(message)
#         except queue.Empty:
#             break
    
#     return jsonify({
#         "running": process_status["running"],
#         "completed": process_status["completed"],
#         "success": process_status["success"],
#         "messages": messages,
#         "final_message": process_status["final_message"]
#     })

# @app.route('/reset', methods=['POST'])
# def reset():
#     """Reset the process status"""
#     reset_status()
#     return jsonify({"status": "reset"})

# # Create the templates directory and index.html
# def create_templates():
#     """Create the templates directory and index.html file if they don't exist"""
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     templates_dir = os.path.join(script_dir, "templates")
    
#     # Create templates directory if it doesn't exist
#     if not os.path.exists(templates_dir):
#         os.makedirs(templates_dir)
    
#     # Create index.html if it doesn't exist
#     index_html_path = os.path.join(templates_dir, "index.html")


# if __name__ == '__main__':
#     # Create templates directory and index.html
#     create_templates()
    
#     # Run the Flask app
#     app.run(debug=True, host='0.0.0.0', port=5000)












from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import subprocess
import os
import sys
import threading
import time
import queue
import json
import re
from datetime import datetime

app = Flask(__name__)

# Global variables to track process status
process_status = {
    "running": False,
    "completed": False,
    "success": False,
    "message_queue": queue.Queue(),
    "final_message": "",
    "current_process": None  # 'registration' or 'proctor'
}

# Global variables for proctor stats
proctor_stats = {
    "no_face_count": 0,
    "multiple_faces_count": 0,
    "face_mismatch_count": 0,
    "normal_behavior_count": 0,
    "total_checks": 0
}

def reset_status():
    """Reset the process status"""
    process_status["running"] = False
    process_status["completed"] = False
    process_status["success"] = False
    process_status["final_message"] = ""
    process_status["current_process"] = None
    # Clear the queue
    while not process_status["message_queue"].empty():
        process_status["message_queue"].get()

def reset_proctor_stats():
    """Reset the proctor statistics"""
    proctor_stats["no_face_count"] = 0
    proctor_stats["multiple_faces_count"] = 0
    proctor_stats["face_mismatch_count"] = 0
    proctor_stats["normal_behavior_count"] = 0
    proctor_stats["total_checks"] = 0

@app.route('/')
def index():
    """Render the main page"""
    # Check if models directory exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "models", "candidate_verification.yml")
    model_exists = os.path.exists(model_path)
    
    return render_template('main.html', model_exists=model_exists)
@app.route('/index.html')
def app_page():
    return render_template('index.html')

@app.route('/exam.html')
def exam_page():
    return render_template('exam.html')


@app.route('/register', methods=['POST'])
def register():
    """Start the registration process"""
    global process_status
    
    # Check if process is already running
    if process_status["running"]:
        return jsonify({"status": "error", "message": "A process is already running"})
    
    # Reset status
    reset_status()
    
    # Set process as running
    process_status["running"] = True
    process_status["current_process"] = "registration"
    
    # Start the registration process in a background thread
    thread = threading.Thread(target=run_registration)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "process": "registration"})

@app.route('/proctor', methods=['POST'])
def proctor():
    """Start the exam proctoring process"""
    global process_status
    
    # Check if process is already running
    if process_status["running"]:
        return jsonify({"status": "error", "message": "A process is already running"})
    
    # Check if model exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "models", "candidate_verification.yml")
    if not os.path.exists(model_path):
        return jsonify({
            "status": "error", 
            "message": "Face model not found. Please complete registration first."
        })
    
    # Get duration from request
    try:
        duration = int(request.form.get('duration', 60))
    except:
        duration = 60
    
    # Reset status
    reset_status()
    reset_proctor_stats()
    
    # Set process as running
    process_status["running"] = True
    process_status["current_process"] = "proctor"
    
    # Create Exam_infringement_record directory if it doesn't exist
    infringement_dir = os.path.join(script_dir, "Exam_infringement_record")
    if not os.path.exists(infringement_dir):
        os.makedirs(infringement_dir)
    
    # Start the proctoring process in a background thread
    thread = threading.Thread(target=run_proctoring, args=(duration,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "process": "proctor", "duration": duration})

def run_registration():
    """Run the registration script"""
    global process_status
    
    try:
        # Get the path to register.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        register_script_path = os.path.join(script_dir, "register.py")
        
        # Check if register.py exists
        if not os.path.exists(register_script_path):
            process_status["message_queue"].put("Error: register.py not found")
            process_status["completed"] = True
            process_status["running"] = False
            process_status["success"] = False
            process_status["final_message"] = "Error: register.py not found"
            return
        
        # Add initial message
        process_status["message_queue"].put("Starting face registration process...")
        
        # Execute the register.py script
        process = subprocess.Popen(
            [sys.executable, register_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Process the output in real-time
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                process_status["message_queue"].put(line.strip())
        
        # Wait for the process to complete
        process.stdout.close()
        return_code = process.wait()
        
        # Get any error output
        errors = process.stderr.read()
        if errors:
            for error_line in errors.split('\n'):
                if error_line.strip():
                    process_status["message_queue"].put(f"Error: {error_line.strip()}")
        
        # Check result
        if return_code == 0:
            # Check if the model file was created
            model_path = os.path.join(script_dir, "models", "candidate_verification.yml")
            if os.path.exists(model_path):
                process_status["success"] = True
                process_status["final_message"] = "Registration completed successfully! The model has been created."
                process_status["message_queue"].put(process_status["final_message"])
            else:
                process_status["success"] = False
                process_status["final_message"] = "Process completed but model file was not created."
                process_status["message_queue"].put(process_status["final_message"])
        else:
            process_status["success"] = False
            process_status["final_message"] = f"Process failed with exit code: {return_code}"
            process_status["message_queue"].put(process_status["final_message"])
    
    except Exception as e:
        process_status["success"] = False
        process_status["final_message"] = f"An error occurred: {str(e)}"
        process_status["message_queue"].put(process_status["final_message"])
    
    finally:
        process_status["completed"] = True
        process_status["running"] = False
        if process and hasattr(process, 'stderr') and process.stderr:
            process.stderr.close()

def run_proctoring(duration):
    """Run the exam proctoring script"""
    global process_status, proctor_stats
    
    try:
        # Get the path to exam_proctor.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        proctor_script_path = os.path.join(script_dir, "exam_proctor.py")
        
        # Create exam_proctor.py if it doesn't exist
        if not os.path.exists(proctor_script_path):
            with open(proctor_script_path, "w") as f:
                f.write("""import cv2
import time
from os import system

font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
cam.set(3, 1280) # set video width
cam.set(4, 720) # set video height

def getFaces(img):
    faces = getFaces.face_detector.detectMultiScale(
        img_gray,
        scaleFactor = 1.2,
        minNeighbors = 5,
        minSize = (getFaces.minW, getFaces.minH),
       )
    return faces

getFaces.face_detector = cv2.CascadeClassifier('./models/haarcascade_frontalface_default.xml');
# Define min window size to be recognized as a face
getFaces.minW = int(0.1*cam.get(3))
getFaces.minH = int(0.1*cam.get(4))

def matchFace(img_gray, face):
    x, y, w, h = face
    id, loss = matchFace.recognizer.predict(img_gray[y:y+h,x:x+w])
    return id == 1

matchFace.recognizer = cv2.face.LBPHFaceRecognizer_create()
matchFace.recognizer.read('./models/candidate_verification.yml')

def record_infringement(time_point, nature , img):
    cv2.imwrite("./Exam_infringement_record/{}_{}.jpg".format(nature, time_point) , img[:])

def logFaceMismatch(img, face):
    draw_rectangle(img, face)
    record_infringement(time.time(), "FaceMismatch", img)

    # Visualization.
    display_status(img, "FACE MISMATCH")


def logMultipleFacesDetected(img, faces):
    for face in faces: 
        draw_rectangle(img, face)

    record_infringement(time.time(), "MultipleFacesDetected", img)

    # Visualization.
    display_status(img, "MULTIPLE FACES DETECTED")



def logNoFaceDetected(img):
    record_infringement(time.time(), "NoFaceFound", img)

    # Visualization.
    display_status(img, "NO FACE DETECTED")

def logNormalBehaviour(img, face):

    # Visualization.
    green = (0,204,0)
    draw_rectangle(img, face, green)
    display_status(img, "CLEAR", green)

def draw_rectangle(img, face, color=(0,0,255)):
    x, y, w, h = face
    cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)

def display_status(img, status, color=(0,0,255)):
    cv2.putText(img, status, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

print("[INFO] Enter the proctoring period(seconds) -- ")
period = int(input())
start = time.time()

while time.time() < period + start:
    ret, img = cam.read()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = getFaces(img_gray)

    if(len(faces) == 0):
        logNoFaceDetected(img)
    elif(len(faces) > 1):
        logMultipleFacesDetected(img, faces)
    elif matchFace(img_gray, faces[0]) == False:
        logFaceMismatch(img, faces[0])
    else:
        logNormalBehaviour(img, faces[0])

    # Visualization.
    # Display processed images as a vid
    cv2.imshow('camera',img) 

    k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break

    time.sleep(0.10)

# Do a bit of cleanup
print("\\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
""")
        
        # Add initial message
        process_status["message_queue"].put(f"Starting exam proctoring process for {duration} seconds...")
        
        # Create a process to run the exam_proctor.py script
        process = subprocess.Popen(
            [sys.executable, proctor_script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Send the duration to the script
        process.stdin.write(str(duration) + "\n")
        process.stdin.flush()
        
        # Process the output in real-time
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                process_status["message_queue"].put(line.strip())
                
                # Collect statistics based on output
                if "NO FACE DETECTED" in line:
                    proctor_stats["no_face_count"] += 1
                    proctor_stats["total_checks"] += 1
                elif "MULTIPLE FACES DETECTED" in line:
                    proctor_stats["multiple_faces_count"] += 1
                    proctor_stats["total_checks"] += 1
                elif "FACE MISMATCH" in line:
                    proctor_stats["face_mismatch_count"] += 1
                    proctor_stats["total_checks"] += 1
                elif "CLEAR" in line:
                    proctor_stats["normal_behavior_count"] += 1
                    proctor_stats["total_checks"] += 1
        
        # Wait for the process to complete
        if process.stdout:
            process.stdout.close()
        return_code = process.wait()
        
        # Count the infringement images
        infringement_dir = os.path.join(script_dir, "Exam_infringement_record")
        if os.path.exists(infringement_dir):
            no_face_files = [f for f in os.listdir(infringement_dir) if f.startswith("NoFaceFound")]
            multiple_faces_files = [f for f in os.listdir(infringement_dir) if f.startswith("MultipleFacesDetected")]
            face_mismatch_files = [f for f in os.listdir(infringement_dir) if f.startswith("FaceMismatch")]
            
            # Update stats based on actual files saved (more accurate than counting log messages)
            proctor_stats["no_face_count"] = len(no_face_files)
            proctor_stats["multiple_faces_count"] = len(multiple_faces_files)
            proctor_stats["face_mismatch_count"] = len(face_mismatch_files)
            
            # Total checks equals all the infringements plus normal behavior
            total_infringements = proctor_stats["no_face_count"] + proctor_stats["multiple_faces_count"] + proctor_stats["face_mismatch_count"]
            proctor_stats["normal_behavior_count"] = proctor_stats["total_checks"] - total_infringements
        
        # Generate summary
        summary = f"""
Proctoring Summary:
------------------
Duration: {duration} seconds
Total Checks: {proctor_stats['total_checks']}
Normal Behavior: {proctor_stats['normal_behavior_count']} ({(proctor_stats['normal_behavior_count']/proctor_stats['total_checks']*100 if proctor_stats['total_checks'] > 0 else 0):.2f}%)
No Face Detected: {proctor_stats['no_face_count']} ({(proctor_stats['no_face_count']/proctor_stats['total_checks']*100 if proctor_stats['total_checks'] > 0 else 0):.2f}%)
Multiple Faces: {proctor_stats['multiple_faces_count']} ({(proctor_stats['multiple_faces_count']/proctor_stats['total_checks']*100 if proctor_stats['total_checks'] > 0 else 0):.2f}%)
Face Mismatch: {proctor_stats['face_mismatch_count']} ({(proctor_stats['face_mismatch_count']/proctor_stats['total_checks']*100 if proctor_stats['total_checks'] > 0 else 0):.2f}%)
        """
        
        # Check result
        if return_code == 0:
            process_status["success"] = True
            process_status["final_message"] = "Proctoring completed successfully."
            process_status["message_queue"].put(process_status["final_message"])
            process_status["message_queue"].put(summary)
        else:
            # Get any error output
            errors = process.stderr.read() if process.stderr else ""
            
            process_status["success"] = False
            process_status["final_message"] = f"Proctoring process failed with exit code: {return_code}"
            process_status["message_queue"].put(process_status["final_message"])
            
            if errors:
                for error_line in errors.split('\n'):
                    if error_line.strip():
                        process_status["message_queue"].put(f"Error: {error_line.strip()}")
    
    except Exception as e:
        process_status["success"] = False
        process_status["final_message"] = f"An error occurred: {str(e)}"
        process_status["message_queue"].put(process_status["final_message"])
    
    finally:
        process_status["completed"] = True
        process_status["running"] = False
        if process and hasattr(process, 'stderr') and process.stderr:
            process.stderr.close()

@app.route('/status')
def status():
    """Return the current status of the process"""
    messages = []
    
    # Get all available messages from the queue without blocking
    while not process_status["message_queue"].empty():
        try:
            message = process_status["message_queue"].get_nowait()
            messages.append(message)
        except queue.Empty:
            break
    
    # Return both process status and proctor stats if applicable
    if process_status["current_process"] == "proctor" and process_status["completed"]:
        return jsonify({
            "running": process_status["running"],
            "completed": process_status["completed"],
            "success": process_status["success"],
            "messages": messages,
            "final_message": process_status["final_message"],
            "process_type": process_status["current_process"],
            "proctor_stats": proctor_stats
        })
    else:
        return jsonify({
            "running": process_status["running"],
            "completed": process_status["completed"],
            "success": process_status["success"],
            "messages": messages,
            "final_message": process_status["final_message"],
            "process_type": process_status["current_process"]
        })

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the process status"""
    reset_status()
    reset_proctor_stats()
    return jsonify({"status": "reset"})

@app.route('/get_logs')
def get_logs():
    """Get the infringement logs and stats"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    infringement_dir = os.path.join(script_dir, "Exam_infringement_record")
    
    logs = {
        "no_face_incidents": [],
        "multiple_faces_incidents": [],
        "face_mismatch_incidents": []
    }
    
    if os.path.exists(infringement_dir):
        for file in os.listdir(infringement_dir):
            try:
                parts = file.split('_')
                if len(parts) >= 2:
                    incident_type = parts[0]
                    timestamp = float(parts[1].split('.')[0])
                    formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    
                    if incident_type == "NoFaceFound":
                        logs["no_face_incidents"].append({
                            "timestamp": timestamp,
                            "formatted_time": formatted_time,
                            "file": file
                        })
                    elif incident_type == "MultipleFacesDetected":
                        logs["multiple_faces_incidents"].append({
                            "timestamp": timestamp,
                            "formatted_time": formatted_time,
                            "file": file
                        })
                    elif incident_type == "FaceMismatch":
                        logs["face_mismatch_incidents"].append({
                            "timestamp": timestamp,
                            "formatted_time": formatted_time,
                            "file": file
                        })
            except Exception as e:
                print(f"Error processing log file {file}: {e}")
    
    return jsonify({
        "logs": logs,
        "stats": proctor_stats
    })

# Create the templates directory and index.html
def create_templates():
    """Create the templates directory and index.html file if they don't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(script_dir, "templates")
    
    # Create templates directory if it doesn't exist
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Create index.html if it doesn't exist
    index_html_path = os.path.join(templates_dir, "index.html")
    if not os.path.exists(index_html_path):
        with open(index_html_path, "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Recognition & Exam Proctoring System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        h1, h2 {
            color: #333;
            text-align: center;
        }
        .container {
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .tab-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background-color: #e9ecef;
            border: 1px solid #dee2e6;
            transition: background-color 0.3s;
        }
        .tab:first-child {
            border-top-left-radius: 5px;
            border-bottom-left-radius: 5px;
        }
        .tab:last-child {
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
        }
        .tab.active {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .instructions {
            background-color: #e9f7fe;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 20px;
        }
        .buttons {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        #resetBtn {
            background-color: #f44336;
        }
        #resetBtn:hover {
            background-color: #d32f2f;
        }
        #output {
            background-color: #000;
            color: #00ff00;
            padding: 10px;
            border-radius: 5px;
            height: 250px;
            overflow-y: auto;
            font-family: monospace;
            margin-top: 20px;
        }
        .success {
            color: #4CAF50;
            font-weight: bold;
        }
        .error {
            color: #f44336;
            font-weight: bold;
        }
        .warning {
            color: #ff9800;
            font-weight: bold;
        }
        .progress {
            height: 10px;
            background-color: #ddd;
            border-radius: 5px;
            margin-top: 20px;
            position: relative;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background-color: #4CAF50;
            border-radius: 5px;
            width: 0%;
            transition: width 0.3s;
            position: absolute;
        }
        .progress-indeterminate {
            background: linear-gradient(to right, #ddd 30%, #4CAF50 50%, #ddd 70%);
            background-size: 200% 100%;
            animation: progress-animation 1.5s infinite;
            height: 100%;
            width: 100%;
        }
        @keyframes progress-animation {
            0% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 14px;
            font-weight: bold;
            margin: 10px 0;
        }
        .status-idle {
            background-color: #e0e0e0;
            color: #333;
        }
        .status-running {
            background-color: #2196F3;
            color: white;
        }
        .status-success {
            background-color: #4CAF50;
            color: white;
        }
        .status-error {
            background-color: #f44336;
            color: white;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .stats-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-top: 20px;
        }
        .stat-card {
            flex-basis: 48%;
            background-color: #fff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stat-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-percentage {
            font-size: 14px;
            color: #666;
        }
        .pie-chart {
            width: 200px;
            height: 200px;
            margin: 20px auto;
            position: relative;
        }
    </style>
</head>
<body>
    <h1>Face Recognition & Exam Proctoring System</h1>
    
    <div class="tab-container">
        <div class="tab active" onclick="switchTab('registration')">Registration</div>
        <div class="tab" onclick="switchTab('proctoring')">Exam Proctoring</div>
        <div class="tab" onclick="switchTab('logs')">Logs & Stats</div>
    </div>
    
    <div id="registration" class="tab-content active container">
        <h2>Face Registration</h2>
        
        <div class="instructions">
            <h3>Instructions:</h3>
            <ol>
                <li>Make sure your camera is connected and working</li>
                <li>Position yourself in front of the camera</li>
                <li>Click the "Start Registration" button</li>
                <li>The system will capture 20 images of your face</li>
                <li>Look at different angles for better recognition accuracy</li>
                <li>Press ESC during capture if you need to stop early</li>
            </ol>
        </div>
        
        <div id="regStatusContainer">
            <span id="regStatusBadge" class="status-badge status-idle">Ready</span>
        </div>
        
        <div id="regProgressContainer" style="display: none;">
            <div class="progress">
                <div class="progress-indeterminate"></div>
            </div>
        </div>
        
        <div class="buttons">
            <button id="startRegBtn">Start Registration</button>
            <button id="resetRegBtn" style="display: none;">Reset</button>
        </div>
        
        <div id="regOutput" class="output"></div>
    </div>
    
    <div id="proctoring" class="tab-content container">
        <h2>Exam Proctoring</h2>
        
        <div class="instructions">
            <h3>Instructions:</h3>
            <ol>
                <li>Make sure you have completed the face registration</li>
                <li>Enter the duration for the proctoring session (in seconds)</li>
                <li>Click "Start Proctoring" to begin the session</li>
                <li>Stay in front of the camera during the entire session</li>
                <li>The system will monitor your presence and identity</li>
                <li>Any violations will be logged for review</li>
            </ol>
        </div>
        
        <div class="form-group">
            <label for="duration">Proctoring Duration (seconds):</label>
            <input type="number" id="duration" min="10" value="60">
        </div>
        
        <div id="proctorStatusContainer">
            <span id="proctorStatusBadge" class="status-badge status-idle">Ready</span>
        </div>
        
<div id="proctorProgressContainer" style="display: none;">
            <div class="progress">
                <div class="progress-indeterminate"></div>
            </div>
        </div>
        
        <div class="buttons">
            <button id="startProctorBtn">Start Proctoring</button>
            <button id="resetProctorBtn" style="display: none;">Reset</button>
        </div>
        
        <div id="proctorOutput" class="output"></div>
    </div>
    
    <div id="logs" class="tab-content container">
        <h2>Proctoring Logs & Statistics</h2>
        
        <div class="instructions">
            <p>This section displays the logs and statistics from your proctoring sessions. You can view infractions and overall behavior patterns.</p>
        </div>
        
        <div class="buttons">
            <button id="refreshLogsBtn">Refresh Logs</button>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-title">Normal Behavior</div>
                <div id="normalBehaviorCount" class="stat-value">0</div>
                <div id="normalBehaviorPercentage" class="stat-percentage">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">No Face Detected</div>
                <div id="noFaceCount" class="stat-value">0</div>
                <div id="noFacePercentage" class="stat-percentage">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Multiple Faces</div>
                <div id="multipleFacesCount" class="stat-value">0</div>
                <div id="multipleFacesPercentage" class="stat-percentage">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Face Mismatch</div>
                <div id="faceMismatchCount" class="stat-value">0</div>
                <div id="faceMismatchPercentage" class="stat-percentage">0%</div>
            </div>
        </div>
        
        <div id="pieChartContainer" class="pie-chart">
            <!-- Pie chart will be inserted here -->
        </div>
        
        <h3>Infringement Logs</h3>
        <div id="logsContainer">
            <div id="noFaceLogs">
                <h4>No Face Detected</h4>
                <ul id="noFaceList"></ul>
            </div>
            <div id="multipleFacesLogs">
                <h4>Multiple Faces Detected</h4>
                <ul id="multipleFacesList"></ul>
            </div>
            <div id="faceMismatchLogs">
                <h4>Face Mismatch</h4>
                <ul id="faceMismatchList"></ul>
            </div>
        </div>
    </div>
    
    <script>
        // Tabs functionality
        function switchTab(tabName) {
            const tabs = document.getElementsByClassName('tab');
            const contents = document.getElementsByClassName('tab-content');
            
            // Deactivate all tabs and contents
            for (let i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            for (let i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            // Activate the selected tab and content
            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Refresh logs if navigating to logs tab
            if (tabName === 'logs') {
                fetchLogs();
            }
        }
        
        // Registration functionality
        const startRegBtn = document.getElementById('startRegBtn');
        const resetRegBtn = document.getElementById('resetRegBtn');
        const regOutput = document.getElementById('regOutput');
        const regStatusBadge = document.getElementById('regStatusBadge');
        const regProgressContainer = document.getElementById('regProgressContainer');
        
        startRegBtn.addEventListener('click', startRegistration);
        resetRegBtn.addEventListener('click', resetRegistration);
        
        function startRegistration() {
            regOutput.innerHTML = '';
            regStatusBadge.textContent = 'Running...';
            regStatusBadge.className = 'status-badge status-running';
            startRegBtn.disabled = true;
            regProgressContainer.style.display = 'block';
            
            fetch('/register', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    pollStatus('registration');
                } else {
                    addRegOutput('Error: ' + data.message, 'error');
                    regStatusBadge.textContent = 'Error';
                    regStatusBadge.className = 'status-badge status-error';
                    startRegBtn.disabled = false;
                    regProgressContainer.style.display = 'none';
                }
            })
            .catch(error => {
                addRegOutput('Error: ' + error, 'error');
                regStatusBadge.textContent = 'Error';
                regStatusBadge.className = 'status-badge status-error';
                startRegBtn.disabled = false;
                regProgressContainer.style.display = 'none';
            });
        }
        
        function resetRegistration() {
            fetch('/reset', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                regOutput.innerHTML = '';
                regStatusBadge.textContent = 'Ready';
                regStatusBadge.className = 'status-badge status-idle';
                startRegBtn.disabled = false;
                resetRegBtn.style.display = 'none';
                regProgressContainer.style.display = 'none';
            });
        }
        
        function addRegOutput(message, type = '') {
            const div = document.createElement('div');
            if (type) {
                div.className = type;
            }
            div.textContent = message;
            regOutput.appendChild(div);
            regOutput.scrollTop = regOutput.scrollHeight;
        }
        
        // Proctoring functionality
        const startProctorBtn = document.getElementById('startProctorBtn');
        const resetProctorBtn = document.getElementById('resetProctorBtn');
        const proctorOutput = document.getElementById('proctorOutput');
        const proctorStatusBadge = document.getElementById('proctorStatusBadge');
        const proctorProgressContainer = document.getElementById('proctorProgressContainer');
        const durationInput = document.getElementById('duration');
        
        startProctorBtn.addEventListener('click', startProctoring);
        resetProctorBtn.addEventListener('click', resetProctoring);
        
        function startProctoring() {
            proctorOutput.innerHTML = '';
            proctorStatusBadge.textContent = 'Running...';
            proctorStatusBadge.className = 'status-badge status-running';
            startProctorBtn.disabled = true;
            proctorProgressContainer.style.display = 'block';
            
            const formData = new FormData();
            formData.append('duration', durationInput.value);
            
            fetch('/proctor', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    pollStatus('proctor');
                } else {
                    addProctorOutput('Error: ' + data.message, 'error');
                    proctorStatusBadge.textContent = 'Error';
                    proctorStatusBadge.className = 'status-badge status-error';
                    startProctorBtn.disabled = false;
                    proctorProgressContainer.style.display = 'none';
                }
            })
            .catch(error => {
                addProctorOutput('Error: ' + error, 'error');
                proctorStatusBadge.textContent = 'Error';
                proctorStatusBadge.className = 'status-badge status-error';
                startProctorBtn.disabled = false;
                proctorProgressContainer.style.display = 'none';
            });
        }
        
        function resetProctoring() {
            fetch('/reset', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                proctorOutput.innerHTML = '';
                proctorStatusBadge.textContent = 'Ready';
                proctorStatusBadge.className = 'status-badge status-idle';
                startProctorBtn.disabled = false;
                resetProctorBtn.style.display = 'none';
                proctorProgressContainer.style.display = 'none';
            });
        }
        
        function addProctorOutput(message, type = '') {
            const div = document.createElement('div');
            if (type) {
                div.className = type;
            }
            div.textContent = message;
            proctorOutput.appendChild(div);
            proctorOutput.scrollTop = proctorOutput.scrollHeight;
        }
        
        // Status polling
        function pollStatus(processType) {
            const statusInterval = setInterval(() => {
                fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // Process messages
                    if (data.messages && data.messages.length > 0) {
                        if (processType === 'registration') {
                            data.messages.forEach(msg => addRegOutput(msg));
                        } else {
                            data.messages.forEach(msg => addProctorOutput(msg));
                        }
                    }
                    
                    // Check if process has completed
                    if (data.completed) {
                        clearInterval(statusInterval);
                        
                        if (processType === 'registration') {
                            regProgressContainer.style.display = 'none';
                            resetRegBtn.style.display = 'inline-block';
                            
                            if (data.success) {
                                regStatusBadge.textContent = 'Success';
                                regStatusBadge.className = 'status-badge status-success';
                                addRegOutput(data.final_message, 'success');
                            } else {
                                regStatusBadge.textContent = 'Failed';
                                regStatusBadge.className = 'status-badge status-error';
                                addRegOutput(data.final_message, 'error');
                            }
                        } else {
                            proctorProgressContainer.style.display = 'none';
                            resetProctorBtn.style.display = 'inline-block';
                            
                            if (data.success) {
                                proctorStatusBadge.textContent = 'Success';
                                proctorStatusBadge.className = 'status-badge status-success';
                                addProctorOutput(data.final_message, 'success');
                                
                                // Update stats if available
                                if (data.proctor_stats) {
                                    updateStats(data.proctor_stats);
                                }
                            } else {
                                proctorStatusBadge.textContent = 'Failed';
                                proctorStatusBadge.className = 'status-badge status-error';
                                addProctorOutput(data.final_message, 'error');
                            }
                            
                            // Fetch logs after proctoring completes
                            fetchLogs();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error polling status:', error);
                    clearInterval(statusInterval);
                    
                    if (processType === 'registration') {
                        regProgressContainer.style.display = 'none';
                        regStatusBadge.textContent = 'Error';
                        regStatusBadge.className = 'status-badge status-error';
                        startRegBtn.disabled = false;
                        addRegOutput('Error polling status: ' + error, 'error');
                    } else {
                        proctorProgressContainer.style.display = 'none';
                        proctorStatusBadge.textContent = 'Error';
                        proctorStatusBadge.className = 'status-badge status-error';
                        startProctorBtn.disabled = false;
                        addProctorOutput('Error polling status: ' + error, 'error');
                    }
                });
            }, 1000);
        }
        
        // Logs functionality
        const refreshLogsBtn = document.getElementById('refreshLogsBtn');
        refreshLogsBtn.addEventListener('click', fetchLogs);
        
        function fetchLogs() {
            fetch('/get_logs')
            .then(response => response.json())
            .then(data => {
                updateStats(data.stats);
                updateLogs(data.logs);
            })
            .catch(error => {
                console.error('Error fetching logs:', error);
            });
        }
        
        function updateStats(stats) {
            // Update stat counts and percentages
            document.getElementById('normalBehaviorCount').textContent = stats.normal_behavior_count;
            document.getElementById('noFaceCount').textContent = stats.no_face_count;
            document.getElementById('multipleFacesCount').textContent = stats.multiple_faces_count;
            document.getElementById('faceMismatchCount').textContent = stats.face_mismatch_count;
            
            const total = stats.total_checks || 0;
            
            if (total > 0) {
                document.getElementById('normalBehaviorPercentage').textContent = 
                    `${((stats.normal_behavior_count / total) * 100).toFixed(2)}%`;
                document.getElementById('noFacePercentage').textContent = 
                    `${((stats.no_face_count / total) * 100).toFixed(2)}%`;
                document.getElementById('multipleFacesPercentage').textContent = 
                    `${((stats.multiple_faces_count / total) * 100).toFixed(2)}%`;
                document.getElementById('faceMismatchPercentage').textContent = 
                    `${((stats.face_mismatch_count / total) * 100).toFixed(2)}%`;
            }
            
            // Create a simple pie chart
            updatePieChart(stats);
        }
        
        function updatePieChart(stats) {
            const chartContainer = document.getElementById('pieChartContainer');
            chartContainer.innerHTML = '';
            
            const total = stats.total_checks || 0;
            if (total === 0) return;
            
            // Create an SVG element
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '200');
            svg.setAttribute('height', '200');
            svg.setAttribute('viewBox', '0 0 100 100');
            
            // Define colors
            const colors = {
                normal: '#4CAF50',
                noFace: '#f44336',
                multipleFaces: '#ff9800',
                faceMismatch: '#2196F3'
            };
            
            // Calculate angles
            let startAngle = 0;
            const data = [
                { name: 'Normal', value: stats.normal_behavior_count, color: colors.normal },
                { name: 'No Face', value: stats.no_face_count, color: colors.noFace },
                { name: 'Multiple Faces', value: stats.multiple_faces_count, color: colors.multipleFaces },
                { name: 'Face Mismatch', value: stats.face_mismatch_count, color: colors.faceMismatch }
            ].filter(item => item.value > 0);
            
            // Create pie slices
            for (const item of data) {
                const angle = (item.value / total) * 360;
                const slice = createPieSlice(50, 50, 40, startAngle, startAngle + angle, item.color);
                svg.appendChild(slice);
                startAngle += angle;
            }
            
            // Add center hole for donut chart
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', '50');
            circle.setAttribute('cy', '50');
            circle.setAttribute('r', '25');
            circle.setAttribute('fill', 'white');
            svg.appendChild(circle);
            
            // Add the SVG to the container
            chartContainer.appendChild(svg);
        }
        
        function createPieSlice(cx, cy, r, startAngle, endAngle, fill) {
            // Convert angles to radians
            const startRad = (startAngle - 90) * Math.PI / 180;
            const endRad = (endAngle - 90) * Math.PI / 180;
            
            // Calculate coordinates
            const x1 = cx + r * Math.cos(startRad);
            const y1 = cy + r * Math.sin(startRad);
            const x2 = cx + r * Math.cos(endRad);
            const y2 = cy + r * Math.sin(endRad);
            
            // Create path
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            
            // Determine which arc to use (large or small)
            const largeArcFlag = endAngle - startAngle <= 180 ? 0 : 1;
            
            // Create SVG path
            const d = [
                `M ${cx},${cy}`,
                `L ${x1},${y1}`,
                `A ${r},${r} 0 ${largeArcFlag},1 ${x2},${y2}`,
                'Z'
            ].join(' ');
            
            path.setAttribute('d', d);
            path.setAttribute('fill', fill);
            
            return path;
        }
        
        function updateLogs(logs) {
            // Update No Face logs
            const noFaceList = document.getElementById('noFaceList');
            noFaceList.innerHTML = '';
            logs.no_face_incidents.forEach(incident => {
                const li = document.createElement('li');
                li.textContent = `${incident.formatted_time}`;
                noFaceList.appendChild(li);
            });
            
            // Update Multiple Faces logs
            const multipleFacesList = document.getElementById('multipleFacesList');
            multipleFacesList.innerHTML = '';
            logs.multiple_faces_incidents.forEach(incident => {
                const li = document.createElement('li');
                li.textContent = `${incident.formatted_time}`;
                multipleFacesList.appendChild(li);
            });
            
            // Update Face Mismatch logs
            const faceMismatchList = document.getElementById('faceMismatchList');
            faceMismatchList.innerHTML = '';
            logs.face_mismatch_incidents.forEach(incident => {
                const li = document.createElement('li');
                li.textContent = `${incident.formatted_time}`;
                faceMismatchList.appendChild(li);
            });
        }
        
        // Check if face model exists on page load
        const modelExists = {{ model_exists|tojson }};
        if (!modelExists) {
            regStatusBadge.textContent = 'Registration Required';
            regStatusBadge.className = 'status-badge status-warning';
            
            proctorStatusBadge.textContent = 'Registration Required';
            proctorStatusBadge.className = 'status-badge status-warning';
            startProctorBtn.disabled = true;
        }
        
        // Initial logs fetch
        fetchLogs();
    </script>
</body>
</html>""")

def create_models_dir():
    """Create the models directory if it doesn't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "models")
    
    # Create models directory if it doesn't exist
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Check if haarcascade_frontalface_default.xml exists, if not download it
    haarcascade_path = os.path.join(models_dir, "haarcascade_frontalface_default.xml")
    if not os.path.exists(haarcascade_path):
        try:
            import urllib.request
            print("Downloading haarcascade_frontalface_default.xml...")
            url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            urllib.request.urlretrieve(url, haarcascade_path)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading haarcascade file: {e}")
            print("Please download manually and place in the models directory.")

if __name__ == "__main__":
    # Create necessary directories and files
    create_templates()
    create_models_dir()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)