from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
import sys
from datetime import datetime
import subprocess
import time

def setup_database(host='localhost', port=27017):
    """
    Set up MongoDB database with schema validation
    This ensures students must submit data in the correct format
    """
    client = MongoClient(host, port)
    db = client['system_monitoring']
    
    # Drop existing collection for fresh start
    try:
        db.drop_collection('metrics')
        print("Dropped existing metrics collection")
    except:
        pass
    
    # Create collection with strict validation rules
    validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['CPU', 'RAM', 'Temperature', 'ID', 'timestamp'],
            'properties': {
                '_id': {
                    'bsonType': 'objectId'
                },
                'CPU': {
                    'bsonType': 'string',
                    'minLength': 3,
                    'maxLength': 100,
                    'description': 'CPU must be a string between 3-100 characters'
                },
                'RAM': {
                    'bsonType': ['int', 'long'],
                    'minimum': 0,
                    'maximum': 1099511627776,  # 1TB in bytes
                    'description': 'RAM must be a positive integer (bytes)'
                },
                'Temperature': {
                    'bsonType': 'int',
                    'minimum': 0,
                    'maximum': 150,
                    'description': 'Temperature must be integer between 0-150'
                },
                'ID': {
                    'bsonType': 'int',
                    'minimum': 1000000,
                    'maximum': 9999999,
                    'description': 'Student ID must be 7-digit integer'
                },
                'timestamp': {
                    'bsonType': 'date',
                    'description': 'Timestamp must be a date object'
                }
            }
        }
    }
    
    try:
        db.create_collection('metrics', validator=validator)
        print("✓ Created metrics collection with validation rules")
        
        # Create indexes for better performance
        db.metrics.create_index([('ID', 1), ('timestamp', -1)])
        db.metrics.create_index('timestamp')
        print("✓ Created indexes on ID and timestamp")
        
        # Test the validation with a sample document
        test_doc = {
            'CPU': 'Intel Core i7-9750H',
            'RAM': 17179869184,  # 16GB in bytes
            'Temperature': 65,
            'ID': 1234567,
            'timestamp': datetime.utcnow()
        }
        
        result = db.metrics.insert_one(test_doc)
        print(f"✓ Validation test passed. Test document ID: {result.inserted_id}")
        
        # Remove test document
        db.metrics.delete_one({'_id': result.inserted_id})
        
        # Display connection info for students
        print("\n" + "="*60)
        print("MongoDB Server Ready for Student Connections!")
        print("="*60)
        print(f"Connection String: mongodb://{host}:{port}/")
        print(f"Database: system_monitoring")
        print(f"Collection: metrics")
        print("\nRequired document format:")
        print("{")
        print("    'CPU': 'string (3-100 chars)',")
        print("    'RAM': integer (0 to 1TB in bytes),")
        print("    'Temperature': integer (0-150),")
        print("    'ID': integer (1000000-9999999),")
        print("    'timestamp': datetime object")
        print("}")
        print("="*60)
        
    except CollectionInvalid as e:
        print(f"✗ Failed to create collection: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error during setup: {e}")
        sys.exit(1)

def is_mongodb_running():
    """Checks if the MongoDB service is active using 'systemctl is-active mongod'."""
    try:
        # systemctl is-active returns 0 if active, non-zero otherwise.
        result = subprocess.run(['systemctl', 'is-active', 'mongod'],
                                capture_output=True, # Suppress output to console
                                text=True,
                                check=False) # Don't raise for non-zero status
        return result.returncode == 0
    except FileNotFoundError:
        # systemctl not found
        print("Warning: 'systemctl' command not found. Cannot check MongoDB status automatically.")
        print("Please ensure MongoDB is running or install systemctl if you are on a systemd-based Linux.")
        return False # Indicates we couldn't confirm it's running
    except Exception as e:
        print(f"An error occurred while checking MongoDB status: {e}")
        return False

def start_mongodb_service():
    """Attempts to start the MongoDB service using 'sudo systemctl start mongod'."""
    print("Attempting to start MongoDB service (mongod)...")
    print("This may require sudo privileges. If prompted, please enter your password.")
    try:
        process = subprocess.run(['sudo', 'systemctl', 'start', 'mongod'],
                                 capture_output=True, text=True, timeout=30) # 30s timeout
        
        if process.returncode == 0:
            print("MongoDB service start command executed.")
            return True # Indicates command was issued
        else:
            print(f"✗ Failed to start MongoDB service using 'sudo systemctl start mongod'.")
            print(f"  Return code: {process.returncode}")
            if process.stdout and process.stdout.strip():
                print(f"  Stdout:\n{process.stdout.strip()}")
            if process.stderr and process.stderr.strip():
                print(f"  Stderr:\n{process.stderr.strip()}")
            print("  Please ensure 'mongod' service is correctly installed and configured.")
            print("  You may need to run this script with sudo or start MongoDB manually.")
            return False
            
    except FileNotFoundError:
        print("Warning: 'sudo' or 'systemctl' command not found. Cannot start MongoDB service automatically.")
        print("Please ensure MongoDB is running manually.")
        return False
    except subprocess.TimeoutExpired:
        print("Timeout occurred while trying to start MongoDB service.")
        print("This might happen if 'sudo' is waiting for a password.")
        print("Please ensure MongoDB is running manually or run this script with appropriate privileges.")
        return False
    except Exception as e:
        print(f"An error occurred while trying to start MongoDB: {e}")
        return False

if __name__ == "__main__":
    if not is_mongodb_running():
        print("MongoDB service (mongod) is not detected or not active.")
        if start_mongodb_service():
            print("Waiting a few seconds for MongoDB to initialize...")
            time.sleep(5)  # Wait for 5 seconds
            if not is_mongodb_running():
                print("✗ Failed to start MongoDB service or it's not responsive after the start command.")
                print("  Please check the service status manually (e.g., 'systemctl status mongod').")
                print("  Ensure MongoDB is installed correctly and can be started, then re-run the script.")
                sys.exit(1)
            else:
                print("✓ MongoDB service is now active.")
        else:
            # start_mongodb_service already prints detailed error messages
            print("Exiting due to failure to start MongoDB.")
            sys.exit(1)
    else:
        print("✓ MongoDB service (mongod) is already active.")

    # Allow custom host if provided
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    setup_database(host=host)