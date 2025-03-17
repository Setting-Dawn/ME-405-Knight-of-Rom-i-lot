# ME-405-Knight-of-Rom-i-lot
![RomiCoverImage](https://github.com/user-attachments/assets/67cd7905-8078-43fe-9269-39565ed9a46b)

## Purpose
This repository was created to document Team Mecha35's methods of making a two-wheeled robot called Romi autonomously navigate an obstacle course in timed trials.

## Utilized Code:
This code utilizes the files task_share.py and cotask.py from the ME 405 Support Library, as well as as the structure of basic_task.py. This repository can be found here: https://github.com/spluttflob/ME405-Support
These files were used in accordance with the license included in the repository, which was also included with this repository for clarity

# Table of Contents
 - ![Purpose](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Purpose)
 - ![Utilized Code](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Utilized_Code)
 - ![Table of Contents](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Purpose)
 - ![Goal](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#The_Goal)
 - ![Solution](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#The_Solution)
   - ![Assumptions](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Assumptions)
     - ![Validity](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#The_(in)Validity_of_Assumptions)
   - ![Video Demo](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Trial_Video)
   - ![Task and State Diagram](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Task_Diagram)
   - ![Mechanical Design](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Mechanical_Design)
   - ![Electrical Design](https://github.com/Setting-Dawn/ME-405-Knight-of-Rom-i-lot/README.me#Electrical_Design)

## The Goal
The following track was provided as the course Romi must drive. It includes:
  1. Numbered checkpoints, which must be reached in numerical order.
  2. Lines that can be detected via IR sensor.
  3. Two Optional Objectives that can be pushed out of the circles to receive a 5 second bonus for a total of 10 seconds.
  4. A metal cage section in which the Line ceases after Checkpoint 4 so Romi must be able to navigate via other methods.
  5. A wall at the end of the course that must be interacted with at least once and must be navigated around to reach the finish.
     
![image](https://github.com/user-attachments/assets/b27fa7a4-7f6d-46e2-b7e6-594073ab0598)

## The Solution
The team determined that because the optional objectives required leaving the line, and the caged section also required a method of navigation other than line following, it would make the most sense to find a method of travel entirely independent of the IR sensor.

Instead, it was decided to translate the course into a series of points that need to be hit. These points would then be driven to in order.

To accomplish this, the magnetometer from a BNO055 IMU was used to read Euler angles to determine heading relative to an initial reference point, and the average change in encoder reading between the two motors was used to track distance travelled. 

### Assumptions
This method of travel relies heavily on two main assumptions:
  1. The wheels do not slip while driving.
  2. The magnetometer remains consistent.

### The (in)Validity of Assumptions
While the wheels do not generally slip when a more moderate effort is requested from the motors, the higher speeds requested caused some slipping during the initial acceleration. This slipping was accounted for via 3 methods.
  1. The wheels were regularly cleaned of dust & larger debris by lightly wiping them with a damp paper towel.
  2. The batteries were regularly recharged so that decreasing voltage did not affect the requested effort.
  3. Any remaining slip was experimentally calibrated into the distance Romi was instructed to travel.
  4. Slipping was not a concern during turning, as the distance travelled was not being recorded during turns and instead relied solely on data from the IMU to ensure the correct angle was reached.

The IMU recalibrates each time it is powered on and switched into a mode other than CONFIGURATION. Additionally, the magnetometer's detection of where North is was inconsistent in the lab room after each recalibration. However, on individual tests, the magnetometer remained constant. That meant that a reference direction could be recorded at the beginning of the run and the desired steering angles could be determined relative to that point. This still required some adjustments.
  1. According to the documentation, to get yaw angle values, the 0x18 register can be read, and the returned value divided by 900 or 16 to get radians or degrees respectively. However, using this calculation, the yaw angle reports readings from 0 to 6.4 radians.
  2. If the reference angle is above pi, the equation (current heading - reference angle) will produce a harsh jump as the actual heading rotates past it's maximum value and becomes 0. This can be adjusted for by adding 2 pi to the current heading if the current heading is less than (reference angle - pi). This adjustment was not initially included, which caused Romi to occasionally begin spinning uncontrollably when new angles brought Romi near the discontinuity.

### ![Trial Video](https://youtube.com/shorts/Kf_3iBvN05o?feature=share)

[<img src="https://github.com/user-attachments/assets/c43b9d0d-15a9-4768-8c70-00cf0dd73db2" width="270" height="480">](https://youtube.com/shorts/Kf_3iBvN05o?feature=share)

## Task Diagram
![Task Diagram](https://github.com/user-attachments/assets/f7590166-38d4-48ed-b110-abad4e325ce3)

## State Transition Diagrams
![ME405 Term Project State Transition Diagrams](https://github.com/user-attachments/assets/efa2f1de-ad83-4d2a-9ef7-544ecfd490e7)

### Task Shares
| Share | data type | Purpose |
|--|--|--|
| m_effL | signed byte | Instruct the Left Motor what direction and PWM to use |
| m_effR | signed byte | Instruct the Right Motor what direction and PWM to use |
| RunL | unsigned byte | Whether the Left motor should be enabled |
| RunR | unsigned byte | Whether the Right motor should be enabled |
| encoderReadL | signed float | The number of radians the Left Encoder has rotated since zeroing |
| encoderReadR | signed float | The number of radians the Right Encoder has rotated since zeroing |
||||
| IRRead | unsigned byte | Whether the IR sensor array should be enabled |
| IRcentroid | signed float | Reports the current centroid calculation from the line reader |
| IRgoal | unsigned byte | Communicates a requested offset from the line |
| IR_shares | unsigned int* | *Actually contains 13 shares each reporting the individual sensor readings |
| IRerror | signed float | Reports the PID scaled current difference between desired and actual centroid for motor effort|
||||
| IMUerror | signed float | The PID scaled difference between desired and actual heading for motor effort|
| enableCompass | unsigned byte | Request steering via the IMU heading |
| updateNorth | unsigned byte | Whether the reference angle should be recalibrated |
| IMUheading | signed float | Approximate radian reading of heading |
| idealHeading | signed float | The heading Romi should be facing, measured relative to its reference angle |
| IMUBraine | signed float | The difference between the desired and actual heading |
||||
| BumpEnable | unsigned byte | Contains a flag enabling or disabling the bump sensors |
| BumperTrigger | unsigned byte | Contains a flag that is raised by the Bump task and acknoledged by the Brain task |

The state transition diagrams for each task are as seen above. 
The Communicate Task simply waits for user input after being initiated and sets relevants flags depending on user input. 
After initiating, the Motor Tasks stay in state 1, taking the errors from the IMU and IR sensors and adjust relative to the set effort, running the motors at the adjusted effort while reading the encoders continuously. 
The IR Sensor Task has a read state and an off state to conserve power. In the read state, the IR Sensor Task calculates the centroid from the 13 readings from each IR sensor and then can switch to off, calibrate high, calibrate low, or continue reading depending on user input from the Communicate Task. In the off state, the IR Sensor Task waits to be enabled or calibrated. 
The IMU Task configures in state 1 after initializing and waits in state 2 until the IMU is configured and calibrated in the correct mode using a setup flag internal to the task. State 3 of the IMU Task if enabled through the Communication Task will record heading data and approximately convert it to radians. If signalled to via the Communication Task, IMU Task state 3 can save the current heading as a reference angle to keep a maintain a desired heading relative the reference angle. The error from the desired heading from the current is calculated relative to the reference angle. The IMU reports only positive readings, so the error is adjusted and normalized to be a number from 1 to -1 for simpler PID adjustments. If the error is within a certain tolerance, state 3 will reset the the PID controller for the IMU, which essentially makes it only proportionally controlled. 
The Bumps Task initializes to start enabled and then once in state 1, continuously updates if any of the bump sensors have been triggered and can switch to an off state if disabled. Romi is equipped with 6 bump switches which could have been used to check where the robot was impacted, but sensing the wall only requires 1 bump sensor, so all 6 bump sensors are used in tandem to check is any side of Romi has collided. The output from the bump sensors is used to update a flag when desired to inform the Brain Task whether an obstruction was hit. 
The Brain Task is designed to keep track of which section of the track the robot is currently at and the desired distance to travel in a list d indexed by section number. Upon initialization, the Brain Task sets effort to zero, section to 1, and stores the current encoder positions. The Brain Task will wait in state 1 until the motors are prompted to move and transition to the next state and section if the a certain encoder distance is reached. The Communication Task is used to command Romi to begin running the course by pressing the space bar after selecting which method to start off with. For the first section, Romi could either be instructed to use the IR sensor to gain a sense of where straight is by inputting 1 or use the IMU to set off straight in the current alignment by inputting c. The IR sensor proved less reliable at setting a straight heading than simply aligning Romi correctly and using the IMU. After completing the first section, the Brain Tasks alternates between states 2 and 3 for turning and driving straight respectively until section 8. The turn state informs the IMU Task of the desired heading by section and waits until the IMU error is sufficiently negligible to continue in addition to a loop counter implemented to ensure Romi reaches the right heading and stores the current encoder positions. If in section 8, the turn state transitions to state 4 instead of state 3 to prepare for interaction with the wall. In Brain Task's state 3 for driving straight, the change in encoder position from the last recorded positions are averaged from the left and right encoders to determine distance travelled, this way only the distance travelled in a straight path is accounted for. If it's not the last section, state 3 will transition to the turn state 2 if the correct encoder distance is reached for the section. State 4 runs at a special section of the course where a wall is interacted with. The speed is adjusted to as to not displace the wall enough to impact performing the rest of the course and distance is still calculated to prevent early triggering of the bump sensors. Once the a certain distance is reached and the bump sensors are triggered, the bump sensor flag is reset and the Brain Task transitions to state 5. In state 5, the Brain Task sets negative effort to move backwards a certain distance relative to negative encoder position changes and sets up to transition to the turn state. The rest of the turns and straights for each section are performed until the stopping after the last section.

![RomiControlBlockDiagram](https://github.com/user-attachments/assets/772d8ffe-fc11-4b6a-9cea-778129ab3cc4)

The block diagram above represents the control scheme implemented in Romi. The control system takes inputs of set motor effort, IR setpoint, and IMU setpoint which can change at various parts of the code. The main outputs of control system are the encoder positions, average encoder position, IMU angle reading, and IMU error. The control system uses measurements from the IMU, encoders,and IR sensors. The bump sensors were implemented outside of the main control scheme as a boolean for determining when to change states in the Brain task rather than inform the motors how to behave. The control system uses the relations between the inputs and sensor readings to calculate an adjusted effort to send to each motor to produced the desired behavior. Simple PID control is implemented only on the IMU error and IR error to tune and adjust the desired response from the motor to the IMU and IR readings.

## Mechanical Design
Components:
- NUCLEO L476RG
- Romi Chassis (PN 3500, 3501, 3502, 3504, 3506, or 3509)
- Motor Driver and Power Distribution Board for Romi Chassis (PN 3543)
- Romi Encoder Pair Kit (PN 3542)
- BNO055 IMU
- Modified Shoe of Brian
- Acrylic Romi-to-Shoe Adapter
- HC-05 Bluetooth Module
- QTR-MD-13A IR Sensor (PN 4253)
- Left (PN 3673) and Right (PN 3674) Bumper Switch Assemblies for Romi
- 3D Printed IR and Bump Sensor Mount

In order to suspend the NUCLEO and Shoe of Brian above the Romi Chassis an acrylic adapter was connnected with standoffs. A 3D printed mount was also designed to connect both the IR sensor and the bump sensors. The IR sensor was too wide to mount directly on the chassis and extended past where the bump sensors mounted directly on the chassis, so a custom mount was designed to connect both to the chassis. A CAD model of the mount is shown below as well as how it connects to the bump and IR sensors.

![ROMI IR and Bump Sensor Mount](https://github.com/user-attachments/assets/86ec684a-8dd7-47da-a822-b66707920ebe)
![ROMI Mount and Sensor Assembly](https://github.com/user-attachments/assets/56e1de6e-5c31-42a9-8684-dd2f80804367)

All the components mounted onto the chassis is shown below.
![IMG_5030](https://github.com/user-attachments/assets/107a2a1d-a950-4250-a2ed-8bed43ad1a16)

## Electrical Setup
### Motor and Encoder Wiring
| Function | Pin | Notes |
|--------|-----|---------|
| Left Encoder Ch.A | PB_4 | Uses Timer 3 |
| Left Encoder Ch.B | PB_5 | Uses Timer 3 |
| Left Motor Enable | PC_9 |  |
| Left Motor Direction | PC_8 |  |
| Left Motor PWM | PB_10 | Uses Timer 2 |
| | | |
| Right Encoder Ch.A | PC_6 | Uses Timer 8 |
| Right Encoder Ch.B | PC_7 | Uses Timer 8 |
| Right Motor Enable | PA_10 |  |
| Right Motor Direction | PB_13 |  |
| Right Motor PWM | PB_3 | Uses Timer 2 |

### Bump Sensors
| Sensor | Pin |
|--------|-----|
| 0      | PA_15 |
| 1      | PH_0 |
| 2      | PH_1 |
| 3      | PC_12 |
| 4      | PC_10 |
| 5      | PC_11 |

### IR Sensor
| Sensor | Pin |
|--------|-----|
| 1      | PC_4 |
| 2      | PB_1 |
| 3      | PC_0 |
| 4      | PA_7 |
| 5      | PC_1 |
| 6      | PA_6 |
| 7      | PB_0 |
| 8      | PC_5 |
| 9      | PA_4 |
| 10      | PC_3 |
| 11      | PA_1 |
| 12      | PC_2 |
| 13      | PA_0 |

### IMU Pins
| Purpose | Pin | Notes |
|--------|-----|--------|
| Reset Pin | PB_2 | Is a notResetPin, so resets if pulled low|
| IMU SDA | PB_9 | Alt function AF4_I2C |
| IMU SCL | PB_8 | Alt function AF4_I2C |

## Analysis
We performed analysis on the motors we received early on to experimentally determine theoretical gain, startup effort, and time constants for each motor shown below. The startup effort was used as a starting point for offsetting the bias between the motors, so that a single input effort resulted in simultaneous startup from both motors. The values needed to be adjusted greatly to result in straight motion upon startup as expected from using theoretically determined values despite being based on experimental data. The time constants were deemed close enough to be negligible and the motor gains were outpaced by the proportional control constants and similar enough to have negligible effect. 
| Parameter | Left Motor | Right Motor |
| -------- | ------- |-------|
| Motor Gain [rad/V*s]  | 4.045  |3.94|
| Motor Startup Effort | 3.19%| 3.31% |
|Time Constant [s]| 0.0874 |0.0895|

The following plots were created from data collected from the left motor with similar analyis done on the right motor to get the values in the table above.

![Plot 1](https://github.com/user-attachments/assets/0e66600a-3898-4324-8765-2998e958823b)
![Plot 2](https://github.com/user-attachments/assets/5b001a12-73d9-47cf-97e4-2e38e6107afa)
![Plot 3](https://github.com/user-attachments/assets/fe0a6cc1-6da0-4c62-b1df-7dc63f8de9f5)
![Plot 4](https://github.com/user-attachments/assets/5e50ca57-d403-447a-8682-6f927afd30b9)
