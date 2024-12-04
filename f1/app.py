from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import json

app = Flask(__name__)

# Configuration for file storage and text history
HISTORY_FILE = 'text_history.json'
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to load the last 10 text entries from the history file
def load_text_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as file:
            history = json.load(file)
    else:
        history = []
    return history[-10:][::-1]  # Last 10 entries in reverse order

# Index route to render HTML with file list and latest text entry
@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    text_history = load_text_history()
    latest_text = text_history[0] if text_history else ""
    return render_template('index.html', files=files, latest_text=latest_text, text_history=text_history)

# Route for uploading files and saving new text entries
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    elif 'shared_text' in request.form:
        new_text = request.form['shared_text']
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as file:
                history = json.load(file)
        else:
            history = []
        history.append(new_text)
        with open(HISTORY_FILE, 'w') as file:
            json.dump(history, file)
    return redirect(url_for('index'))

# Route to download files
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Route to delete files
@app.route('/delete_file', methods=['POST'])
def delete_file():
    filename = request.form['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify(success=True)

# Route to get specific text entry from history
@app.route('/get_text_history', methods=['POST'])
def get_text_history():
    index = int(request.form['index'])
    text_history = load_text_history()
    if 0 <= index < len(text_history):
        return jsonify(text=text_history[index])
    return jsonify(text="")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5080)
