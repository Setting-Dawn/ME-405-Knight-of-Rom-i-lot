import pyb,time
import IRsensorObj

class IRcontroller:
    def __init__(self,CtrlPin,ListofPins):
        self.ctrl = CtrlPin
        self.ctrl.low()
        self.evens = []
        self.odds = []
        self.pins = []
        for i,pin in enumerate(ListofPins):
            newSensor = IRsensorObj.IRSensor(pin)
            self.pins.append(newSensor)
        
    def enable(self):
        self.ctrl.high()

    def disable(self):
        self.ctrl.low()
    
    def lowPower(self):
        n = 28
        while n > 0:
            self.ctrl.low()
            time.sleep(100/1e6)
            self.ctrl.high()
            time.sleep(100/1e6)
            n -= 1

    def reset(self):
        for pin in self.pins:
            pin.reset()
                
    def calibrateHigh(self):
        for pin in self.pins:
            pin.calibrateHigh()

    def calibrateLow(self):
        for pin in self.pins:
            pin.calibrateLow()
                
    def calibrateRange(self):
        for pin in self.pins:
            pin.calibrateRange()

    def update(self):
        return [pin.update() for pin in self.pins]

    
            