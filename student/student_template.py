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
    'ID': integer (your 4-digit student ID),
    'timestamp': datetime object
}
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, WriteError
from datetime import datetime
import time
import platform
import psutil

# TODO: Replace with your student ID (4-digit number)
STUDENT_ID = 1234

# TODO: Replace with instructor-provided connection info
MONGODB_HOST = "localhost"  # or instructor's IP address
MONGODB_PORT = 27017
DATABASE_NAME = "system_monitoring"
COLLECTION_NAME = "metrics"

def get_system_info():
    """
    TODO: Implement this function to collect system information
    
    Returns:
        dict: System information with keys: CPU, RAM, Temperature, ID
    """
    # Hint: Use platform and psutil modules
    # For temperature, you can simulate it with random values (40-80)
    pass

def connect_to_mongodb():
    """
    TODO: Implement this function to connect to MongoDB
    
    Returns:
        collection: MongoDB collection object or None if connection fails
    """
    # Hint: Use try-except to handle connection errors
    pass

def insert_data(collection, data):
    """
    TODO: Implement this function to insert data into MongoDB
    
    Args:
        collection: MongoDB collection object
        data: Dictionary containing system information
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Hint: Don't forget to add timestamp!
    # Hint: Handle validation errors from MongoDB
    pass

def main():
    """
    Main loop - runs at 1Hz
    """
    print(f"Starting system monitoring for Student ID: {STUDENT_ID}")
    
    # TODO: Connect to MongoDB
    collection = None  # Replace with your connection
    
    if collection is None:
        print("Failed to connect to MongoDB!")
        return
    
    print("Connected to MongoDB successfully!")
    print("Starting data collection...")
    
    while True:
        try:
            # TODO: Collect system information
            
            # TODO: Insert into MongoDB
            
            # TODO: Print success/failure message
            
            # Wait 1 second (1Hz)
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()