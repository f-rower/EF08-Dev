''' This code is used to implement flying, landing and perching operations'''
import logging
import pid_param #includes the pid parameters for each flying mode
import time
from threading import Timer
from threading import Thread
from cflib.utils.callbacks import Caller #THis will be useful to create a callback for when a joystick button is pressed.
import gamepad
from Plotter import Plot
#import matplotlib.pyplot as plt  THIS IS TO BE USED FOR PLOTTING ON THE GO.
import cflib.crtp
from cflib.crazyflie import Crazyflie
import logging
import time
from cflib.crazyflie.log import LogConfig

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)
#plt.plot([1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()

class flying:

    def __init__(self, link_uri):
        """ Initialize and run with the specified link_uri """
        print(link_uri)
        # Create a Crazyflie object without specifying any cache dirs
        self._cf = Crazyflie()
        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        #The cf object has these  attributes which are used to call
        # a function when any of these events happen.
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

    # #######Stuff to do on connection/disconnection

    def _connected(self, link_uri):
        print("Connected to crazyflie")
        self.fly()
        self._cf.close_link()
    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False

#############These are the flying, plotting, etc methods

    def fly(self):
        print("I'm flying")
        time.sleep(3)
        self._cf.commander.send_setpoint(0, 0, 0, 0) #THis is so that cf doesn't fly away at the beginning
        the_time = time.time() + 5
        while time.time() < the_time:
            thrust = int(32000*(((gamepad.get())[0])))
            print(thrust)
            self._cf.commander.send_setpoint(0, 0, 0, abs(thrust))
        self._cf.commander.send_setpoint(0, 0, 0, 0)


    def land(self):
        print("I'm landing")

    def perch(self):
        print("I'm perching")

    def log(self):
        print("I'm logging stuff")

    def plot(self):
        print("Plotting stuff")

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print('Scanning interfaces for Crazyflies...')
    available = cflib.crtp.scan_interfaces()
    print('Crazyflies found:')
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = flying(available[0][0])
    else:
        print('No Crazyflies found, cannot run example')