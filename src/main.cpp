#include <Arduino.h>

#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define LED_COUNT 8

Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);

int onRPM = 20;
int normMaxRPM = 800;
int overRevRPM = 1000;

bool doneStartup = false;

const uint32_t tachColor[LED_COUNT] = {
    Adafruit_NeoPixel::Color(0, 255, 0), // green
    Adafruit_NeoPixel::Color(0, 255, 0),
    Adafruit_NeoPixel::Color(0, 255, 0),
    Adafruit_NeoPixel::Color(0, 255, 0),
    Adafruit_NeoPixel::Color(255, 255, 0),
    Adafruit_NeoPixel::Color(255, 255, 0),
    Adafruit_NeoPixel::Color(255, 0, 0), // orange
    Adafruit_NeoPixel::Color(255, 0, 0),
};

const uint32_t shiftColor = Adafruit_NeoPixel::Color(0, 0, 255);            // blue
const uint32_t overRevColor = Adafruit_NeoPixel::Color(255, 255, 255, 255); // red

// Set the RPMuency when each LED should turn on
// First LED turns on at minRPMuency
int lightShiftRPM[LED_COUNT] = {
    50,
    100,
    200,
    300,
    400,
    500,
    600,
    700,
};

void setup()
{
  Serial.begin(9600);

  pixels.begin();
  pixels.show();
  pixels.setBrightness(255);

  pinMode(A0, INPUT);
}

void loop()
{
  int RPM = analogRead(A0);
  Serial.println(RPM);

  if (doneStartup == false)
  {
    if (RPM > onRPM)
    {
      // run start sequence
      // LEDs will light up, flash and light out upon starting the engine.
      for (int i = 0; i < LED_COUNT; ++i)
      {
        pixels.setPixelColor(i, tachColor[i]);
        pixels.show();
        delay(80);
      }
      for (int i = 0; i < LED_COUNT; ++i)
      {
        pixels.setPixelColor(i, tachColor[i]);
        pixels.show();
      }
      for (int i = LED_COUNT - 1; i >= 0; --i)
      {
        pixels.setPixelColor(i, pixels.Color(0, 0, 0));
        pixels.show();
        delay(80);
      }
      doneStartup = true;
      pixels.fill(pixels.Color(0, 0, 0));
      pixels.show();
    }
    if (RPM < onRPM)
      doneStartup = false;
  }

  if (RPM < normMaxRPM) // normal operating range
  {
    for (int i = 0; i < LED_COUNT; ++i)
    {
      if (RPM > lightShiftRPM[i])
        pixels.setPixelColor(i, tachColor[i]);
      else
        pixels.setPixelColor(i, pixels.Color(0, 0, 0));
    }
    pixels.show();
  }
  else if (RPM >= normMaxRPM && RPM < overRevRPM) // shift flash
  {
    pixels.fill(shiftColor);
    pixels.show();
    delay(30);
    pixels.fill(pixels.Color(0, 0, 0));
    pixels.show();
    delay(30);
  }
  else if (RPM >= overRevRPM) // over rev flash
  {
    pixels.fill(overRevColor);
    pixels.show();
    delay(30);
    pixels.fill(pixels.Color(0, 0, 0));
    pixels.show();
    delay(30);
  }
}
