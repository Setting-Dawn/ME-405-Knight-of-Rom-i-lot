import gc
import pyb
import random
from pyb import Pin, Timer, UART
import cotask, task_share
import encoderObj, motorObj,IRsensorObj, IRcontrollerObj, PIDobj, IMUObj, Bumper
import array, time, math

def communicate(shares):
    """
    Task that handles user input and instructs Romi's behavior accordingly.
    """
    # Get references to the shares and queue which have been passed to this task
    (speedL,speedR,
     IRRead,IR_shares,IRcentroid,
     RunL,RunR,enableCompass,updateNorth,encoderReadL,encoderReadR) = shares
        
    try:
        ser = UART(1,115200)
        pyb.repl_uart(ser)
        print("Bluetooth enabled")
    except:
        print("Bluetooth not enabled")

    SetValue = 0 # Driving Speed set by user input

    # Set up Finite State Machine
    state = 0
    s0_Init = 0
    s1_awaitUser = 1

    while True:
        # Nothing needs to init other than
        if state == s0_Init:
            state = s1_awaitUser

        elif state == s1_awaitUser:
            if ser.any():
                Lvel = speedL.get()
                Rvel = speedR.get()
                char = ser.read(1).decode()

                # Allow user input for forward speed
                if char == "w":
                    SetValue = min(100,SetValue+5)
                    print(f"Current Target : {SetValue}")
                elif char == "s":
                    SetValue = max(-100,SetValue-5)
                    print(f"Current Target : {SetValue}")

                # Confirm speed
                elif char == " ":
                    print("Toggling Run")
                    print(f"L pos: {encoderReadL.get()}, R pos{encoderReadR.get()}")

                    # Toggle Run Flag for both motors
                    RunR.put(not(RunR.get()))
                    RunL.put(not(RunL.get()))


                    Lvel = SetValue
                    Rvel = SetValue
                    #updateNorth.put(True)
                    #print("North Set")
                
                # Turn off IR sensor
                elif str(char) == "0":
                    IRRead.put(0)
                    print("IR Sensor Off")

                # Turn on IR sensor
                elif str(char) == "1":
                    IRRead.put(1)
                    print("IR Sensor On")

                # Request Calibrate High signal reading
                elif str(char) == "2":
                    IRRead.put(2)
                    print("Calibrating High")

                # Request Calibrate Low signal floor
                elif str(char) == "3":
                    IRRead.put(3)
                    print("Calibrating Low")

                # Request Calibrate Low signal floor
                elif str(char) == "4":
                    IRRead.put(4)
                    print("IR Reset")
                elif str(char) == "6":
                    IRRead.put(6)
                    print("IR Only")

                # Report last IR reading values
                if str(char) == "5":
                    print("Values:")
                    for share in IR_shares:
                        print(share.get())
                    print(IRcentroid.get())

                # Manually steer Romi
                elif char == "i":
                    Lvel += 5
                    Rvel += 5
                elif char == "j":
                    Lvel -= 5
                    Rvel += 5
                elif char == "k":
                    Lvel -= 5
                    Rvel -= 5
                elif char == "l":
                    Lvel += 5
                    Rvel -= 5

                # Enable/Disable the IMU tasks steering and set its "north"
                elif char == "c":
                    enableCompass.put(not(enableCompass.get()))
                    if enableCompass.get():
                        print("Compass Enabled")
                        updateNorth.put(True)
                        print("North Set")
                    else: 
                        print("Compass Not Enabled")
                elif char == "n":
                    updateNorth.put(True)
                    print("North Set")
                speedL.put(Lvel)
                speedR.put(Rvel)
                
        else:
            raise ValueError("State out of Range")
        yield 0

