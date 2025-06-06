from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
import sys
import os
import platform
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
    """Checks if the MongoDB service is active on both Windows and Linux systems."""
    system = platform.system()
    
    if system == "Windows":
        # Windows: Check if MongoDB service is running using Windows SC command
        try:
            result = subprocess.run(['sc', 'query', 'MongoDB'],
                                   capture_output=True,
                                   text=True,
                                   check=False)
            # If SC returns 0 and "RUNNING" is in the output, the service is running
            return result.returncode == 0 and "RUNNING" in result.stdout
        except FileNotFoundError:
            # SC command not found or not accessible
            print("Warning: Cannot check MongoDB service status using Windows SC command.")
            # Try connecting to MongoDB directly as a fallback
            try:
                # Simple connection test
                client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
                client.admin.command('ping')  # Will raise exception if server is not available
                return True
            except Exception:
                print("Could not connect to MongoDB server.")
                return False
        except Exception as e:
            print(f"An error occurred while checking MongoDB status: {e}")
            return False
    else:
        # Linux: Use systemctl if available
        try:
            # systemctl is-active returns 0 if active, non-zero otherwise.
            result = subprocess.run(['systemctl', 'is-active', 'mongod'],
                                    capture_output=True,
                                    text=True,
                                    check=False)
            return result.returncode == 0
        except FileNotFoundError:
            # systemctl not found, try using ps as fallback
            try:
                result = subprocess.run(['ps', '-A'],
                                       capture_output=True,
                                       text=True)
                return 'mongod' in result.stdout
            except:
                # If ps also fails, try direct connection
                try:
                    client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
                    client.admin.command('ping')
                    return True
                except Exception:
                    print("Could not verify if MongoDB is running through any method.")
                    return False
        except Exception as e:
            print(f"An error occurred while checking MongoDB status: {e}")
            return False

def start_mongodb_service():
    """Attempts to start the MongoDB service on both Windows and Linux systems."""
    system = platform.system()
    
    if system == "Windows":
        print("Attempting to start MongoDB service on Windows...")
        try:
            # On Windows, use the NET START command with administrative privileges
            # The /y flag suppresses confirmation prompts
            process = subprocess.run(['net', 'start', 'MongoDB'],
                                     capture_output=True,
                                     text=True,
                                     timeout=30)  # 30s timeout
            
            if process.returncode == 0:
                print("MongoDB service start command executed successfully.")
                return True
            elif "already been started" in process.stderr:
                # Already running is still a success case
                print("MongoDB service is already running.")
                return True
            else:
                print(f"✗ Failed to start MongoDB service using 'net start MongoDB'.")
                print(f"  Return code: {process.returncode}")
                if process.stdout and process.stdout.strip():
                    print(f"  Stdout:\n{process.stdout.strip()}")
                if process.stderr and process.stderr.strip():
                    print(f"  Stderr:\n{process.stderr.strip()}")
                
                # Try to provide helpful information
                print("\nPossible solutions:")
                print("  1. Ensure MongoDB is installed as a Windows service")
                print("  2. Run this script as Administrator")
                print("  3. Try starting MongoDB manually:")
                print("     - From the Start menu, search for 'Services'")
                print("     - Find MongoDB service and start it")
                print("     - Or run 'mongod.exe' directly from the MongoDB bin folder")
                return False
                
        except FileNotFoundError:
            print("Warning: 'net' command not found. Cannot start MongoDB service automatically.")
            print("Please ensure MongoDB is running manually.")
            return False
        except subprocess.TimeoutExpired:
            print("Timeout occurred while trying to start MongoDB service.")
            print("Please ensure MongoDB is running manually or run this script with administrative privileges.")
            return False
        except Exception as e:
            print(f"An error occurred while trying to start MongoDB: {e}")
            return False
    else:
        # Linux
        print("Attempting to start MongoDB service (mongod)...")
        print("This may require sudo privileges. If prompted, please enter your password.")
        try:
            process = subprocess.run(['sudo', 'systemctl', 'start', 'mongod'],
                                     capture_output=True, text=True, timeout=30)
            
            if process.returncode == 0:
                print("MongoDB service start command executed.")
                return True
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
            # Try using the service command if systemctl is not available
            try:
                process = subprocess.run(['sudo', 'service', 'mongod', 'start'],
                                        capture_output=True, text=True, timeout=30)
                if process.returncode == 0:
                    print("MongoDB service start command executed using 'service'.")
                    return True
                else:
                    print("Failed to start MongoDB using both 'systemctl' and 'service' commands.")
                    print("Please start MongoDB manually.")
                    return False
            except:
                print("Warning: Neither 'systemctl' nor 'service' commands are available.")
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
    system = platform.system()
    print(f"Detected operating system: {system}")
    
    if not is_mongodb_running():
        print("MongoDB service is not detected or not active.")
        if start_mongodb_service():
            print("Waiting a few seconds for MongoDB to initialize...")
            time.sleep(5)  # Wait for 5 seconds
            if not is_mongodb_running():
                print("✗ Failed to start MongoDB service or it's not responsive after the start command.")
                
                if system == "Windows":
                    print("  Please check if MongoDB is installed as a Windows service.")
                    print("  You can check the service status in the Services application.")
                    print("  Alternatively, you can try starting MongoDB manually:")
                    print("  - Run the MongoDB executable directly from its installation directory")
                    print("  - Typically: C:\\Program Files\\MongoDB\\Server\\<version>\\bin\\mongod.exe")
                else:
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
        print("✓ MongoDB service is active.")

    # Allow custom host if provided
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    setup_database(host=host)