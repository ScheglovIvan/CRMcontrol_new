from ControlStatus import ControlOrderStatus
import time
from datetime import datetime


while True:
    try:
        start_time = datetime.now()
        ControlOrderStatus()
    except:
        pass
    
    time_sleep = 350

    print("time slip " + str(time_sleep) + "sec")
    print(datetime.now() - start_time)

    time.sleep(time_sleep)
    