def motorL(shares):
    """
    Task that handles the Left Motor and Encoder
    """
    MotorEffTimer,effort,RunFlg,IMUerror,encoderRead,IRerror = shares

    # Encoder Timers Setup
    MotorEncoderL = pyb.Timer(3, period = 0xFFFF, prescaler = 0) # L Motor Encoder Timer
    EncObj = encoderObj.Encoder(MotorEncoderL,pyb.Pin.cpu.B4,pyb.Pin.cpu.B5)

    # Left Motor Logical Pins
    MotorEnableL = Pin(Pin.cpu.C9, mode=Pin.OUT_PP) # L Motor Enable nSLP
    MotorDirL = Pin(Pin.cpu.C8, mode=Pin.OUT_PP) # L Motor Dir DIR
    # L Motor Effort create the timer object PB10 TIM2ch4
    MotorEffortL = MotorEffTimer.channel(3, pin=Pin.cpu.B10, mode=Timer.PWM, pulse_width_percent=0)
    Motor = motorObj.Motor(MotorEffortL,MotorDirL,MotorEnableL) # Motor and Encoder object creation

    eff = 0
    startupAdjust = 0.18 # Experimentally determined to cause Romi to drive straight.


    # Set up Finite State Machine
    state = 0
    s0_Init = 0
    s1_Run = 1

    while True:

        # Initialize
        if state == s0_Init:
            effort.put(0)
            Motor.enable()
            state = s1_Run

        # Always run
        elif state == s1_Run:
            EncObj.update()
            encoderRead.put(EncObj.get_position())

            desired = effort.get()*(1 - IRerror.get()/2) - IMUerror.get()

            eff = desired + math.copysign(startupAdjust,desired)
            Motor.set_effort(eff*RunFlg.get())


        else:
            raise ValueError("State out of Range")
        yield 0

def motorR(shares):
    """
    Task that handles the Right Motor and Encoder
    """
    MotorEffTimer,effort,RunFlg,IMUerror,encoderRead,IRerror = shares

    # Right Motor Logistical Pins
    MotorEnable = Pin(Pin.cpu.A10, mode=Pin.OUT_PP) # R Motor Enable nSLP
    MotorDir = Pin(Pin.cpu.B13, mode=Pin.OUT_PP) # R Motor Dir DIR
    # R Motor Effort create the timer object PB3 TIm2ch2
    MotorEffort = MotorEffTimer.channel(2, pin=Pin.cpu.B3, mode=Timer.PWM, pulse_width_percent=0) 
    Motor = motorObj.Motor(MotorEffort,MotorDir,MotorEnable) # Motor and Encoder object creation
    
    # Encoder Timers Setup
    MotorEncoder = pyb.Timer(8, period = 0xFFFF, prescaler = 0) # R Motor Encoder Timer
    EncObj = encoderObj.Encoder(MotorEncoder,pyb.Pin.cpu.C6,pyb.Pin.cpu.C7)


    eff = 0
    startupAdjust = 3.5 # Experimentally determined to cause Romi to drive straight.


    # Set up Finite State Machine
    state = 0
    s0_Init = 0
    s1_Run = 1

    while True:

        # Initialize
        if state == s0_Init:
            effort.put(0)
            Motor.enable()
            state = s1_Run

        # Always run
        elif state == s1_Run:                        
            EncObj.update()
            encoderRead.put(EncObj.get_position())

            desired = effort.get()*(1 + IRerror.get()/2) + IMUerror.get()

            eff = desired + math.copysign(startupAdjust,desired)
            Motor.set_effort(eff*RunFlg.get())

        else:
            raise ValueError("State out of Range")
        yield 0

