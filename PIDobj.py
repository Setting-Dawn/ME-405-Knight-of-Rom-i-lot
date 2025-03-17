from time import ticks_us,ticks_diff
class PID:
    def __init__(self,Kp,Ki,Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        if Ki != 0:
            self.maxErr = 100/Ki
        else:
            self.maxErr = 0
        self.reset()

    def update(self,error,dT):
        '''Returns a signal based on the sum of: \n
          Kp * error \n
          Ki * accumulated error \n
          Kd * the change in error \n'''
        self.integErr += error*dT
        if self.integErr > self.maxErr:
            self.integErr = self.maxErr
        elif self.integErr < -self.maxErr:
            self.integErr = -self.maxErr

        if self.prev_error == None:
            self.prev_error = error
        self.de_dt = (error-self.prev_error)/dT
        Pcontribute = self.Kp*error
        Icontribute = self.Ki*self.integErr
        Dcontribute = self.Kd*self.de_dt
        return Pcontribute + Icontribute + Dcontribute
    
    def reset(self):
        '''Clears all stored non-constant values including accumulated error'''
        self.integErr = 0
        self.prev_error = None
        self.de_dt = 0