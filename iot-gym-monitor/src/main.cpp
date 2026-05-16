#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>
#include "config.h"

Adafruit_BME680 bme;

struct SensorReading {
    float temperature;
    float humidity;
    float pressure;
    float altitude;
    float gasResistance;
    const char* airQualityLabel;
};

bool initBME680() {
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

    bool status = bme.begin(BME680_ADDRESS);
    if (!status) {
        return false;
    }

    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);

    // Gas heater: 320°C for 150 ms
    bme.setGasHeater(320, 150);

    return true;
}

const char* classifyAirQuality(float gasResistance) {
    if (isnan(gasResistance) || gasResistance <= 0) {
        return "Unknown";
    }
    // Higher gas resistance usually indicates cleaner air.
    if (gasResistance > 50000) {
        return "Good";
    } else if (gasResistance > 20000) {
        return "Moderate";
    } else {
        return "Poor";
    }
}

SensorReading readSensors() {
    SensorReading reading;

    if (!bme.performReading()) {
        reading.temperature = NAN;
        reading.humidity = NAN;
        reading.pressure = NAN;
        reading.altitude = NAN;
        reading.gasResistance = NAN;
        reading.airQualityLabel = "Unknown";
    } else {
        reading.temperature = bme.temperature;
        reading.humidity = bme.humidity;
        reading.pressure = bme.pressure / 100.0f;
        reading.altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
        reading.gasResistance = bme.gas_resistance;
        reading.airQualityLabel = classifyAirQuality(reading.gasResistance);
    }

    return reading;
}

bool isValidReading(const SensorReading& r) {
    if (isnan(r.temperature) || isnan(r.humidity) || isnan(r.pressure)) {
        return false;
    }

    if (r.temperature < -10 || r.temperature > 60) {
        return false;
    }

    if (r.humidity < 0 || r.humidity > 100) {
        return false;
    }

    if (r.pressure < 800 || r.pressure > 1100) {
        return false;
    }

    return true;
}

void printReadings(const SensorReading& r) {
    Serial.println("---- Sensor Readings ----");
    Serial.printf("Temperature:       %.2f °C\n", r.temperature);
    Serial.printf("Humidity:          %.2f %%\n", r.humidity);
    Serial.printf("Pressure:          %.2f hPa\n", r.pressure);
    Serial.printf("Altitude:          %.2f m\n", r.altitude);
    Serial.printf("Gas resistance:    %.2f Ohms\n", r.gasResistance);
    Serial.printf("Air quality:       %s\n", r.airQualityLabel);
    Serial.println();
}

bool connectToSingleWiFi(const char* ssid, const char* password, unsigned long timeoutMs = 15000) {
    Serial.printf("Trying WiFi: %s\n", ssid);

    WiFi.disconnect(true, true);
    delay(1000);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    unsigned long startAttempt = millis();

    while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < timeoutMs) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("WiFi connected successfully!");
        Serial.printf("Connected to: %s\n", WiFi.SSID().c_str());
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        Serial.println();
        return true;
    }

    Serial.printf("Failed to connect to: %s\n\n", ssid);
    return false;
}

bool connectWiFi() {
    for (int i = 0; i < WIFI_NETWORK_COUNT; i++) {
        if (connectToSingleWiFi(WIFI_NETWORKS[i].ssid, WIFI_NETWORKS[i].password)) {
            return true;
        }
    }

    Serial.println("ERROR: Could not connect to any configured WiFi networks.");
    return false;
}

void buildJsonPayload(const SensorReading& r, String& outJson) {
    JsonDocument doc;

    doc["deviceId"] = DEVICE_ID;
    doc["temperature"] = r.temperature;
    doc["humidity"] = r.humidity;
    doc["pressure"] = r.pressure;
    doc["altitude"] = r.altitude;
    doc["gasResistance"] = r.gasResistance;
    doc["airQualityLabel"] = r.airQualityLabel;
    doc["uptimeMs"] = millis();

    serializeJson(doc, outJson);
}

bool sendToBackend(const SensorReading& r) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected - skipping upload");
        return false;
    }

    String payload;
    buildJsonPayload(r, payload);

    String url = String(API_BASE_URL) + "/api/measurements";

    WiFiClientSecure client;
    client.setInsecure();

    HTTPClient http;
    http.setTimeout(20000);
    http.setReuse(false);

    Serial.println("Sending POST to:");
    Serial.println(url);

    if (!http.begin(client, url)) {
        Serial.println("Failed to initialize HTTPS connection");
        return false;
    }

    http.addHeader("Content-Type", "application/json");
    http.addHeader("Connection", "close");

    Serial.println("Sending payload:");
    Serial.println(payload);

    int responseCode = http.POST(payload);

    Serial.printf("POST response code: %d\n", responseCode);

    if (responseCode > 0) {
        String responseBody = http.getString();
        Serial.println("Response:");
        Serial.println(responseBody);
        http.end();
        return responseCode >= 200 && responseCode < 300;
    }

    Serial.printf("POST failed, error: %s\n", http.errorToString(responseCode).c_str());

    http.end();
    return false;
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("BME680");
    Serial.println("===========================");

    if (!initBME680()) {
        Serial.println("ERROR: Could not find BME680 sensor.");
        Serial.println("Check wiring and I2C address.");
        while (true) {
            delay(1000);
        }
    }

    Serial.println("Sensors initialized successfully!");
    Serial.println();

    connectWiFi();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi connection lost. Reconnecting...");
        connectWiFi();
    }

    SensorReading reading = readSensors();
    printReadings(reading);

    if (isValidReading(reading)) {
        sendToBackend(reading);
    } else {
        Serial.println("Invalid sensor reading - not sending to backend");
    }

    delay(10000);
}