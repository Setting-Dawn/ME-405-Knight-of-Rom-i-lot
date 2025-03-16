import pyb
class IRSensor:

    def __init__(self, pin):
        '''Initializes a single IR senor object'''
        self.ADC = pyb.ADC(pin)
        self.gain = 4095
        self.reset()

    def reset(self):
        self.high = 4095
        self.low = 0
        self.calibrateRange()

    def calibrateHigh(self):
        self.high = self.ADC.read()
        self.calibrateRange()
        
    def calibrateLow(self):
        self.low = self.ADC.read()
        self.calibrateRange()

    def calibrateRange(self):
        self.range = max(self.high - self.low,1)

    def update(self):
        value = self.ADC.read()
        bounded = min(max(value,self.low),self.high)
        value = int(max(self.gain*(bounded-self.low)/self.range,0))
        return value
