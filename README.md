# MongoDB System Monitoring Exercise

## Overview

This exercise is designed to help you learn MongoDB by implementing a real-time system monitoring application. You will write a Python script that collects system information (CPU, RAM, Temperature) from your computer and stores it in a MongoDB database. The server side of the application will display this data on a real-time dashboard.

## Learning Objectives

- Connect to a MongoDB database using PyMongo
- Create and insert documents with proper validation
- Implement error handling for database operations
- Work with real-time data collection and processing
- Understand MongoDB schema validation

## Exercise Structure

The repository is organized as follows:

```
mongodb_exercise/
├── README.md               # This file
├── server/                 # Instructor-provided monitoring server
│   ├── monitor_service.py  # Flask server for dashboard
│   ├── requirements.txt    # Server dependencies
│   ├── setup_mongodb.py    # MongoDB setup script
│   └── templates/          # Web dashboard templates
│       └── dashboard.html  # Dashboard UI
└── student/                # Your working directory
    ├── requirements.txt    # Student script dependencies
    ├── student_solution.py # Your solution (to be completed)
    └── student_template.py # Template to start with
```

## Getting Started

### Prerequisites

- Python 3.6+
- MongoDB Server (must be running)

### Setup

1. **Install MongoDB Server** (if not already installed):
   
   For Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install -y mongodb
   sudo systemctl enable mongodb
   sudo systemctl start mongodb
   ```

   For other OS, follow the [official MongoDB installation guide](https://docs.mongodb.com/manual/installation/).

2. **Set up the Python environment**:
   
   ```bash
   # Install student requirements
   cd mongodb_exercise/student
   pip install -r requirements.txt
   
   # Install server requirements (for running the dashboard)
   cd ../server
   pip install -r requirements.txt
   ```

3. **Initialize the MongoDB database**:
   
   ```bash
   # This will create the database and set up the required collection with validation
   cd mongodb_exercise/server
   python setup_mongodb.py
   ```

## Your Task

1. **Copy the template to start your solution**:
   
   ```bash
   cd mongodb_exercise/student
   cp student_template.py student_solution.py
   ```

2. **Complete the implementation** in `student_solution.py`:
   - Connect to the MongoDB server
   - Collect system information (CPU, RAM, Temperature)
   - Insert data with proper format and timestamp
   - Handle errors gracefully
   - Maintain a 1Hz sampling rate (one sample per second)

### Required Document Format

Your script must insert documents in this format:
```python
{
    'CPU': string (3-100 characters),                   # e.g., "Intel Core i7-9750H"
    'RAM': integer (bytes),                             # e.g., 17179869184 (16GB)
    'Temperature': integer (0-150),                     # e.g., 65
    'ID': integer (your 7-digit imaginary student ID),  # e.g., 1234567
    'timestamp': datetime object                        # e.g., datetime.utcnow()
}
```

MongoDB will validate your documents against this schema. If your data doesn't match the requirements, the insertion will fail.

## Running the Dashboard

To visualize your data and verify your solution is working:

1. **Start the MongoDB server** (if not already running)
2. **Run your solution script**:
   ```bash
   cd mongodb_exercise/student
   python student_solution.py
   ```
3. **In a separate terminal, run the monitoring server**:
   ```bash
   cd mongodb_exercise/server
   python monitor_service.py
   ```
4. **Open a web browser** and navigate to:
   ```
   http://localhost:5000
   ```

You should see your system metrics displayed in real-time on the dashboard.

## Tips and Hints

1. **MongoDB Connection**: Use `pymongo.MongoClient` to connect to MongoDB.
2. **System Information**: 
   - Use `platform.processor()` for CPU information
   - Use `psutil.virtual_memory().total` for RAM in bytes
   - For temperature, you can simulate values if your system doesn't provide them
3. **Error Handling**: Wrap MongoDB operations in try-except blocks to handle connection issues
4. **Timing**: Use `time.sleep(1)` to maintain the 1Hz sampling rate

## Submission

Your completed `student_solution.py` file should:
1. Successfully connect to MongoDB
2. Collect and insert valid system metrics data
3. Run continuously at 1Hz until manually stopped
4. Handle errors without crashing

## Resources

- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [psutil Documentation](https://psutil.readthedocs.io/)