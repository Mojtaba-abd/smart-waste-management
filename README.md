Smart Waste Management System
Project Overview

The Smart Waste Management System is an IoT and AI-integrated solution designed to optimize municipal waste collection. By utilizing real-time sensor data, machine learning predictions, and dynamic route optimization algorithms, this system reduces operational costs, fuel consumption, and overflow incidents.

The system consists of three main components:

    Hardware: IoT nodes (ESP32) that measure bin fill levels and transmit data to the cloud.

    Machine Learning (Backend): A Python-based engine that predicts future fill levels and calculates optimal collection routes using the Traveling Salesman Problem (TSP) algorithm.

    Frontend (Dashboard): A responsive Vue.js web application for monitoring bins, visualizing routes on a map, and controlling the optimization engine.

Project Structure
Plaintext

smart-waste-management/
├── frontend/ # Vue.js 3 + Vite Dashboard application
├── ml/ # Python scripts for ML, Routing, and Flask API
└── hardware/ # C++ code for ESP32 and Ultrasonic Sensors

Features

    Real-time Monitoring: Live visualization of bin status, battery levels, and location on an interactive map.

    Intelligent Routing: Dynamic generation of collection routes based on bin urgency and physical location using Google OR-Tools.

    Predictive Analytics: Machine learning models (Linear Regression/Random Forest) to forecast when bins will become full.

    Status Alerts: Automated classification of bins into Normal, Warning, and Critical states based on fill percentage.

    Hybrid Visualization: Map overlay showing both bin status markers and the active optimization route path.

Technology Stack
Frontend

    Framework: Vue.js 3 (Composition API)

    Build Tool: Vite

    Styling: Tailwind CSS, Shadcn UI

    Mapping: Leaflet.js

    Database Integration: Firebase Web SDK

Machine Learning & Backend

    Language: Python 3.x

    Server: Flask (REST API)

    Optimization: Google OR-Tools (Constraint Solver for TSP)

    Data Processing: Pandas, NumPy, Scikit-learn

    Database Integration: Firebase Admin SDK

Hardware

    Microcontroller: ESP32

    Sensors: HC-SR04 Ultrasonic Sensor

    Connectivity: WiFi / HTTPS to Firebase Realtime Database

Installation and Setup
Prerequisites

    Node.js (v16+)

    Python (v3.9+)

    Arduino IDE or PlatformIO

    A Firebase project with Realtime Database enabled

1. Database Configuration

   Create a project in the Firebase Console.

   Enable Realtime Database.

   Generate a Service Account Private Key (JSON file) from Project Settings > Service Accounts.

   Get your Web App Config (API Key, App ID, etc.) from Project Settings > General.

2. Machine Learning Backend Setup

Navigate to the ml directory:
Bash

cd ml

Create a virtual environment and install dependencies:
Bash

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Note: Ensure you place your serviceAccountKey.json file inside the ml/ directory.

Run the API server:
Bash

python api.py

The server will start on http://127.0.0.1:5000. 3. Frontend Dashboard Setup

Navigate to the frontend directory:
Bash

cd frontend

Install dependencies:
Bash

npm install

Configure environment variables: Create a .env file in the frontend root and add your Firebase credentials:
مقتطف الرمز

VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=your_database_url
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

Run the development server:
Bash

npm run dev

Access the dashboard at http://localhost:5173. 4. Hardware Setup

    Open the code in hardware/ using Arduino IDE or PlatformIO.

    Update the WiFi credentials and Firebase host/auth tokens in the code.

    Connect the HC-SR04 sensor to the ESP32:

        VCC -> 5V

        GND -> GND

        Trig -> GPIO 5

        Echo -> GPIO 18

    Upload the code to the ESP32.

API Reference

The Python backend exposes the following endpoints for the frontend to trigger logic manually:

    POST /run-optimization

        Triggers the TSP algorithm to calculate the optimal route for critical bins.

        Updates /routes in Firebase.

    POST /run-inference

        Triggers the ML model to predict "Time to Full" for all bins based on historical data.

        Updates /predictions in Firebase.

Contact

Team Enki

    Mujtaba Abdulmuttalib  - Lead Developer & Architect

    Hussein Ali - Hardware & IoT Specialist

    Mustafa Safa - Hardware & IoT Specialist

    Zainab Haidar  - Project Manager & Research

Institution: University of Babylon, College of IT.