def IRsensor(shares):
    readMode, values, centroid, err, goal = shares
    
    CtrlPin = pyb.Pin(pyb.Pin.cpu.B14, mode=Pin.OUT_PP)
    PinList = [
        pyb.Pin.cpu.C4, #IR 1
        pyb.Pin.cpu.B1, #IR 2
        pyb.Pin.cpu.C0, #IR 3
        pyb.Pin.cpu.A7, #IR 4
        pyb.Pin.cpu.C1, #IR 5
        pyb.Pin.cpu.A6, #IR 6
        pyb.Pin.cpu.B0, #IR 7
        pyb.Pin.cpu.C5, #IR 8
        pyb.Pin.cpu.A4, #IR 9
        pyb.Pin.cpu.C3, #IR 10
        pyb.Pin.cpu.A1, #IR 11
        pyb.Pin.cpu.C2, #IR 12
        pyb.Pin.cpu.A0, #IR 13
    ]
    
    lineIdxGoal = 7
    Controller = IRcontrollerObj.IRcontroller(CtrlPin,PinList)

    # Create PID & constants
    Kp = 1
    Ki = 0
    Kd = 0
    IrPID = PIDobj.PID(Kp,Ki,Kd)
    
    # Set up Finite State Machine
    state = 0
    s0_Init = 0
    s1_Read = 1
    s2_Off = 2

    while True:

        # Initialize
        if state == s0_Init:
            prevTime = time.ticks_us()
            goal.put(lineIdxGoal)
            state = s1_Read

        # Read for Line data
        elif state == s1_Read:

            # Turn on, Read, then turn off
            Controller.enable()
            time.sleep(30/1e6)
            data = Controller.update()
            Controller.disable()

            # Calculate Centroid of line readings
            total,weightSum = 0,0
            for i,datum in enumerate(data):
                values[i].put(datum)
                total += datum
                weightSum += (i+1)*datum

            try:
                location = weightSum/total
            except ZeroDivisionError:
                location = 0

            # Compute error if a line reading can be found.
            currTime = time.ticks_us()
            if total > 0 and max(data) > 70:
                diff = lineIdxGoal - location
                if abs(diff) < 0.1:
                    IrPID.reset() 
                dT = time.ticks_diff(currTime,prevTime)
                err.put(IrPID.update(diff,dT))
                centroid.put(location)
            else:
                centroid.put(0)
            prevTime = currTime
            
            # Check if a mode change was requested
            mode = readMode.get()
            if mode == 1 or mode == 6:
                yield 0
                continue
            elif mode == 0:
                centroid.put(0)
                err.put(0)
                IrPID.reset()
                state = s2_Off
            elif mode == 2:
                Controller.enable()
                time.sleep(30/1e6)
                Controller.calibrateHigh()
                Controller.disable()
                readMode.put(1)
            elif mode == 3:
                Controller.enable()
                time.sleep(30/1e6)
                Controller.calibrateLow()
                Controller.disable()
                readMode.put(1)

        # Don't read, in order to save power but check for re-enable.
        elif state == s2_Off:
            mode = readMode.get()
            if not mode:
                yield 0
                continue
            elif mode == 1 or mode == 6:
                state = s1_Read
            elif mode == 2:
                Controller.enable()
                time.sleep(30/1e6)
                Controller.calibrateHigh()
                Controller.disable()
                readMode.put(0)
            elif mode == 3:
                Controller.enable()
                time.sleep(30/1e6)
                Controller.calibrateLow()
                Controller.disable()
                readMode.put(0)
        yield 0

def IMU_task(shares):
    ErrShare,enableCompass,updateNorth,IMUheading,desiredHeading,IMUBraine = shares

    # Define Required Pins
    IMU_RST = Pin(Pin.cpu.B2, mode=Pin.OUT_PP)
    IMU_RST.high()
    IMU_SDA = Pin(Pin.cpu.B9, mode=Pin.ALT, alt=Pin.AF4_I2C1)
    IMU_SCL = Pin(Pin.cpu.B8, mode=Pin.ALT, alt=Pin.AF4_I2C1)

    # Establish i2C communication behavior
    i2c = pyb.I2C(1) # create on bus 1
    i2c = pyb.I2C(1, pyb.I2C.CONTROLLER) # create and init as a controller
    i2c.init(pyb.I2C.CONTROLLER, baudrate=400000) # init as a controller
    MainObj = IMUObj.IMU(i2c,IMU_RST)
    
    errortol = .3 #random.randint(50,100)/100
    delayTimer = 0
    setup = False

    # Create PID
    Kp = 80
    Ki = 0.001
    Kd = 60
    Controller = PIDobj.PID(Kp,Ki,Kd)

    # Set up Finite State Machine
    state = 0
    s0_Init = 0
    s1_Config = 1
    s2_Delay = 2
    s3_Read = 3

    while True:
        
        # Repeatedly attempt to establish i2c connection to IMU
        if state == s0_Init:
            results = i2c.scan()
            refAngle = 0
            if results != []:
                state = s1_Config
                MainObj.changeMode("CONFIG")
                delayTimer = 7e3
                prevtime = time.ticks_us()

        # Change to NDOF mode
        elif state ==s1_Config:
            MainObj.setCalibrate()
            MainObj.changeMode("NDOF")
            delayTime = 20e3
            setup = True
            prevtime = time.ticks_us()
            state = s2_Delay

        # Act as a wait timer while IMU changes modes
        elif state == s2_Delay:
            if delayTimer <= 0:
                state = s1_Config
                if setup:
                    state = s3_Read
            currtime = time.ticks_us()
            delayTimer -= time.ticks_diff(currtime,prevtime)
            prevtime = currtime

        # Read Data
        elif state == s3_Read:
            # If compass navigation isn't enabled, skip
            if not enableCompass.get():
                Controller.reset()
                IMUerror.put(0)
                heading = 0
                yield 0
                continue

            # Record heading data
            currtime = time.ticks_us()
            angleData = MainObj.update()
            yaw,roll,pitch = angleData[:3]
            xrate,yrate,zrate = angleData[3:]
            dt = time.ticks_diff(currtime,prevtime)
            prevtime = currtime
            heading = yaw/900
            IMUheading.put(heading)
            
            # If reseting the reference angle
            if updateNorth.get():
                refAngle = heading
                updateNorth.put(False)
                print(f"North:{refAngle}")
            
            # Calculate orientation relative to the new "0"
            if heading < refAngle - 3.2:
                heading += 2*3.2
            diff = heading-desiredHeading.get()-refAngle
            if diff > 2*3.2:
                diff -= 2*3.2
            elif diff < -2*3.2:
                diff += 2*3.2

            if diff > 3.2:
                error = (diff-2*3.2)/3.2
            else:
                error = (diff)/3.2

            # If heading is within margin of error, clear accumulated error
            if abs(error) < errortol:
                Controller.reset()
            IMUBraine.put(error) # Difference between desired and current heading
            result = Controller.update(error,dt)
            
            ErrShare.put(result) # Amount of effort change requested from motors

        yield 0 


