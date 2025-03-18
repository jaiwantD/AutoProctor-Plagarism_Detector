from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import subprocess
import threading

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

log_data = {"Clear": 0, "No Face Detected": 0}
log_lock = threading.Lock()

def run_proctoring():
    global log_data
    proc = subprocess.Popen(['python', 'exam_proctor.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        with log_lock:
            if "CLEAR" in line:
                log_data["Clear"] += 1
            elif "NO FACE DETECTED" in line:
                log_data["No Face Detected"] += 1
            
    
    proc.wait()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    subprocess.run(['python', 'register.py'])
    session['registered'] = True
    return redirect(url_for('home'))

@app.route('/start_test', methods=['POST'])
def start_test():
    if not session.get('registered'):
        return redirect(url_for('home'))
    proctoring_thread = threading.Thread(target=run_proctoring, daemon=True)
    proctoring_thread.start()
    return redirect(url_for('test_page'))

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/end_test', methods=['POST'])
def end_test():
    with log_lock:
        return jsonify(log_data)

if __name__ == '__main__':
    app.run(debug=True)
