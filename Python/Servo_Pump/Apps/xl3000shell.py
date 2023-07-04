import json, time, math
from tecancavro.models import XP3000
from tecancavro.transport import TecanAPISerial

class Well:
    """
    Class to instantiate a well (isolated experiment), saving attributes if in_port
    and the parameters regarding replenishment cycles.
    """

    def __init__(self, pump, in_port, source_port, in_volume_ul, period_s, speed,
                 tic, name=''):
        """
        Object constructor function.

        Args:
            'pump' (obj) : reference to pump object
            `in_port' (int) : 'pump' port for reagent delivery (to well)
            'source_port' (int) : port connected to reservoir source
            'in_volume_ul' (float) : absolute volume (uL) to deliver at intervals
                                     of 'period_s'
            'period_s' (float) : frequency of reagent deliverance
            'speed' (int) : speed code ranging 1(fast)-40(slow)
            'tic' (int) : starting time of schedule (sec)
        Kwargs:
            `name' (str) : give a label to the well

        """
        self.pump = pump
        self.in_port = in_port
        self.source_port = source_port
        self.in_volume_ul = float(in_volume_ul)
        self.period_s = float(period_s)
        self.speed = int(speed)
        self.tic = int(tic)
        self.name = str(name)
        # State
        self.state = {
            'iteration': 0,
            'in_volume': 0,
            'syringe_volume': 0
        }

    def queryStatus(self, t):
        """
        Query if the node is ready for a cycle iteration based on 'period_s' frequency
        and 'start_time'

        :return (boolean): ready to conduct a cycle iteration
        """

        if math.floor((t - self.tic) / self.period_s) >= self.state['iteration']:
            return True
        else:
            return False

    def deliveryCycle(self, in_volume_ul=None, in_port=None, source_port=None):
        """
        Conduct a delivery cycle: dispense 'in_volume_ul' from 'in_port'
        """

        in_volume_ul = in_volume_ul if in_volume_ul is not None else self.in_volume_ul
        in_port = in_port if in_port is not None else self.in_port
        source_port = source_port if source_port is not None else self.source_port

        # Check syringe fill
        self.checkSyringe()
        if self.state['syringe_volume'] <= 1.25 * in_volume_ul:
            self.fillSyringe(source_port)
        # Dispense
        self.pump.setSpeed(self.speed)
        self.pump.dispense(in_port, in_volume_ul)
        self.pump.delayExec(1000)
        self.pump.changePort(source_port)
        delay = self.pump.executeChain() #Command Overflow [15]
        self.pump.waitReady(delay)
        # State update
        self.state['iteration'] += 1
        self.state['in_volume'] += in_volume_ul

    def checkSyringe(self):
        """
        Check the plunger position
        """

        # State update
        plunger_pos = self.pump.getPlungerPos()
        self.state['syringe_volume'] = (plunger_pos / 3000) * self.pump.syringe_ul

    def fillSyringe(self, source_port=None, speed=10):
        """
        Fill the syringe vial from 'source_port'
        """

        source_port = source_port if source_port is not None else self.source_port

        # Fill syringe
        self.pump.setSpeed(speed)
        self.pump.changePort(source_port)
        self.pump.delayExec(1000)
        self.pump.movePlungerAbs(3000) #move the plug absolute possition, 3000 increments, full load 3000 in the srynge
        self.pump.delayExec(1000)
        delay = self.pump.executeChain()
        self.pump.waitReady(delay)
        time.sleep(10)  # idle for 5 seconds look here Command Overflow [15], faster lower value

        # State update
        self.checkSyringe()

    def statusReport(self):
        """Print the contents of self.state in table format."""
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '{0} \t{1} \t\tIter: {2} \tVolume In: {3} \tSyringe Volume: {4}'
        print(msg.format(time_stamp, self.name, self.state['iteration'],
                         self.state['in_volume'], self.state['syringe_volume']))


if __name__ == '__main__':
    # Initialization
    # '/dev/ttyUSB0' for rpi
    # 'COM3' or similar for PC
    xp3000_pump = XP3000(com_link=TecanAPISerial(0, 'COM3', 9600), waste_port=3,
                         debug=True) #initiazilizing
    xp3000_pump.init()
    time.sleep(3)  # idle for 3 seconds

    # Experimental design
    xp3000_pump.setSpeed(12)
    experiment_params = {
        'complete': False,
        'tic': time.time(),
        'duration': 60 * 60 * 24 * 30,
        'wells_list': []
    }

    # Fluid Line I: 20uL every 60sec
    experiment_params['wells_list'].append(Well(pump=xp3000_pump,
                                                in_port='I',
                                                source_port='O',
                                                in_volume_ul=300,
                                                period_s=20, #lower faster period s
                                                speed=5, #lower faster, how many seconds could move the srynge
                                                tic=experiment_params['tic'],
                                                name="Fluid Line I"))
    # Fluid Line E: 10uL every 60sec
    #experiment_params['wells_list'].append(Well(pump=xp3000_pump,
                                                #in_port='E',
                                                #source_port='O',
                                                #in_volume_ul=10,
                                                #period_s=60,
                                                #speed=20,
                                                #tic=experiment_params['tic'],
                                                #name="Fluid Line E"))

    # Fill the syringe
    experiment_params['wells_list'][0].fillSyringe()
    time.sleep(10)  # idle for 5 seconds

    # Manage replenishment cycles
    while not experiment_params['complete']:
        toc = time.time()
        if toc - experiment_params['tic'] >= experiment_params['duration']:
            experiment_params['complete'] = True
            break
        for well in experiment_params['wells_list']:
            time.sleep(5)  # idle for 5 seconds

            if well.queryStatus(toc):
                well.deliveryCycle()
                well.statusReport()
        time.sleep(10)  # idle for 5 seconds