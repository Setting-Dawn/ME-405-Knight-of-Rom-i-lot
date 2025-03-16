# ME-405-Knight-of-Rom-i-lot
## Purpose
This repository was created to document Team Mecha35's methods of making a two-wheeled robot called Romi autonomously navigate an obstacle course in timed trials.

## Utilized Code:
This code utilizes the files task_share.py and cotask.py from the ME 405 Support Library, as well as as the structure of basic_task.py. This repository can be found here: https://github.com/spluttflob/ME405-Support

## The Goal
The following track was provided as the course Romi must drive. It includes:
  1. Numbered checkpoints, which must be reached in numerical order.
  2. Lines that can be detected via IR sensor.
  3. 2 Optional Objectives that can be pushed out of the circles to recieve a 5 second bonus for a total of 10 seconds.
  4. A metal cage section in which the Line ceases after Checkpoint 4 so Romi must be able to navigate via other methods.
  5. A wall at the end of the course that must be interacted with at least once and must be navigated around to reach the finish.
     
![image](https://github.com/user-attachments/assets/b27fa7a4-7f6d-46e2-b7e6-594073ab0598)

## The Solution
The team determined that because the optional objectives required leaving the line, and the caged section also required a method of navigation other than line following, it would make the most sense to find a method of travel entirely independant of the IR sensor.

Instead, it was decided to translate the course into a series of points that needed to be hit. These points would then be driven to in order.

To accomplish this, the magnetometer from a BNO055 IMU was used to read Euler angles to determine heading relative to an initial reference point, and the average change in encoder reading between the two motors was used to track distance travelled. 

### Assumptions
This method of travel relies heavily on two main assumptions:
  1. The wheels do not slip while driving.
  2. The magnetometer remains consistent.

While the wheels do not generally slip when a more moderate effort is requested from the motors, the higher speeds requested caused some slipping during the initial acceleration. This slipping was accounted for via 3 methods.
  1. The wheels were regularly cleaned of dust & larger debris by lighting wiping them with a damp paper towel.
  2. The batteries were regularly recharged so that decreasing voltage did not affect the requested effort.
  3. Any remaining slip was hand tuned into the distance Romi was instructed to travel.
  4. Slipping was not a concern during turning, as the distance travelled was not being recorded during turns and instead relied solely on data from the IMU to ensure the correct angle was reached.

The IMU recalibrates each time it is powered on and switched into a mode other than CONFIGURATION. Additionally, the magnetometer's detection of where North is was inconsistent in the lab room after each recalibration. However, on individual tests, the megnetometer remained constant. That meant that a reference direction could be recorded at the beginning of the run and the desired steering angles could be determined relative to that point. This still required some adjustments.
  1. According to the documentation, to get yaw angle values, the 0x18 register can be read, and the returned value divided by 900 or 16 to get radians or degrees respectively. However, using this calculation, the yaw angle reports readings from 0 to 6.4 radians.
  2. If the reference angle is above pi, the equation (current heading - reference angle) will produce a harsh jump as the actual heading rotates past it's maximum value and becomes 0. This can be adjusted for by adding 2 pi to the current heading if the current heading is less than (reference angle - pi). This adjustment was not initially included, which caused Romi to occasionally begin spinning uncontrollably when new angles brought Romi near the discontinuity.

![ME405 Term Project State Transition Diagrams](https://github.com/user-attachments/assets/763c06c5-af27-4378-a108-7e49cacac6d7)

!(https://youtube.com/shorts/Kf_3iBvN05o?feature=share)

