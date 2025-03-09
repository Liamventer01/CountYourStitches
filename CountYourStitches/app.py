import json
from flask import Flask, render_template, request, jsonify
import webbrowser
from threading import Timer
import os

app = Flask(__name__)

# File to store the stitch and row data
DATA_FILE = "counter_data.json"
AUTO_INCREASE_FILE = "auto_increase.txt"

# Load saved data from file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"stitch_count": 0, "row_count": 0, "stitches_per_row": 0}

# Save data to file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

# Initialize data
data = load_data()
stitch_count = data["stitch_count"]
row_count = data["row_count"]
stitches_per_row = data["stitches_per_row"]

@app.route('/')
def home():
    return render_template('index.html', stitch_count=stitch_count, row_count=row_count, stitches_per_row=stitches_per_row)

@app.route('/popout')
def popout():
    return render_template('popout.html', stitch_count=stitch_count, row_count=row_count, stitches_per_row=stitches_per_row)

@app.route('/update_counts', methods=['POST'])
def update_counts():
    global stitch_count, row_count, stitches_per_row

    data = request.json
    action = data.get('action')

    if action == 'increment_stitch':
        if stitch_count < stitches_per_row:
            stitch_count += 1
    elif action == 'undo_stitch':
        if stitch_count > 0:
            stitch_count -= 1
    elif action == 'increment_row':
        row_count += 1
        stitch_count = 0  # Reset stitches for new row
    elif action == 'reset_rows':
        row_count = 0
        stitch_count = 0  # Reset stitches as well
    elif action == 'set_stitches_per_row':
        stitches_per_row = int(data.get('value', 0))
        stitch_count = 0  # Reset stitches
        row_count = 0  # Reset rows

    # Save new values to file
    save_data({"stitch_count": stitch_count, "row_count": row_count, "stitches_per_row": stitches_per_row})

    return jsonify({'stitch_count': stitch_count, 'row_count': row_count, 'stitches_per_row': stitches_per_row})

@app.route('/get_auto_increase', methods=['GET'])
def get_auto_increase():
    """ Returns whether the Auto-Increase checkbox is enabled (from the main page). """
    try:
        with open(AUTO_INCREASE_FILE, "r") as file:
            return jsonify(file.read().strip() == "true")  # Return True/False
    except FileNotFoundError:
        return jsonify(False)  # Default to False if the file doesn't exist

@app.route('/save_auto_increase', methods=['POST'])
def save_auto_increase():
    """ Saves the auto-increase checkbox setting to a file. """
    data = request.json
    auto_increase = "true" if data.get("auto_increase", False) else "false"

    with open(AUTO_INCREASE_FILE, "w") as file:
        file.write(auto_increase)

    return jsonify({"status": "saved"})

@app.route('/get_stitches_per_row', methods=['GET'])
def get_stitches_per_row():
    """ Returns the stitches per row value """
    data = load_data()
    return jsonify({"stitches_per_row": data["stitches_per_row"]})

# Function to open the browser automatically
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    Timer(1, open_browser).start()  # Delay opening the browser by 1 second
    app.run(debug=True, host='127.0.0.1', port=5000)
