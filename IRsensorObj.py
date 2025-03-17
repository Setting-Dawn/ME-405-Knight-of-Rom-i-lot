import pyb
class IRSensor:

    def __init__(self, pin):
        '''Initializes a single IR senor object'''
        self.ADC = pyb.ADC(pin)
        self.gain = 4095
        self.reset()

    def reset(self):
        '''Resets the minimum and maximum bounds'''
        self.high = 4095
        self.low = 0
        self.calibrateRange()

    def calibrateHigh(self):
        '''Sets the maximum reading of "Black" to the current reading'''
        self.high = self.ADC.read()
        self.calibrateRange()
        
    def calibrateLow(self):
        '''Sets the minimum reading of "White" to the current reading'''
        self.low = self.ADC.read()
        self.calibrateRange()

    def calibrateRange(self):
        '''Calculate the difference between the limited bounds'''
        self.range = max(self.high - self.low,1)

    def update(self):
        '''Report readings based on where the unaltered readings 
        fall in the calibration range'''
        value = self.ADC.read()
        bounded = min(max(value,self.low),self.high)
        value = int(max(self.gain*(bounded-self.low)/self.range,0))
        return value
