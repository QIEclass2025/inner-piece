from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import SOSRecord, MentalRecord, save_record, load_records, delete_record, QUESTION_BANK
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sos')
def sos():
    return render_template('sos.html')

@app.route('/api/save_sos', methods=['POST'])
def api_save_sos():
    data = request.json
    # data expects: { 'course': '...', 'memo': '...', 'grounding': {...} }
    record_dict = {
        "type": "SOS",
        "date": data.get('date'), # generated in frontend or fallback? Better to let model generate date or use backend time.
                                  # Model generates date in __init__ but we are reconstructing.
                                  # Let's create object to use its date logic or just manually construct dict if passing raw.
                                  # Models.py classes set date on init.
    }
    # It's cleaner to use the class to generate a fresh record with current server time
    record = SOSRecord(
        course=data.get('course'),
        memo=data.get('memo'),
        grounding=data.get('grounding')
    )
    if save_record(record.to_dict()):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 500

@app.route('/abcde')
def abcde():
    # Pass a random question for the D stage
    question = random.choice(QUESTION_BANK)
    return render_template('abcde.html', initial_question=question)

@app.route('/api/get_question', methods=['GET'])
def get_question():
    return jsonify({"question": random.choice(QUESTION_BANK)})

@app.route('/api/save_abcde', methods=['POST'])
def api_save_abcde():
    data = request.json
    record = MentalRecord(
        adversity=data.get('adversity'),
        belief=data.get('belief'),
        consequence=data.get('consequence'),
        disputation=data.get('disputation'),
        effect=data.get('effect'),
        memo=data.get('memo')
    )
    if save_record(record.to_dict()):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 500

@app.route('/api/delete_record/<string:record_id>', methods=['DELETE'])
def api_delete_record(record_id):
    if delete_record(record_id):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Record not found"}), 404

@app.route('/history')
def history():
    records = load_records()
    # Sort by date descending
    records.sort(key=lambda x: x.get('date', ''), reverse=True)
    return render_template('history.html', records=records)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
