#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

void setup() {
  Serial.begin(115200);
  delay(10);

  // Connect to WiFi
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String url = "https://io.adafruit.com/api/v2/";
    url += AIO_USERNAME;
    url += "/feeds/";
    url += FEED_KEY;
    //url += "/data/last";

    http.begin(url);
    http.addHeader("X-AIO-Key", AIO_KEY);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response payload: " + payload);

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
        return;
      }

      // Extract values
      const char* value = doc["last_value"];
      const char* created_at = doc["updated_at"];
      
      // uncomment for debugging
      //Serial.println("Parsed JSON structure:");
      //serializeJsonPretty(doc, Serial);
      
      if (value) {
        Serial.println("last value: " + String(value));
      } else {
        Serial.println("Value not found in JSON response");
      }
      
      if (created_at) {
        Serial.println("last update: " + String(created_at));
      } else {
        Serial.println("Created At not found in JSON response");
      }

    } else {
      Serial.println("Error on HTTP request");
    }

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(10000);
}
