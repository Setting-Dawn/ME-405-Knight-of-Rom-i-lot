from time import ticks_us, ticks_diff # Use to get dt value in update()
import pyb, math
from array import array
class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim, chA_pin, chB_pin):
        '''Initializes an Encoder object'''

        self.position = 0 # Total accumulated position of the encoder
        self.prev_count = 0 # Counter value from the most recent update
        self.delta = 0 # Change in count between last two updates
        self.dt = 0 # Amount of time in micro seconds between last two updates
        self.prev_ticks = ticks_us()
        self.encTicks2Rad = 1440/(2*math.pi) # (1440 ticks/2pi rad)

        self.tim = tim
        self.tim.channel(1, pin=chA_pin, mode=pyb.Timer.ENC_AB)
        self.tim.channel(2, pin=chB_pin, mode=pyb.Timer.ENC_AB)
        self.prev_Vel = array("f",10*[0])

        self.AR = self.tim.period() + 1

    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
        track of the change in count and check for counter reload'''
        # Get current encoder position
        curr_count = self.tim.counter()
        # Set raw Delta
        self.delta = curr_count - self.prev_count
        # Check if raw Delta is too big
        if abs(self.delta) > (self.AR+1)/2:
            self.delta += -(self.AR+1)*self.delta//max(abs(self.delta),1)
        self.position += self.delta
        self.prev_count = curr_count
        
        curr_ticks = ticks_us()
        self.dt = ticks_diff(curr_ticks,self.prev_ticks)
        self.prev_ticks = curr_ticks

    def get_position(self):
        '''Returns the most recently updated value of position as determined
        within the update() method'''
        return self.position/self.encTicks2Rad
    
    def get_velocity(self):
        '''Returns a measure of velocity using the the most recently updated
        value of delta as determined within the update() method'''
        self.prev_Vel[:-1] = self.prev_Vel[1:]
        self.prev_Vel[-1] = self.delta*1_000_000/(self.dt*self.encTicks2Rad)
        return sum(self.prev_Vel)/len(self.prev_Vel)

    def get_dt(self):
        return self.dt
    
    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
        to measure with respect to the new zero position'''
        print("Zeroing")
        self.position = 0
        self.prev_count = self.tim.counter()