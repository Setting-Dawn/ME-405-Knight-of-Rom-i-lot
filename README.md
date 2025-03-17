# ME-405-Knight-of-Rom-i-lot
## Purpose
This repository was created to document Team Mecha35's methods of making a two-wheeled robot called Romi autonomously navigate an obstacle course in timed trials.

## Utilized Code:
This code utilizes the files task_share.py and cotask.py from the ME 405 Support Library, as well as as the structure of basic_task.py. This repository can be found here: https://github.com/spluttflob/ME405-Support

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

While the wheels do not generally slip when a more moderate effort is requested from the motors, the higher speeds requested caused some slipping during the initial acceleration. This slipping was accounted for via 3 methods.
  1. The wheels were regularly cleaned of dust & larger debris by lightly wiping them with a damp paper towel.
  2. The batteries were regularly recharged so that decreasing voltage did not affect the requested effort.
  3. Any remaining slip was hand-tuned into the distance Romi was instructed to travel.
  4. Slipping was not a concern during turning, as the distance travelled was not being recorded during turns and instead relied solely on data from the IMU to ensure the correct angle was reached.

The IMU recalibrates each time it is powered on and switched into a mode other than CONFIGURATION. Additionally, the magnetometer's detection of where North is was inconsistent in the lab room after each recalibration. However, on individual tests, the megnetometer remained constant. That meant that a reference direction could be recorded at the beginning of the run and the desired steering angles could be determined relative to that point. This still required some adjustments.
  1. According to the documentation, to get yaw angle values, the 0x18 register can be read, and the returned value divided by 900 or 16 to get radians or degrees respectively. However, using this calculation, the yaw angle reports readings from 0 to 6.4 radians.
  2. If the reference angle is above pi, the equation (current heading - reference angle) will produce a harsh jump as the actual heading rotates past it's maximum value and becomes 0. This can be adjusted for by adding 2 pi to the current heading if the current heading is less than (reference angle - pi). This adjustment was not initially included, which caused Romi to occasionally begin spinning uncontrollably when new angles brought Romi near the discontinuity.

![ME405 Term Project State Transition Diagrams](https://github.com/user-attachments/assets/763c06c5-af27-4378-a108-7e49cacac6d7)

### ![Trial Video](https://youtube.com/shorts/Kf_3iBvN05o?feature=share)

[<img src="https://github.com/user-attachments/assets/c43b9d0d-15a9-4768-8c70-00cf0dd73db2" width="270" height="480">](https://youtube.com/shorts/Kf_3iBvN05o?feature=share)
![Untitled Diagram drawio](https://github.com/user-attachments/assets/f7590166-38d4-48ed-b110-abad4e325ce3)

### Task Shares
| Share | data type | Purpose |
|--|--|--|
| m_effL | signed byte | Instruct the Left Motor what direction and PWM to use |
| m_effR | signed byte | Instruct the Right Motor what direction and PWM to use |
| RunL | unsigned byte | Whether the Left motor should be enabled |
| RunR | unsigned byte | Whether the Right motor should be enabled |
| RunR | unsigned byte | Whether the Right motor should be enabled |
| encoderReadL | signed float | The number of radians the Left Encoder has rotated since zeroing |
| encoderReadR | signed float | The number of radians the Right Encoder has rotated since zeroing |
||||
| IRRead | unsigned byte | Whether the IR sensor array should be enabled |
| IRcentroid | signed float | Reports the current centroid calculation from the line reader |
| IRgoal | unsigned byte | Communicates a requested offset from the line |
| IR_shares | unsigned int* | *Actually contains 13 shares each reporting the individual sensor readings |
| IRerror | signed float | Reports the current difference between desired and actual centroid |
||||
| IMUerror | signed float | Reports the current difference between desired and actual centroid |
| enableCompass | unsigned byte | Request steering via the IMU heading |
| undateNorth | unsigned byte | Whether the reference angle should be recalibrated |
| idealHeading | signed float | The heading Romi should be facing, measured relative to its reference angle |
| idealHeading | signed float | The heading Romi should be facing, measured relative to its reference angle |
| IMUBraine | signed float | The difference between the desired and actual heading |
||||
| BumpEnable | unsigned byte | Contains a flag enabling or disabling the bump sensors |
| BumperTrigger | unsigned byte | Contains a flag that is raised by the Bump task and acknoledged by the Brain task |




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
