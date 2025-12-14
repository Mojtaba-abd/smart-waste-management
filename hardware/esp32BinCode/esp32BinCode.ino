// ----------------------------------------------------------------------
// Smart Waste Prototype: Bin 26 (Baghdad) - 11cm Toy Bin Version (FIXED)
// ----------------------------------------------------------------------

#include <WiFi.h>
#include <time.h>
#include "FirebaseESP32.h" 

// --- Configuration ---
#define WIFI_SSID "Ali2023"
#define WIFI_PASSWORD "20242024"

// --- Firebase Configuration ---
#define FIREBASE_HOST "smart-waste-3d7d0-default-rtdb.europe-west1.firebasedatabase.app"
#define FIREBASE_AUTH "BsclSHICRx6Ic76lP8O9vbF2JLq2wG4EwFr1Sz93" 

// --- Bin Specific Info ---
const String BIN_ID = "bin_026"; 
const float BIN_LAT = 33.3128; 
const float BIN_LON = 44.3615;
const int TRIG_PIN = 23; 
const int ECHO_PIN = 22; 
const long GMTOFFSET_SEC = 10800; 
const int DAYLIGHT_OFFSET_SEC = 0;

// --- Prototype Settings ---
const float MAX_DISTANCE_CM = 11.0; 
const unsigned long SEND_INTERVAL_MS = 5000; 

// --- Global Variables ---
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
unsigned long lastSendTime = 0;

// --- Helper Functions ---

void reconnect_wifi() {
    if (WiFi.status() == WL_CONNECTED) return;
    Serial.print("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected.");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

void setClock() {
    configTime(GMTOFFSET_SEC, DAYLIGHT_OFFSET_SEC, "pool.ntp.org", "time.nist.gov");
    Serial.println("Waiting for NTP time sync...");
    time_t nowSecs = time(nullptr);
    while (nowSecs < 10000) {
        delay(500);
        Serial.print(".");
        nowSecs = time(nullptr);
    }
    struct tm timeinfo;
    gmtime_r(&nowSecs, &timeinfo);
    Serial.printf("\nCurrent Time: %s", asctime(&timeinfo));
}

float read_fill_level() {
    // 1. Trigger the sensor
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // 2. Read the Echo
    long duration = pulseIn(ECHO_PIN, HIGH);
    
    // 3. Convert to cm
    float distanceCm = duration * 0.0343 / 2;

    // --- FIX STARTS HERE ---
    // If distance is 0, the sensor didn't read anything (Wiring error or Out of Range)
    // We should treat this as 0% fill (Empty) or maintain previous state, not 100% full.
    if (distanceCm == 0 || distanceCm > 1000) {
        Serial.println("Error: Sensor returned 0cm (Check VCC/GND/Pins). Returning 0% Fill.");
        return 0.0;
    }

    // If the distance is GREATER than the bin height (e.g. 15cm), it means it's empty.
    if (distanceCm > MAX_DISTANCE_CM) {
        distanceCm = MAX_DISTANCE_CM;
    }
    // --- FIX ENDS HERE ---

    // 4. Calculate Fill % 
    float fillLevel = ((MAX_DISTANCE_CM - distanceCm) / MAX_DISTANCE_CM) * 100.0;

    // 5. Clamp values
    if (fillLevel < 0) fillLevel = 0;     
    if (fillLevel > 100) fillLevel = 100; 

    Serial.printf("Dist: %.1f cm | Fill: %.1f%%\n", distanceCm, fillLevel);
    return fillLevel;
}

void push_data_to_firebase(float fillLevel) {
    reconnect_wifi(); 
    time_t nowSecs = time(nullptr);
    String timestamp = String(nowSecs); 

    FirebaseJson data;
    data.set("fill_level", String(fillLevel, 2));
    data.set("latitude", String(BIN_LAT, 6));
    data.set("longitude", String(BIN_LON, 6));
    data.set("timestamp", timestamp);

    String currentPath = "/bins/" + BIN_ID;
    
    if (Firebase.setJSONAsync(fbdo, currentPath.c_str(), data)) { 
        Serial.printf("Pushed Current Data to %s\n", currentPath.c_str());
    } else {
        Serial.printf("Failed Current: %s\n", fbdo.errorReason().c_str());
    }

    String historyPath = "/history/" + BIN_ID + "/" + timestamp;
    if (Firebase.setJSONAsync(fbdo, historyPath.c_str(), data)) { 
        Serial.println("History Saved.");
    }
}

// ----------------------------------------------------------------------
// Setup and Loop
// ----------------------------------------------------------------------

void setup() {
    Serial.begin(115200);
    
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    reconnect_wifi();
    setClock();

    config.database_url = FIREBASE_HOST; 
    config.signer.tokens.legacy_token = FIREBASE_AUTH; 

    Firebase.begin(&config, &auth); 
    fbdo.setResponseSize(1024);
    Firebase.reconnectWiFi(false); 

    Serial.println("Setup Complete.");
}

void loop() {
    if (millis() - lastSendTime > SEND_INTERVAL_MS) {
        lastSendTime = millis();
        float fillLevel = read_fill_level();
        push_data_to_firebase(fillLevel);
    }
    delay(10); 
}