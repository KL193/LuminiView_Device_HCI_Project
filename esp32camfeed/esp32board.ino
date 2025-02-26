#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_SSD1306.h>
#include <VL53L0X.h>
#include <BH1750.h>

// OLED Display settings
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1  
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// VL53L0X Distance Sensor
VL53L0X sensor;

// BH1750 Light Sensor
BH1750 lightMeter;

// WiFi Credentials
const char *ssid = "Galaxy A034811";
const char *password = "jajh4371";

// API URL
const char* api_url = "http://52.140.5.249:3000/status";

// Timing Variables
unsigned long lastSensorUpdate = 0;
unsigned long lastAPIUpdate = 0;
const unsigned long sensorInterval = 500;    // Update sensor every 500ms
const unsigned long apiInterval = 20000;     // Fetch API every 20s

// API Status Message
String apiStatusMessage = "Loading...";

// Buzzer Pin
#define BUZZER_PIN 4  
bool buzzerOn = false;
uint16_t lastValidDistance = 30;
bool firstValidReading = false;

// Sensor thresholds
const uint16_t DISTANCE_MIN_SAFE = 15;
const float LIGHT_MIN_SAFE = 50;
const float LIGHT_MAX_SAFE = 2000;

// Device status tracking
bool oledInitialized = false;
bool distanceSensorInitialized = false;
bool lightSensorInitialized = false;

void setup() {
    Serial.begin(115200);
    Wire.begin();

    // Initialize OLED Display
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("OLED Initialization Failed!");
        oledInitialized = false;
    } else {
        oledInitialized = true;
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(WHITE);
        display.setCursor(10, 10);
        display.println("Connecting to WiFi...");
        display.display();
    }

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");
    
    // Initialize VL53L0X Sensor
    sensor.setTimeout(500);
    if (!sensor.init()) {
        Serial.println("VL53L0X Initialization Failed!");
        distanceSensorInitialized = false;
    } else {
        distanceSensorInitialized = true;
        sensor.setMeasurementTimingBudget(200000);
    }

    // Initialize BH1750 Sensor
    if (!lightMeter.begin()) {
        Serial.println("BH1750 Initialization Failed!");
        lightSensorInitialized = false;
    } else {
        lightSensorInitialized = true;
    }

    // Initialize Buzzer
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    Serial.println("Setup Complete");
}

// Function to Read and Display Sensor Data
void updateSensorData() {
    uint16_t distance = 0;
    float lightLevel = 0;
    
    if (distanceSensorInitialized) {
        distance = sensor.readRangeSingleMillimeters() / 10;
        if (sensor.timeoutOccurred() || distance > 200) {
            if (firstValidReading) {
                distance = lastValidDistance;
            } else {
                distance = DISTANCE_MIN_SAFE + 5;
            }
        } else {
            lastValidDistance = distance;
            firstValidReading = true;
        }
    } else {
        distance = DISTANCE_MIN_SAFE + 10;
    }

    if (lightSensorInitialized) {
        lightLevel = lightMeter.readLightLevel();
    } else {
        lightLevel = LIGHT_MIN_SAFE + 50;
    }

    bool distanceSafe = (distance >= DISTANCE_MIN_SAFE);
    bool lightSafe = (lightLevel >= LIGHT_MIN_SAFE && lightLevel <= LIGHT_MAX_SAFE);
    bool buzzerTrigger = distanceSafe && lightSafe;

    if (oledInitialized) {
        display.clearDisplay();
        display.setTextSize(1);
        display.setCursor(0, 0);

        display.print("Dist: ");
        display.print(distance);
        display.println(" cm");
        display.println(distanceSafe ? "Distance OK" : "Too Close!");

        display.setCursor(0, 25);
        display.print("Light: ");
        display.print(lightLevel);
        display.println(" lux");
        display.println(lightSafe ? "Light OK" : (lightLevel < LIGHT_MIN_SAFE ? "Low Light" : "Too Bright"));

        display.setCursor(0, 50);
        display.print("Alert: ");
        display.println(apiStatusMessage);

        display.display();
    }

    if (buzzerTrigger) { 
        digitalWrite(BUZZER_PIN, HIGH);
        buzzerOn = true;
    } else { 
        digitalWrite(BUZZER_PIN, LOW);
        buzzerOn = false;
    }
}

// Function to Fetch and Process API Status
void fetchAPIStatus() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(api_url);
        int httpResponseCode = http.GET();

        if (httpResponseCode > 0) {
            String payload = http.getString();
            Serial.println("API Response: " + payload);

            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);

            int status = doc["status"];
            if (status == 1) {
                apiStatusMessage = "Get Rest!";
            } else {
                apiStatusMessage = "All Good!";
            }
        } else {
            Serial.println("Error in HTTP request");
            apiStatusMessage = "API Error!";
        }
        http.end();
    } else {
        Serial.println("WiFi Disconnected!");
        apiStatusMessage = "No WiFi!";
    }
}

void loop() {
    if (millis() - lastSensorUpdate >= sensorInterval) {
        lastSensorUpdate = millis();
        updateSensorData();
    }
    
    if (millis() - lastAPIUpdate >= apiInterval) {
        lastAPIUpdate = millis();
        fetchAPIStatus();
    }
}
