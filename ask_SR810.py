import SR_810 as sr_810
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time


#rm = pyvisa.ResourceManager()
#print(rm.list_resources())
#my_instrument = rm.open_resource('ASRL/dev/ttyUSB0::INSTR',read_termination='\r', write_termination='\n')
#my_instrument.write("SNAP?1,3")
#x = my_instrument.read()
#print(x)


sr_810.connection()
#sr_810.lock_in_modulation_frequency(1000)
x = sr_810.lock_in_signal()
#y = sr_810.lock_in_signal()
print(x)
#print(y)

sr_810.close_connection()