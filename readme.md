# Operator Interface Control Board #

First off, I need a better name for this product...

The **Operator Interface Control Board (OICB)** is a small printed circuit board with an Atmel ATMega 2560 microprocessor that provides easy I/O for the operator/driver to interface with their robot.

![](https://raw.githubusercontent.com/GarnetSquardon4901/Operator-Interface-Control-Board/master/frc_control_board_top.png)

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
The OICB is connected to your computer view a USB A to B cable (printer cable). You can write code in your LabVIEW Dashboard that interfaces between your robot and the OICB. You can use various methods to transmit data to and from your robot, but the easiest to use is Network Tables.



