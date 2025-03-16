from pyb import Pin
class Motor:
    '''A motor driver interface encapsulated in a Python class. Works with
    motor drivers using separate PWM and direction inputs such as the DRV8838
    drivers present on the Romi chassis from Pololu.'''
    def __init__(self, PWM, DIR, nSLP):
        '''Initializes a Motor object'''
        self.nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self.DIR = Pin(DIR, mode=Pin.OUT_PP, value=0)
        self.PWM = PWM
        
    def set_effort(self, effort):
        '''Sets the present effort requested from the motor based on an input value
        between -100 and 100'''
        if effort >= 0:
            self.DIR.low()
        elif effort < 0:
            self.DIR.high()
        self.PWM.pulse_width_percent(abs(effort))

    def enable(self):
        '''Enables the motor driver by taking it out of sleep mode into brake mode'''
        self.nSLP_pin.high()
        
    def disable(self):
        '''Disables the motor driver by taking it into sleep mode'''
        self.nSLP_pin.low()