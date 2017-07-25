"""
Code that logs the parameters and plots them.
It should run all the time.
Logged parameters should be written to a file as well.
"""
import logging
import time
from threading import Timer
#import matplotlib.pyplot as plt  THIS IS TO BE USED FOR PLOTTING ON THE GO.

import cflib.crtp  # noqa
from cflib.crazyflie.log import LogConfig

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)
#plt.plot([1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()

class Plot():

    def __init__(self, link_uri, cf):
        """ Initialize and run the example with the specified link_uri and cf object """
        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True
        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer',
                                  period_in_ms=1000)  # self.lg_stab is a LogConfig object FOR THE STABILIZER. See
        # log.py for details.
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')
        self._lg_stab.add_variable('stabilizer.thrust', 'float')
        print(time.strftime("%d/%m/%Y"))
        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            cf.log.add_config(self._lg_stab)  #cf is cf object created in main loop
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(
                self._log_data)  # this says what to do when a new set of data is received
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # Start a timer to disconnect in 5s
        t = Timer(5,print('Done logging')) #TIMER NEEDS A FUNCTION TO DO WHEN IT RUNS OUT OF TIME.
        t.start()
    def _connected(self, link_uri, cf):  #cf is the crazyflie object created in the main loop.
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""



    def _log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _log_data(self, timestamp, data, logconf): #logconf, timestamp and data come from the imported LogConfig class.
        """Callback from the log API when data arrives"""
        print('[%d][%s]: %s' % (timestamp, logconf.name, data))
        f = open("fileread.txt", 'a+')
        f.write("%s\n" % data)
        f.close()
        print(data['stabilizer.roll']) #data is a DICTIONARY with entries that can be accessed in the way shown in this line.
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

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    #while le.is_connected:
        #time.sleep(1)
