from flask import Flask, render_template, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
import os

nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if os.path.exists(nltk_data_path):
    nltk.data.path.append(nltk_data_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class AnalysisData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    T1 = db.Column(db.String(100), nullable=True)
    T2 = db.Column(db.String(100), nullable=True)
    T3 = db.Column(db.String(100), nullable=True)
    T4 = db.Column(db.String(100), nullable=True)
    Esc_Reason_LFFR_AllReasons = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return (f"AnalysisData(T1='{self.T1}', T2='{self.T2}', T3='{self.T3}', "
                f"T4='{self.T4}', Esc_Reason_LFFR_AllReasons='{self.Esc_Reason_LFFR_AllReasons}')")\
                
# This function creates the tables and inserts dummy data
def populate_dummy_data():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        # Create dummy records
        dummy1 = AnalysisData(T1="FreeWay End", T2="Sensor Reading", T3="Lane End", T4="Brake applied",
                                Esc_Reason_LFFR_AllReasons="ASR Failure")
        dummy2 = AnalysisData(T1="Alpha", T2="Beta", T3="Gamma", T4="Delta",
                                Esc_Reason_LFFR_AllReasons="Reason2")
        dummy3 = AnalysisData(T1="Highway Junction", T2="Lidar Detection", T3="Lane Markings Faded", T4="Speed Reduced", 
                      Esc_Reason_LFFR_AllReasons="Camera Obstruction")

        dummy4 = AnalysisData(T1="Tunnel Entry", T2="Radar Warning", T3="Lane Narrowing", T4="Steering Assist", 
                            Esc_Reason_LFFR_AllReasons="GPS Signal Loss")

        dummy5 = AnalysisData(T1="Construction Zone", T2="Ultrasonic Alert", T3="Lane Deviation", T4="Emergency Braking", 
                            Esc_Reason_LFFR_AllReasons="Sensor Calibration Error")

        dummy6 = AnalysisData(T1="Roundabout", T2="Camera Feed", T3="Lane Change", T4="Acceleration Limited", 
                            Esc_Reason_LFFR_AllReasons="Lane Prediction Failure")

        dummy7 = AnalysisData(T1="Bridge Crossing", T2="Temperature Warning", T3="Lane Merge", T4="Traction Control", 
                            Esc_Reason_LFFR_AllReasons="Environmental Conditions")

        dummy8 = AnalysisData(T1="Traffic Jam", T2="Proximity Sensor", T3="Lane Closure", T4="Autopilot Disengaged", 
                            Esc_Reason_LFFR_AllReasons="Multiple Obstacle Detection")
        # Add the records to the session
        db.session.add(dummy1)
        db.session.add(dummy2)
        db.session.add(dummy3)
        db.session.add(dummy4)
        db.session.add(dummy5)
        db.session.add(dummy6)
        db.session.add(dummy7)
        db.session.add(dummy8)
        db.session.commit()
        print("Dummy data inserted.")
    
@app.route('/', methods =[ 'GET', 'POST'])
def index():
    return render_template('index.html')

def extract_keywords(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    print(f"tagged",tagged)

    keywords = []
    phrase = []

    for word, tag in tagged:
        if tag.startswith('JJ') or tag.startswith('NN') or tag.startswith('VB'):
            phrase.append(word)
        else:
            if phrase:
                keywords.append(' '.join(phrase))
                phrase = []
    if phrase:
        keywords.append(" ".join(phrase))
    return keywords

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify(error="Invalid input"), 400
    message = data.get('message', '')
    
    # Check if the message contains an ID reference
    import re
    id_match = re.search(r'id\s+(?:number\s+)?(\d+)', message.lower())
    
    if id_match:
        # Extract the ID number
        record_id = int(id_match.group(1))
        record = AnalysisData.query.get(record_id)
        
        if record:
            # Construct a natural language explanation
            explanation = (
                f"For ID {record_id}, the escalation reason is '{record.Esc_Reason_LFFR_AllReasons}'. "
                f"This occurred in the context of '{record.T1}' (location/situation), "
                f"with '{record.T2}' providing data. "
                f"The lane condition was '{record.T3}' and the system response was '{record.T4}'."
            )
            return jsonify(status="ok", analysis=explanation), 200
        else:
            return jsonify(status="error", analysis=f"No record found with ID {record_id}."), 404
    
    # If no ID is specified, fall back to the keyword-based search
    keywords = extract_keywords(message)
    print (f"Extracted keywords: {keywords}")
    
    query = AnalysisData.query

    if keywords:
        # Combine conditions for all keywords across all columns.
        conditions = []
        for kw in keywords:
            conditions.append(AnalysisData.T1.ilike(f"%{kw}%"))
            conditions.append(AnalysisData.T2.ilike(f"%{kw}%"))
            conditions.append(AnalysisData.T3.ilike(f"%{kw}%"))
            conditions.append(AnalysisData.T4.ilike(f"%{kw}%"))
            conditions.append(AnalysisData.Esc_Reason_LFFR_AllReasons.ilike(f"%{kw}%"))
        # Filter rows that satisfy at least one of the conditions
        query = query.filter(or_(*conditions))
    
    # Execute the query and fetch results
    result_rows = query.all()
    
    # Format the results (here, we simply use __repr__ to represent each row)
    results = [repr(row) for row in result_rows]
    
    # Create a summary of the token analysis and database query results
    analysis_result = (f"Extracted keywords: {', '.join(keywords)}. "
                      f"Database query results: {results}")
    
    return jsonify(status="ok", analysis=analysis_result), 200

@app.route('/data', methods=['GET'])
def show_data():
    data = AnalysisData.query.all()
    return render_template('data.html', data=data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        if AnalysisData.query.count() == 0:
            populate_dummy_data()
    app.run()