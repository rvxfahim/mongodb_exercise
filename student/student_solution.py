"""
MongoDB Direct Connection Exercise
==================================

Your task: Complete this script to collect system information and 
store it in MongoDB with a 1Hz sampling rate.

Requirements:
1. Connect to MongoDB server (connection info will be provided)
2. Collect: CPU model, RAM (bytes), Temperature, Student ID
3. Insert data with proper format and timestamp
4. Handle errors gracefully
5. Maintain 1Hz sampling rate

MongoDB Document Format:
{
    'CPU': string (3-100 characters),
    'RAM': integer (bytes),
    'Temperature': integer (0-150),
    'ID': integer (your 7-digit student ID),
    'timestamp': datetime object
}
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, WriteError
from datetime import datetime
import time
import platform
import psutil
import random

# TODO: Replace with your student ID (7-digit number)
STUDENT_ID = 1234567

# TODO: Replace with instructor-provided connection info
MONGODB_HOST = "localhost"  # or instructor's IP address
MONGODB_PORT = 27017
DATABASE_NAME = "system_monitoring"
COLLECTION_NAME = "metrics"

def get_system_info():
    """
    Collects system information including CPU model, RAM, temperature, and student ID.
    
    Returns:
        dict: System information with keys: CPU, RAM, Temperature, ID
    """
    try:
        # Get CPU information
        cpu_info = platform.processor()
        # If CPU info is too short, use a more detailed method
        if len(cpu_info) < 3:
            cpu_info = platform.machine() + " " + platform.processor()
        
        # Make sure CPU string is within the required length (3-100 characters)
        cpu_info = cpu_info[:100] if len(cpu_info) > 100 else cpu_info
        if len(cpu_info) < 3:
            cpu_info = "Unknown CPU Model"
            
        # Get RAM in bytes
        ram_bytes = psutil.virtual_memory().total
        
        # Simulate temperature reading (between 40-80 degrees)
        temperature = random.randint(40, 80)
        
        return {
            'CPU': cpu_info,
            'RAM': ram_bytes,
            'Temperature': temperature,
            'ID': STUDENT_ID
        }
    except Exception as e:
        print(f"Error collecting system information: {e}")
        # Return default values in case of error
        return {
            'CPU': "Error retrieving CPU info",
            'RAM': 0,
            'Temperature': 50,
            'ID': STUDENT_ID
        }

def connect_to_mongodb():
    """
    Connects to MongoDB server using the provided connection information.
    
    Returns:
        collection: MongoDB collection object or None if connection fails
    """
    try:
        # Create a MongoDB client
        client = MongoClient(MONGODB_HOST, MONGODB_PORT, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        # Get database and collection
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        return collection
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error when connecting to MongoDB: {e}")
        return None

def insert_data(collection, data):
    """
    Inserts system information data into MongoDB with timestamp.
    
    Args:
        collection: MongoDB collection object
        data: Dictionary containing system information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add current timestamp to the data
        data['timestamp'] = datetime.now()
        
        # Insert the document
        result = collection.insert_one(data)
        
        # Check if insertion was successful
        return result.acknowledged
    except WriteError as e:
        print(f"MongoDB write error: {e}")
        return False
    except OperationFailure as e:
        print(f"MongoDB operation failure: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during data insertion: {e}")
        return False

def main():
    """
    Main loop - runs at 1Hz
    """
    print(f"Starting system monitoring for Student ID: {STUDENT_ID}")
    
    # Connect to MongoDB
    collection = connect_to_mongodb()
    
    if collection is None:
        print("Failed to connect to MongoDB!")
        return
    
    print("Connected to MongoDB successfully!")
    print("Starting data collection...")
    
    # Success and failure counters for statistics
    success_count = 0
    failure_count = 0
    
    while True:
        try:
            # Collect system information
            system_info = get_system_info()
            
            # Insert into MongoDB
            if insert_data(collection, system_info):
                success_count += 1
                print(f"Data inserted successfully. Total: {success_count} (Failures: {failure_count})")
            else:
                failure_count += 1
                print(f"Failed to insert data. Total failures: {failure_count}")
            
            # Wait 1 second (1Hz)
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            print(f"Summary: {success_count} successful insertions, {failure_count} failures")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            failure_count += 1
            time.sleep(1)

if __name__ == "__main__":
    main()
