#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

#define button 14
#define led_red 25
#define led_blue 26
#define led_green 27
#define cooldown 10000

long last_press = 0;

void status(String status){
  if(status == "error") {
    digitalWrite(led_red, HIGH);
  }
  if(status== "working"){
    digitalWrite(led_green, HIGH);
  }
  if(status=="waiting"){
    digitalWrite(led_blue, HIGH);
  }
}

void getMqtt(){
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String url = "https://io.adafruit.com/api/v2/";
    url += AIO_USERNAME;
    url += "/feeds/";
    url += FEED_KEY;

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
      const char* last_update = doc["updated_at"];
      processMqtt(value, last_update);
      
      // uncomment for debugging
      //Serial.println("Parsed JSON structure:");
      //serializeJsonPretty(doc, Serial);
      
      if (value) {
        Serial.println("last value: " + String(value));
      } else {
        Serial.println("Value not found in JSON response");
      }
      
      if (last_update) {
        Serial.println("last update: " + String(last_update));
      } else {
        Serial.println("Created At not found in JSON response");
      }

    } else {
      Serial.println("Error on HTTP request");
    }

    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  }
}

void processMqtt(const char* last_value, const char* last_update){
  if(last_value == "connection requested"){//and last update < currenttime - 5min
    //sendMqtt("200")
  }
  if(last_value.indexOf("game:")!=-1){
    last_value.remove(0, 5);
    int time = int(last_value)*1000;
    print(String(time))
  }
}

void setup() {
  pinMode(led_blue, OUTPUT);
  pinMode(led_green, OUTPUT);
  pinMode(led_red, OUTPUT);
  pinMode(button, INPUT_PULLUP);
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
  if(!digitalRead(button)&&millis()-last_press>cooldown){
    last_press = millis();
    status("waiting");
    getMqtt();
  }
  delay(2000);
}