def Bumps(shares):
    enable, hitBumper = shares

    # Create Bumper Objects
    bumpers = []
    bumpers.append(Bumper.Bumper(Pin.cpu.A15))
    bumpers.append(Bumper.Bumper(Pin.cpu.H0))
    bumpers.append(Bumper.Bumper(Pin.cpu.H1))
    bumpers.append(Bumper.Bumper(Pin.cpu.C12))
    bumpers.append(Bumper.Bumper(Pin.cpu.C10))
    bumpers.append(Bumper.Bumper(Pin.cpu.C11))
    
    # Set up Finite State Machine
    state = 0
    s0_init = 0
    s1_On = 1
    s2_Off = 2

    while True:
        
        # Initialize
        if state == s0_init:
            enable.put(True)
            state = s1_On

        # Update bumpers and check for bump triggers
        elif state == s1_On:
            Bumps = [x.update() for x in bumpers]
            if Bumps.count(True):
                hitBumper.put(True)
        
            if not enable.get():
                state = s2_Off
                for bumper in bumpers:
                    bumper.disable()
        
        # Prevent the bumpers from updating by idling
        elif state == s2_Off:
            if enable.get():
                state = s1_On
                for bumper in bumpers:
                    bumper.disable()

        yield 0


def Brain(shares):
    (speedL,speedR,
     IRRead,IR_shares,IRcentroid,
     RunL,RunR,enableCompass,updateNorth,Lpos,Rpos,IMUerror,desiredHeading,Bumperhit,BumpEnable) = shares

    # Setup Individual Gains for PID
    eff = 0

    # Create all line segment distances
    d1 = 8 # Straightaway
    d2 = 16 # To Checkpoint 1
    d3 = 14.5 # To Checkpoint 2
    d4 = 12 # Through Bonus Objective 1
    d5 = 4 # To Checkpoint 3
    d6 = 13 # To Checkpoint 4
    d7 = 20 # Through Metal Structure
    d8 = 13 # Minimum distance to Wall
    d9 = 8 # To Bonus Objective 2
    d10 = 8 # Distance to Original Straightaway
    d11 = 12 # Return to Start
    d = [0,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11]


    # Create all angles needed
    psi1 = 0 # Reference angle
    psi2 = 0.551654983 # Toward Checkpoint 1
    psi3 = -0.713060833 # Toward Checkpoint 2
    psi4 = 1.508377517 # Toward Bonus Objective 1
    psi5 = 1.73869225 # Toward Checkpoint 3
    psi6 = -3.1 # Toward Checkpoint 4
    psi7 = -3.2 # Navigable direction of Metal Structure
    psi8 = -0.5*math.pi # Toward Wall
    psi9 = 0*math.pi # Toward Bonus Objective 2
    psi10 = -0.5*math.pi # Perpendicular to Straightaway
    psi11 = -1*math.pi # Back toward start.
    psi = [0,psi1,psi2,psi3,psi4,psi5,psi6,psi7,psi8,psi9,psi10,psi11]

    maxspeed = 70 # Speed Romi should attempt to race with
    errortol = .25 # Permissible error in heading in radians
    backupdist = -2 # After hitting the wall, reverse this distance
    maxcount = 10 # Wait clock reset value
    walloffsetv = 40 # Amount of speed reduction when approaching wall

    # Set up Finite State Machine
    state               = 0
    s00_Init            = 0
    s01_section1        = 1
    s02_turn            = 2
    s03_straight        = 3
    s04_wall            = 4
    s05_backup          = 5
    s06_off             = 6

    while True:
        
        # Initialize
        if state == s00_Init:
            state = s01_section1
            eff = 0
            speedL.put(eff)
            speedR.put(eff)
            LposPre = Lpos.get()
            RposPre = Rpos.get()
            section = 1
        
        # Move forward and get initial readings
        elif state == s01_section1:
            if IRRead.get() == 6:
                d[1] = 100
            eff = maxspeed
            speedL.put(eff)
            speedR.put(eff)
            dist = ((Lpos.get()-LposPre) + (Rpos.get()-RposPre))/2

            # If path length exceeds target distance, next step.
            if dist > d1:
                section += 1
                state += 1
                count = 0
                eff = 0
                speedL.put(eff)
                speedR.put(eff)
                if IRRead.get():
                    IRRead.put(0)
                    print("IR Sensor Off")
                    enableCompass.put(True)
                    print("Compass Enabled")
                    updateNorth.put(True)
                    print("North Set")

        # Behavior for rotating in place
        elif state == s02_turn:
            # Give IMU task a new preferenced heading
            desiredHeading.put(psi[section])

            # If heading is within tolerance, continue
            if abs(IMUerror.get()) < errortol:
                count += 1
                LposPre = Lpos.get()
                RposPre = Rpos.get()

                # Determine which behavior is required next
                if section == 8 and count > maxcount:
                    state = s04_wall
                    Bumperhit.put(False)
                elif section < len(d) and count > maxcount:
                    state = s03_straight
                else:
                    state = s02_turn

        # Behavior for driving straight
        elif state == s03_straight:

            # Request Speed
            eff = maxspeed
            speedL.put(eff)
            speedR.put(eff)

            dist = ((Lpos.get()-LposPre) + (Rpos.get()-RposPre))/2

            # If path length exceeds target distance, next step.
            if dist > d[section]:
                eff = 0
                speedL.put(eff)
                speedR.put(eff)
                section += 1
                if section < len(d):
                    state = s02_turn
                    count = 0
                else:
                    state = s06_off
                    print("Done")

        # Move forward while checking for collision
        elif state == s04_wall:
            eff = maxspeed - walloffsetv
            speedL.put(eff)
            speedR.put(eff)
            dist = ((Lpos.get()-LposPre) + (Rpos.get()-RposPre))/2

            # If path length exceeds target distance and a collision occured, next step.
            if dist > (d[section]) and Bumperhit.get():
                LposPre = Lpos.get()
                RposPre = Rpos.get()
                eff = 0
                speedL.put(eff)
                speedR.put(eff)
                Bumperhit.put(False)
                state = s05_backup

        # Back up after Wall hit
        elif state == s05_backup:
            eff = -maxspeed
            speedL.put(eff)
            speedR.put(eff)
            dist = -abs(((Lpos.get()-LposPre) + (Rpos.get()-RposPre))/2)

            # If path length exceeds target distance, next step.
            if dist < backupdist:
                eff = 0
                speedL.put(eff)
                speedR.put(eff)
                if section < len(d):
                    section += 1
                    state = s02_turn
                    count = 0
                else:
                    continue

        # Idle and disable Romi
        elif state == s06_off:
            RunL.put(False)
            RunR.put(False)
            IRRead.put(0)
            enableCompass.put(False)
            BumpEnable.put(False)     
        yield 0      


