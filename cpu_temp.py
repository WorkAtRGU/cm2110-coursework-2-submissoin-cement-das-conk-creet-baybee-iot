from sense_hat import SenseHat

class CPUTemp:
    def __init__(self, tempfilename = "/sys/class/thermal/thermal_zone0/temp"):
        self.tempfilename = tempfilename

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.tempfile = open(self.tempfilename, "r")
    
    def read(self):
        self.tempfile.seek(0)
        return self.tempfile.read().rstrip()

    def get_temperature(self):
        return self.get_temperature_in_c()

    def get_temperature_in_c(self):
        tempraw = self.read()
        return float(tempraw[:-3] + "." + tempraw[-3:])

    def get_temperature_in_f(self):
        return self.convert_c_to_f(self.get_temperature_in_c())
    
    def convert_c_to_f(self, c):
        return c * 9.0 / 5.0 + 32.0

    def __exit__(self, type, value, traceback):
        self.close()
            
    def close(self):
        self.tempfile.close()
        
        
        
    def get_actual_temp(self):
        return temp_calc



# Example of how to use this class
##with CPUTemp() as cpu_temp:
    ##global c
    ##c = cpu_temp.get_temperature()
    ##print("cpu temp %d"%c)

# get the temperature from the Sense HAT temperatur sensors
##sense = SenseHat()

##p = sense.get_temperature_from_pressure()
##h = sense.get_temperature_from_humidity()

##print("Average temp %d"%((p+h)/2))

# factor = 3 appears to work if the RPi is in a case
# change to factor = 5 appears to work for RPi's not in a case
##factor = 3

##temp_calc = ((p+h)/2) - (c/factor)
# temp_calc is accurate to +/- 2 deg C.
##print("Actual temp %d"%temp_calc)