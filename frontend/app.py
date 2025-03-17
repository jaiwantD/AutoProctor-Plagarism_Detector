from flask import Flask, render_template, jsonify, redirect, url_for, Response
import subprocess
import os
import sys
import threading
import time

app = Flask(__name__)

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (project root)
project_root = os.path.dirname(current_dir)
# Path to the backend register.py
register_script_path = os.path.join(project_root, 'backend', 'register.py')

# Global variables to store registration process results
registration_process = None
registration_output = ""
registration_complete = False
registration_success = False

@app.route('/')
def index():
    """Render the main index page"""
    global registration_complete, registration_success, registration_output
    # Reset registration status when landing on the main page
    registration_complete = False
    registration_success = False
    registration_output = ""
    return render_template('main.html')
@app.route('/index.html')
def app_page():
    return render_template('index.html')

def run_registration():
    """Run the register.py script in a separate thread and capture its output"""
    global registration_process, registration_output, registration_complete, registration_success
    
    try:
        # Run the register.py script
        registration_process = subprocess.Popen(
            [sys.executable, register_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Capture output
        stdout, stderr = registration_process.communicate()
        
        # Store output
        registration_output = stdout + stderr
        
        # Check if registration was successful
        registration_success = "Registration successful" in registration_output
        
        # Mark as complete
        registration_complete = True
        
    except Exception as e:
        registration_output = f"Error running registration: {str(e)}"
        registration_complete = True
        registration_success = False

@app.route('/register', methods=['POST'])
def register():
    """Start the registration process"""
    global registration_complete, registration_success, registration_output
    
    # Reset status
    registration_complete = False
    registration_success = False
    registration_output = ""
    
    # Start registration in a separate thread
    threading.Thread(target=run_registration).start()
    
    # Return immediately with a pending status
    return jsonify({
        'success': True,
        'message': 'Registration started',
        'status': 'pending'
    })

@app.route('/check_registration_status')
def check_registration_status():
    """Check the status of the registration process"""
    global registration_complete, registration_success, registration_output
    
    if not registration_complete:
        return jsonify({
            'complete': False,
            'message': 'Registration in progress...'
        })
    
    return jsonify({
        'complete': True,
        'success': registration_success,
        'message': registration_output
    })

@app.route('/exam')
def exam():
    """Run the exam_proctor.py script and redirect to the exam page"""
    try:
        # Path to the exam_proctor.py script
        exam_script_path = os.path.join(project_root, 'backend', 'exam_proctor.py')
        
        # Start the exam proctor script as a background process
        subprocess.Popen(
            [sys.executable, exam_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # For now, just render a placeholder exam page
        return render_template('exam.html')
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to start exam: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True)