if __name__ == "__main__":
    # Motor PWM Timer Setup
    MotorEffTimer = pyb.Timer(2, freq=22000) # Motor Effort Timer

    # Create Required Shares
    m_effL = task_share.Share('b', thread_protect=False, name="L Motor Effort")
    m_effR = task_share.Share('b', thread_protect=False, name="R Motor Effort")
    RunL = task_share.Share('B', thread_protect=False, name="L Motor Run Flg")
    RunR = task_share.Share('B', thread_protect=False, name="R Motor Run Flg")

    IRRead = task_share.Share('B', thread_protect=False, name="Read IR Mode")
    IRcentroid = task_share.Share('f', thread_protect=False, name="Centroid Location")
    IRgoal = task_share.Share('B', thread_protect=False, name="Desired Centroid Location")
    IR_shares = []
    for i in range(13):
        temp = task_share.Share('I', thread_protect=False, name=f"IR {i}")
        temp.put(False)
        IR_shares.append(temp)
    IR_shares = tuple(IR_shares)
    IRerror = task_share.Share('f', thread_protect=False, name="Centroid Error")
    IMUerror = task_share.Share('f', thread_protect=False, name="Heading Error")
    enableCompass = task_share.Share('B', thread_protect=False, name="Compass Enable")
    updateNorth = task_share.Share('B', thread_protect=False, name="Update North")
    enableCompass.put(False)
    updateNorth.put(False)
    idealHeading = task_share.Share('f', thread_protect=False, name="Ideal Heading")
    IMUheading = task_share.Share('f', thread_protect=False, name="IMU Heading")
    IMUBraine = task_share.Share('f', thread_protect=False, name="IMU Brain Error")
    encoderReadL = task_share.Share('f', thread_protect=False, name="Encoder Read L")
    encoderReadR = task_share.Share('f', thread_protect=False, name="Encoder Read R")
    BumpEnable = task_share.Share('B', thread_protect=False, name="Bumper Enable Flg")

    BumperTrigger = task_share.Share('B', thread_protect=False, name="Triggered Bumpers")

    task1 = cotask.Task(communicate, name="Communicate", priority=3, period=25,
                        profile=True, trace=False,
                        shares=(m_effL,m_effR,
                                IRRead,IR_shares,IRcentroid,
                                RunL,RunR,enableCompass,updateNorth,encoderReadL,encoderReadR))
    MotorL = cotask.Task(motorL, name="motorL", priority=5, period=10,
                        profile=True, trace=False, 
                        shares=(MotorEffTimer,m_effL,RunL,IMUerror,encoderReadL,IRerror))
    MotorR = cotask.Task(motorR, name="motorR", priority=5, period=10,
                        profile=True, trace=False, 
                        shares=(MotorEffTimer,m_effR,RunR,IMUerror,encoderReadR,IRerror))
    IRsensors = cotask.Task(IRsensor, name="Line Sense",priority=1, period=20,
                        profile=True, trace=False,
                        shares=(IRRead,IR_shares,IRcentroid,IRerror,IRgoal))
    IMUtask = cotask.Task(IMU_task, name="IMU board",priority=1, period = 22,
                        profile=True, trace=False,
                        shares=(IMUerror,enableCompass,updateNorth,IMUheading,idealHeading,IMUBraine))
    Bumping = cotask.Task(Bumps, name="Bumpers",priority=2, period = 50,
                        profile=True, trace=False,
                        shares=(BumpEnable,BumperTrigger))
    BrainTask = cotask.Task(Brain, name="Brain", priority=4, period=25,
                        profile=True, trace=False,
                        shares=(m_effL,m_effR,
                                IRRead,IR_shares,IRcentroid,
                                RunL,RunR,enableCompass,updateNorth,
                                encoderReadL,encoderReadR,IMUBraine,idealHeading,BumperTrigger,BumpEnable))
    
    cotask.task_list.append(task1)
    cotask.task_list.append(MotorL)
    cotask.task_list.append(MotorR)
    cotask.task_list.append(IRsensors)
    cotask.task_list.append(IMUtask)
    cotask.task_list.append(Bumping)
    cotask.task_list.append(BrainTask)

    ##########
    ##########
    ##########    !!!  Note: All code beyond this point was copied
    ##########          from basic_task.py from the co-task
    ##########            library provided to us in ME 405 lab
    ##########
    ##########

    print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
          "Press Ctrl-C to stop and show diagnostics.")
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()
    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')