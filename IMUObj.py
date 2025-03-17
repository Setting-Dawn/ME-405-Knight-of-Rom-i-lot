import pyb, time, struct
class IMU:

    class reg:
        EULER_YAW = (0x1A,"h")
        EULER_YAW_RATE = (0x18,"h")
    
    def __init__(self,I2Cobj,resetPin):
        self.I2C = I2Cobj
        self.nRST = resetPin

    def reset(self):
        self.nRST.low()
        time.sleep(30/1e6)
        self.nRST.high()

    def changeMode(self,mode):
        if mode == "NDOF":
            val = 0b1100
        elif mode == "CONFIG":
            val = 0b0000
        else:
            pass
        self.I2C.mem_write(val,0x28, 0x3D, timeout=1000)

    def isCalibrate(self):
        buff = bytearray(1)
        self.I2C.mem_read(buff, 0x28, 0x35)
        sys = (buff[0] >> 6) & 3
        gyr = (buff[0] >> 4) & 3
        acc = (buff[0] >> 2) & 3
        mag = buff[0] & 3
        return sys,gyr,acc,mag
    
    def saveCalibrate(self):
        buff = bytearray(22)
        self.I2C.mem_read(buff, 0x28, 0x55)
        for byte in buff:
            print(byte)
        with open("Coefficients.txt","w") as file:
            for byte in buff:
                file.write(str(bin(byte)))
                file.write("\n")

    def update(self):
        buff = bytearray(12)
        self.I2C.mem_read(buff, 0x28, 0x14)
        xrate,yrate,zrate,heading,roll,pitch = struct.unpack("<hhhhhh",buff)

        return heading,roll,pitch,xrate,yrate,zrate

    def setCalibrate(self):
        buff = bytearray(22)
        with open("Coefficients.txt","r") as file:
            for i,line in enumerate(file.readlines()):
                print(line)
                buff[i] = int(line)
        self.I2C.mem_write(buff,0x28,0x55)

    def getAngles(self,selection=None):
        buff = bytearray(4)
        self.I2C.mem_read(buff, 0x28, 0x18)
