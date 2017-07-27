''' This code is used to implement flying, landing and perching operations'''
import pid_param #includes the pid parameters for each flying mode
import time
from threading import Timer
from threading import Thread
from cflib.utils.callbacks import Caller #THis will be useful to create a callback for when a joystick button is pressed.
import gamepad #For reading gamepad inputs.
import cflib.crtp
from cflib.crazyflie import Crazyflie
import logging
import time
from cflib.crazyflie.log import LogConfig
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from multiprocessing import Process
style.use('fivethirtyeight')

#Constants
PERCHING_EVENT = False #Controls implementation of perching
DISCONNECT = False #Controls when the cf should be disconnected

#GAMEPAD MAPPING

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class Fly_EF08:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        # Create a Crazyflie object without specifying any cache dirs
        self._cf = Crazyflie()

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True


    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)
        t1 = Thread(target = self.listen_disconnect)
        t1.start()

    # CODE FOR LOGGING

        # Add logconfigs for plotting/saving later
        self._lg_vbat = LogConfig(name='pm', period_in_ms=100) #self.lg_stab is a LogConfig object. See log.py for
        # details.
        self._lg_vbat.add_variable('pm.vbat', 'float')
        print(time.strftime("%d/%m/%Y"))
        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_vbat)
            # This callback will receive the data
            self._lg_vbat.data_received_cb.add_callback(self._stab_log_data)#this says what to do when a new set of data is received
            # This callback will be called on errors
            self._lg_vbat.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_vbat.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

    # CALL FLYING CODE

        t2 = Thread(target = self.fly)
        t2.start()

    # METHODS FOR PLOTTING AND ERRORS

    def listen_disconnect(self):
        """Listen for disconnection"""
        while 1:
            if (gamepad.get())[13] != 0:  #Start button
                print("Disconnected from crazyflie")
                self._cf.close_link()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        # logconf, timestamp and data come from the imported LogConfig class.
        """Callback from the log API when data arrives"""
        #print('[%d][%s]: %s' % (timestamp, logconf.name, data))
        f = open("fileread.txt", 'a+')
        f.write("%s," % time.time())
        f.write("%s\n" % data['pm.vbat'])
        f.close()
        # data is a DICTIONARY with entries that can be accessed in the way shown in this line.
        #print(data['stabilizer.roll'])

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

    # FLYING, LANDING AND PERCHING CODE

    def fly(self):
        print("I'm flying")
        # time.sleep(1)
        # THis is so that cf doesn't fly away at the beginning
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        while (gamepad.get())[14] == 0:
            #Change maximum thrust here
            thrust = int(32000*((gamepad.get())[0]))
            #print(thrust)
            #print((gamepad.get())[14])
            self._cf.commander.send_setpoint(0, 0, 0, abs(thrust))
            #self._cf.commander.send_setpoint(0, 0, 0, 0)
        self.land()

    def land(self):
        print("I'm landing")
        global PERCHING_EVENT
        #print(PERCHING_EVENT)
        while not PERCHING_EVENT:
            if (gamepad.get())[6]:
                PERCHING_EVENT = True
            AX_L_H = (gamepad.get())[0]
            AX_L_V = (gamepad.get())[1]
            AX_R_H = (gamepad.get())[3]
            AX_R_V = (gamepad.get())[4] # need some way of updating these values outside the while loop
            #print(AX_R_V,AX_R_H,AX_L_V,AX_L_H)
            if (AX_L_H + AX_L_V + AX_R_H + AX_R_V) <0.2: #This allows for some accidental control touch. The smaller
                # the number, the more sensitive. Consider making just a sum of the ABSOLUTE values.
                self._cf.commander.send_setpoint(0, 0, 0, 500) #sample code
            else:
                self.fly() #If button pressed, go back to flying mode
        self.perch()

    def perch(self):
        print("I'm perching")
        global PERCHING_EVENT
        while PERCHING_EVENT:
            AX_L_H = (gamepad.get())[0]
            AX_L_V = (gamepad.get())[1]
            AX_R_H = (gamepad.get())[3]
            AX_R_V = (gamepad.get())[4]  # need some way of updating these values outside the while loop
            #print(AX_R_V, AX_R_H, AX_L_V, AX_L_H)
            if (AX_L_H + AX_L_V + AX_R_H + AX_R_V) < 0.2:  # This allows for some accidental control touch. The smaller
                # the number, the more sensitive. Consider making just a sum of the ABSOLUTE values.
                self._cf.commander.send_setpoint(0, 0, 0, 1000)  # sample code
            else:
                PERCHING_EVENT = False
                self.fly()  # If button pressed, go back to flying mode



    # MAIN LOOP

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
        le = Fly_EF08(available[0][0])
    else:
        print('No Crazyflies found, cannot run example')

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    #while le.is_connected:
       #time.sleep(5)