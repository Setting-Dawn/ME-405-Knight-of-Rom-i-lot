import pyb
class Bumper:

    def pinBump(self,line):
        """External Interupt function that debounces itself \n
        and increases that bumper's hit-counter
        """
        self.ExtInt.disable()
        self.Hit = True
        self.Count += 1

    def __init__(self, pin):
        """Instantiate an object for handling each bumper \n
        :param pin: is the pin address used for the bumper
        """
        self.pin = pin
        self.reset()

    def reset(self):
        """Resets all handled values to default
        """
        self.ExtInt = pyb.ExtInt(self.pin, pyb.ExtInt.IRQ_FALLING,
                                  pyb.Pin.PULL_UP, self.pinBump)
        self.Hit = False
        self.Count = 0

    def update(self):
        """Re-enables the interupt if triggered \n
        :return Bool: Whether the pin was hit
        """
        if self.Hit:
            self.ExtInt.enable()
            self.Hit = False
            return True
        return False
    
    def getCount(self):
        """Returns the number of hits since last reset \n
        :return Count: The number of times the bumper has triggered since reset
        """
        return self.Count
    
    def enable(self):
        self.ExtInt.enable()
        self.Hit = False

    def disable(self):
        self.ExtInt.disable()
        self.Hit = False

    