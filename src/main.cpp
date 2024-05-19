#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN 6
#define LED_COUNT 8

Adafruit_NeoPixel pixels(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);

const uint32_t black = Adafruit_NeoPixel::Color(0, 0, 0);
const uint32_t red = Adafruit_NeoPixel::Color(255, 0, 0);
const uint32_t green = Adafruit_NeoPixel::Color(0, 255, 0);
const uint32_t blue = Adafruit_NeoPixel::Color(0, 0, 255);
const uint32_t orange = Adafruit_NeoPixel::Color(255, 150, 0);

const uint32_t overRevColor = red;
const uint32_t shiftColor = blue;

uint16_t RPM = 0;
uint16_t onRPM = 20;
uint16_t shiftRPM = 7000;
uint16_t overRevRPM = 7500;

uint8_t shiftColorTime = 30;
uint8_t overRevColorTime = 30;

bool doneStartup = false;

const uint32_t tachColor[LED_COUNT] = {
    green,
    green,
    green,
    orange,
    orange,
    orange,
    red,
    red,
};

uint16_t lightShiftRPM[LED_COUNT] = {
    1000,
    1500,
    2000,
    2500,
    3000,
    4000,
    5000,
    6000,
};

void startUpAnimation()
{
  for (int i = 0; i < LED_COUNT; ++i)
  {
    pixels.setPixelColor(i, tachColor[i]);
    pixels.show();
    delay(80);
  }
  for (int i = LED_COUNT - 1; i >= 0; --i)
  {
    pixels.setPixelColor(i, black);
    pixels.show();
    delay(80);
  }
  pixels.fill(black);
  pixels.show();
}

void normalOperation()
{
  for (int i = 0; i < LED_COUNT; ++i)
  {
    if (RPM > lightShiftRPM[i])
      pixels.setPixelColor(i, tachColor[i]);
    else
      pixels.setPixelColor(i, black);
  }
  pixels.show();
}

void shiftOperation()
{
  uint32_t color = millis() % (2 * shiftColorTime) <= shiftColorTime ? shiftColor : black;
  pixels.fill(color);
  pixels.show();
}

void overRevOperation()
{
  uint32_t color = millis() % (2 * overRevColorTime) <= overRevColorTime ? overRevColor : black;
  pixels.fill(color);
  pixels.show();
}

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(5);

  pixels.begin();
  pixels.show();
  pixels.setBrightness(100);

  pinMode(A0, INPUT);
}

void loop()
{
  // RPM = analogRead(A0);

  if (Serial.available() > 0)
  {
    String data = Serial.readString();
    Serial.flush();
    RPM = data.toInt();
    Serial.println(RPM);
  }

  if (!doneStartup && RPM > onRPM)
  {
    doneStartup = true;
    startUpAnimation();
  }
  else
  {
    if (RPM > overRevRPM)
      overRevOperation();
    else if (RPM > shiftRPM)
      shiftOperation();
    else if (RPM > onRPM)
      normalOperation();
    else
    {
      pixels.fill(black);
      pixels.show();

      doneStartup = false;
    }
  }
}