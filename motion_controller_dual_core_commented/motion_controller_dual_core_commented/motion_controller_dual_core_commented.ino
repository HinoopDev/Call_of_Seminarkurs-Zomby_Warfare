/*
© Johannes Heubach 2025
*/

//Libaries:
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <BleKeyboard.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_NeoPixel.h>

//Pinouts:
#define SDA 16
#define SCL 17
#define SDA2 18
#define SCL2 19
#define btn 5
#define LED_PIN 21

//WS2812B specific:
#define LED_COUNT 4

//SSD1306 specific:
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

//storage for UI output:
bool fire = 0;
bool ble = 0;
bool movea = 0;
bool moved = 0;
bool movew = 0;
bool moves = 0;
bool firing = 0;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire1, OLED_RESET);  //Setup SSD1306

Adafruit_MPU6050 mpu; //Setup Gyroscope

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);  //Setup WS2812B

BleKeyboard bleKeyboard("Controller", "@TPA_dev2", 69); //Setup BLE name

//Create tasks:
TaskHandle_t gyro;
TaskHandle_t periphs;

//Create colors for WS2812B:
uint32_t red = strip.Color(255, 0, 0);
uint32_t green = strip.Color(0, 255, 0);
uint32_t blue = strip.Color(0, 0, 255);
uint32_t türkis = strip.Color(0, 255, 255);
uint32_t orange = strip.Color(255, 127, 0);

void setup() {
  //WS2812B initiate:
  strip.begin();
  strip.show();

  //Serial monitor initiate:
  Serial.begin(115200);

  //printing which core is getting used for "void setup":
  Serial.print("setup running on core ");
  Serial.println(xPortGetCoreID());
  //setting pinModes:

  pinMode(btn, INPUT_PULLDOWN);
  //initiating BLE-Keyboard:

  Serial.println("BLE-Keyboard initalizing");
  bleKeyboard.begin();
  bleKeyboard.setDelay(20);
  //initiating 2 I2C buses:

  Serial.println("I2C initalizing");
  Wire.begin(SDA, SCL);
  Wire1.begin(SDA2, SCL2, 100000);

  //checking for gyroscope:
  if (!mpu.begin()) {
    Serial.println("MPU6050 connection failed");
    strip.fill(red, 0, 4);
    strip.show();
    while (1)
      ;
  } else {
    Serial.println("MPU6050 connected");
  }

  //checking for SSD1306:
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    strip.fill(red, 0, 4);
    strip.show();
    for (;;)
      ;
  } else {
    Serial.println("Display conencted");
  }

  //initiating tasks on seperate cores:
  xTaskCreatePinnedToCore(gyrocode, "gyro", 10000, NULL, 1, &gyro, 0);
  xTaskCreatePinnedToCore(peripherals, "periphs", 50000, NULL, 1, &periphs, 1);

  //UI output on WS2812B:
  strip.fill(green, 0, 4);
  strip.show();
  delay(300);
  strip.clear();
  strip.show();
  delay(300);
  strip.fill(green, 0, 4);
  strip.show();
  delay(300);
  strip.clear();
  strip.show();

  //rotating display:
  display.setRotation(2);
}

//Task reading gyroscope:
void gyrocode(void* pvParameters) {
  //infinity Loop:
  for (;;) {

    //for debugging purpose printing Core task is running on:
    Serial.print("gyro running on core ");
    Serial.println(xPortGetCoreID());

    //for powerefficency only check gyroscope when BLE conencted
    //also for obvious reasons sending BLE commands only when BLE conencted
    if (bleKeyboard.isConnected()) {

      //storing ble status for UI output:
      ble = 1;

      //creating floats for gyroscope data and getting gyroscope data:
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);

      //temporarely storing gyroscope data as floats:
      float a_x = a.acceleration.x;
      float a_y = a.acceleration.y;
      float a_z = a.acceleration.z;

      float g_x = g.gyro.x;
      float g_y = g.gyro.y;
      float g_z = g.gyro.z;

      float t = temp.temperature;

      //getting button status and temporarely storing it:
      fire = digitalRead(btn);

      //printing values on serial monitor for debugging:
      Serial.print(a_x);
      Serial.print(" , ");
      Serial.print(a_y);
      Serial.print(" , ");
      Serial.print(a_z);
      Serial.print(" , ");
      Serial.print(g_x);
      Serial.print(" , ");
      Serial.print(g_y);
      Serial.print(" , ");
      Serial.print(g_z);
      Serial.print(" , ");
      Serial.println(fire);

      //sending Keystrokes over BLE if gyroscope is tilted a ceratin way:
      if (a_x > 3) {
        bleKeyboard.press('s');
        movea = 1;
      } else {
        movea = 0;
      }
      if (a_x < -1) {
        bleKeyboard.press('w');
        moved = 1;
      } else {
        moved = 0;
      }
      if (a_y > 2) {
        bleKeyboard.press('a');
        moves = 1;
      } else {
        moves = 0;
      }
      if (a_y < -2) {
        bleKeyboard.press('d');
        movew = 1;
      } else {
        movew = 0;
      }
      if (fire == 1) {
        bleKeyboard.press('f');
        firing = 1;
      } else {
        firing = 0;
      }
      delay(100);
      bleKeyboard.releaseAll();
    } 
    
    //UI output if BLE disconnected:
    else {
      Serial.println("Connecting...");
      ble = 0;
      delay(100);
    }
  }
}

//Task handling UI:
void peripherals(void* pvParameters) {

  //delay to stop colliding with UI output from void setup:
  delay(1300);

  //infinity Loop:
  for (;;) {

    //for debugging purpose printing Core task is running on:
    Serial.print("peripherals running on core ");
    Serial.println(xPortGetCoreID());

    //resetting data currently on the UI output from void setup:
    strip.clear();
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.setTextColor(SSD1306_WHITE);

    //printing on UI output if BLE conencted:
    if (ble == 1) {
      display.print("BLE connected");

      //printing on UI output if button is pressed:
      if (firing == 1) {
        display.setCursor(0, 18);
        display.print("Firing");
        strip.fill(orange, 0, 4);
      } else {
        display.setCursor(0, 18);
        display.print("Idle");
      }

      //printing on UI output if gyroscope is tilted enough for Keystrokes to be sent and in which way the gyroscope is tilted
      if (movea == 1 || moved == 1 || moves == 1 || movew == 1) {
        display.setCursor(0, 9);
        display.print("Moving");
        if (movea == 1) {
          strip.setPixelColor(0, türkis);
        }
        if (moves == 1) {
          strip.setPixelColor(1, türkis);
        }
        if (moved == 1) {
          strip.setPixelColor(2, türkis);
        }
        if (movew == 1) {
          strip.setPixelColor(3, türkis);
        }
      } else {
        display.setCursor(0, 9);
        display.print("Idle");
      }
      display.display();
      strip.show();
    } 
    
    //printing on UI output if BLE not connected:
    else {
      display.print("BLE connecting");
      display.display();
      strip.fill(blue, 0, 4);
      strip.show();
      delay(300);
      strip.clear();
      strip.show();
      delay(300);
    }
  }
}

void loop() {
}
