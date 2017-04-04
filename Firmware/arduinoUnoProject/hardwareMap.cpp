#include "hardwareMap.h"

// Settings for how fast and how precise the servo sweeps.
// The full sweep time should be very close to SWEEP_COUNT * SWEEP_DELAY
#define SWEEP_COUNT 200.0  // Number of iterations to step the servo
#define SWEEP_DELAY 10     // Delay between steps (ms)

// How far to sweep the servo from 0 to SWEEP_FULL_SCALE degrees
#define SWEEP_FULL_SCALE 180.0

// Pulse width adjustments for non-compliant servos (defaults: PWM_MIN = 544; PWM_MAX = 2400)
#define PWM_MIN 600
#define PWM_MAX 2400

// The analog pin map is based on the Arduino Mega 2560 pins.
// Analog Pin Map:               {ANA0, ANA1, ANA2, ANA3, ANA4, ANA5}
const uint8_t u8_Analog_Pins[] = {A0,   A1,   A2,   A3,   A4,   A5}; 

// PWM Pin Map:                  {PWM0}
const uint8_t u8_PWM_Pins[] =    {11}; 

// Switch Pin Map:               {SW0, SW1, SW2, SW3, SW4, SW5}
const uint8_t u8_SW_Pins[] =     {2,   3,   4,   5,   6,   7}; 

// LED Pin Map:                  {LED0, LED1, LED2, LED3}
const uint8_t u8_LED_Pins[] =    {8,    9,    10,   12};

// Status LED
enum {
  STATUS_LED = 13
};


// Global Variables
uint8_t u8_StatusLED_value; 
Servo servoOutputs[NUM_OF_PWM_OUTS];

// Sets the Status LED to on or off. 
void setStatusLED(uint8_t u8_value)
{
  u8_StatusLED_value = u8_value;
  digitalWrite(STATUS_LED, u8_StatusLED_value);   
}

// Toggles the Status LED (Blinks)
void toggleStatusLED(void)
{
   setStatusLED(!u8_StatusLED_value);
}

// Initializes hardware by setting up the hardware pins and doing a self-test
void initHardware(void)
{
  // Analog Configuration
  analogReference(DEFAULT);
  uint8_t u8_Analog_Index;
  for(u8_Analog_Index = 0; u8_Analog_Index < NUM_OF_ANA_INS; u8_Analog_Index++)
    pinMode(u8_Analog_Pins[u8_Analog_Index], INPUT);
    
  // Switch Configuration
  uint8_t u8_Switch_Index;
  for(u8_Switch_Index = 0; u8_Switch_Index < NUM_OF_SW_INS; u8_Switch_Index++)
    pinMode(u8_SW_Pins[u8_Switch_Index], INPUT_PULLUP);
    
  // PWM Configuration
  uint8_t u8_PWM_Index;
  for(u8_PWM_Index = 0; u8_PWM_Index < NUM_OF_PWM_OUTS; u8_PWM_Index++)
  {
    // Set the pinmode to output
    pinMode(u8_PWM_Pins[u8_PWM_Index], OUTPUT);
    // Attach the servo to the PWM generator
    servoOutputs[u8_PWM_Index].attach(u8_PWM_Pins[u8_PWM_Index], PWM_MIN, PWM_MAX);
  }
    
  // LED Configuration
  uint8_t u8_LED_Index;
  for(u8_LED_Index = 0; u8_LED_Index < NUM_OF_LED_OUTS; u8_LED_Index++)
    pinMode(u8_LED_Pins[u8_LED_Index], OUTPUT);
  blankLEDs();
  
  // Status LED Configuration
  pinMode(STATUS_LED,         OUTPUT); 
  
  // Initialize Values and perform self-test
  resetHardware(0); 
}

void blankLEDs(void) {
  setLEDs(0x0000);
}

// Sets all the LEDs in the LED values array.
void setLEDs(uint16_t u16_ledMask) {
  uint8_t u8_LED_Index;
  for(u8_LED_Index = 0; u8_LED_Index < NUM_OF_LED_OUTS; u8_LED_Index++) {
    digitalWrite(u8_LED_Pins[u8_LED_Index], (u16_ledMask & 0x8000) ? HIGH:LOW);
    u16_ledMask <<= 1;
  }
}

// Read the switch values into au8_SW_values[].
uint16_t getSwitchMask(void)
{
  uint8_t u8_Switch_Index = NUM_OF_SW_INS;
  uint16_t u16_SW_values = (digitalRead(u8_SW_Pins[u8_Switch_Index--])? 0x0000:0x0001);
  do {
    u16_SW_values <<= 1;
    u16_SW_values |= (digitalRead(u8_SW_Pins[u8_Switch_Index])? 0x0000:0x0001);
  } while(u8_Switch_Index-- != 0);
  return u16_SW_values;
}

uint8_t getAnalog(uint8_t u8_AnalogChannel) {
  if(u8_AnalogChannel < NUM_OF_ANA_INS)
    return analogRead(u8_Analog_Pins[u8_AnalogChannel]) >> 2;
}


// Sets the LED outputs off and returns the servos back to 0 degrees. 
void resetHardware(uint8_t u8_selfTest)
{
  // Set LEDs off
  setLEDs(0x0000);
  
  // Turn Status LED off
  setStatusLED(LOW);
  
  // Set Servos to 0 (account for any floating point error, as the sweep should return them back to 0). 
  for(uint8_t u8_PWM_Index = 0; u8_PWM_Index < NUM_OF_PWM_OUTS; u8_PWM_Index++)
      setPWM(u8_PWM_Index, 0); 
}

void setPWM(uint8_t u8_pwmChannel, uint8_t u8_pwmValue) {
  if(u8_pwmChannel < NUM_OF_PWM_OUTS)
    servoOutputs[u8_pwmChannel].write(u8_pwmValue);
}


