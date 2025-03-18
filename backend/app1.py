


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



def create_models_dir():
    """Create the models directory if it doesn't exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "models")
    
    # Create models directory if it doesn't exist
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    
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
    create_models_dir()
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)