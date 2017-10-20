# Operator Interface Control Board #

First off, I need a better name for this product...

The **FRC Operator Interface Control Board (OICB)** provides teams with an easy to use interface to connect remote sensors and actuators to their robot such as servos for gauges, LEDs, switches, buttons, and potentiometers. 

Built on top of an ATmega 2560 and flashed with the Arduino bootloader, it provides teams for even more customizability with an easy-to-use platform that many of them are already familiar with. 

The electrical connections are where this board is really unique compared to other options for FRC teams such as the Cypress PSoC board or TI LaunchPad. This board utilizes the two and three pin connections that are used for PWM cables and for the Robot Signal Light to individually connect peripherals to the OICD. This means that adding, removing, or replacing a switch is as easy as unplugging and/or plugging a new one back in. 

![](https://raw.githubusercontent.com/GarnetSquardon4901/Operator-Interface-Control-Board/master/Documentation/images/frc_control_board_top.png)

## Example Usage ##
Here is the control board from Garnet Squadron's 2016 robot, Sandstorm III. We have 5 preset buttons with a manual knob. Each arm position button also had an LED that shows what mode is currently selected as well as if the arm is in the position being set. An autonomous selector with 5 modes, two momentary toggle switches, and a Ye Olde Kaboom button for shooter the ball, which had a red ring that lit when the shooting-allowed parameters were met.

![](https://raw.githubusercontent.com/GarnetSquardon4901/Operator-Interface-Control-Board/master/Documentation/images/IMG_0693.JPG)

## Features ##
- USB Powered
- 16 Analog Inputs
- 16 Digital Inputs**
- 16 LED Outputs @ 20mA
- 11 PWM Outputs**
- Arduino Compatible
- CRC serialized data

** These I/O pins can be reconfigured by changing the firmware to do either Digital In, Digital Out, or PWM Out.

## How it works ##
The OICB is connected to your computer view a USB A to B cable. The OICB application is installed on your computer (see Releases). You set your team number within the application, and it will connect to your robot's Network Table server to fetch and push control data. 



