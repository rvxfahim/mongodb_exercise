from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from pymongo import MongoClient
from datetime import datetime, timedelta
import threading
import time
import json
from bson import json_util

app = Flask(__name__)
app.config['SECRET_KEY'] = 'monitor-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB connection
client = MongoClient('localhost', 27017)
db = client['system_monitoring']

# Store last known state to detect changes
last_counts = {}

def monitor_database():
    """
    Background thread that monitors database for new entries
    """
    global last_counts
    
    while True:
        try:
            # Get current count for each student
            pipeline = [
                {'$group': {
                    '_id': '$ID',
                    'count': {'$sum': 1},
                    'last_entry': {'$last': '$$ROOT'}
                }}
            ]
            
            results = list(db.metrics.aggregate(pipeline))
            
            for result in results:
                student_id = result['_id']
                count = result['count']
                
                # Check if this student has new data
                if student_id not in last_counts or last_counts[student_id] < count:
                    last_counts[student_id] = count
                    
                    # Emit the new data
                    last_entry = result['last_entry']
                    socketio.emit('new_data', {
                        'CPU': last_entry['CPU'],
                        'RAM': last_entry['RAM'],
                        'Temperature': last_entry['Temperature'],
                        'ID': last_entry['ID'],
                        'timestamp': last_entry['timestamp'].isoformat()
                    })
            
            time.sleep(0.5)  # Check every 500ms
            
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(1)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/students')
def get_students():
    """Get list of active students (those who submitted in last 5 minutes)"""
    try:
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        students = db.metrics.distinct('ID', {
            'timestamp': {'$gte': five_min_ago}
        })
        return jsonify(sorted(students))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/<int:student_id>')
def get_student_data(student_id):
    """Get recent data for a specific student"""
    try:
        # Get last 50 entries
        data_from_db = list(db.metrics.find(
            {'ID': student_id},
            {'_id': 0}
        ).sort('timestamp', -1).limit(50))
        
        # Reverse to get chronological order (oldest to newest)
        data_from_db.reverse()
        
        # Convert datetime objects to ISO strings for client-side compatibility
        # The client's `new Date(entry.timestamp)` expects a string or number,
        # not a potential `{"$date": "..."}` object from default json_util behavior for datetimes.
        processed_data = []
        for record in data_from_db:
            # Create a new dictionary for the processed record
            # This ensures that if 'timestamp' is the only field needing conversion,
            # other fields are copied as is.
            current_record = record.copy() # Start with a copy of the original record
            if 'timestamp' in current_record and isinstance(current_record['timestamp'], datetime):
                current_record['timestamp'] = current_record['timestamp'].isoformat()
            processed_data.append(current_record)
        
        # Use json.dumps. If there were other BSON types json_util.default was handling,
        # this approach assumes they are not present or are handled by direct conversion.
        # Given the schema (ID, CPU, RAM, Temp, timestamp), after converting timestamp to string,
        # all fields are standard JSON types.
        return json.dumps(processed_data, default=json_util.default)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get database statistics"""
    try:
        stats = {
            'total_documents': db.metrics.count_documents({}),
            'active_students': len(db.metrics.distinct('ID')),
            'last_minute': db.metrics.count_documents({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=1)}
            })
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validation_errors')
def get_validation_errors():
    """
    Check system log for validation errors
    This helps instructor see what mistakes students are making
    """
    # In production, you'd parse MongoDB logs
    # For now, return common error patterns
    return jsonify({
        'common_errors': [
            'Document failed validation: CPU must be string',
            'Document failed validation: RAM exceeds maximum value',
            'Document failed validation: Missing required field timestamp',
            'Document failed validation: ID must be 7-digit number'
        ]
    })

if __name__ == '__main__':
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_database, daemon=True)
    monitor_thread.start()
    
    print("Starting monitoring service on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)