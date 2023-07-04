import time
import math

from tecancavro.models import CentrisB
from tecancavro.transport import TecanAPISerial

class Vitals:
    """
    System-level methods managing delays and halts.
    """

    def __init__(self, pump, disp_valve=None, aspir_valve=None):
        """
        Object constructor function, save pump and valve references

        Args:
            'pump' (obj) : reference to pump object
        Kwargs:
            'disp_valve' (obj) : reference to dispensing valve object
            'aspir_valve' (obj) : reference to aspirating valve object
        """
        self.pump = pump
        self.disp_valve = disp_valve
        self.aspir_valve = aspir_valve

    def autoWash(self, wells_list, period_s, name='', report_s=300):
        """
        For every Well in 'wells_list', continuously aspirate through the inlet
        port and dispense out the outlet port for the duration of 'period_s'.
        This process entails aspiration through the fluidic rig of the entire
        system

        Args:
            'wells_list' (list) : list of all Well objects to wash
            'period_s' (float) : washing time period in seconds
        Kwargs:
            `name' (str) : give a label to the wash
            'report_s' (float) : frequency of generating a status report
        """

    def sysDelay(self, period_s, name='', report_s=300):
        """
        Let the system idle for 'period_s' seconds and generate delay status report
        at frequency of 'report_s'.

        Args:
            'period_s' (float) : delay period in seconds
        Kwargs:
            `name' (str) : give a label to the delay period
            'report_s' (float) : frequency of generating a status report
        """
        delay_params = {
            'name': name,
            'complete': False,
            'tic': time.time(),
            'duration': period_s,
            'iteration': 0,
            'report_s': report_s
        }

        # Manage delay and reporting
        while not delay_params['complete']:
            toc = time.time()
            if toc - delay_params['tic'] >= delay_params['duration']:
                delay_params['complete'] = True
                break
            if report_s is not None:
                if math.floor((toc - delay_params['tic']) / delay_params['report_s']) >= \
                        delay_params['iteration']:
                    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    msg = '{0} \t{1} \t{2}s complete of \t{3}s delay '
                    print(msg.format(time_stamp, delay_params['name'],
                                     delay_params['iteration'] * delay_params['report_s'],
                                     delay_params['duration']))
                    delay_params['iteration'] += 1
            time.sleep(5)  # idle for 5 seconds


class Well:
    """
    Class to instantiate a well (isolated experiment), saving attributes if in_port,
    out_port, and the parameters regarding replenishment cycles.
    """

    def __init__(self, pump, source_port, in_port, out_port, exhaust_port, in_volume_ul,
                 out_volume_ul, period_s, tic, speed=12, disp_valve=None, disp_port=None,
                 aspir_valve=None, aspir_port=None, name=''):
        """
        Object constructor function.

        Args:
            'pump' (obj) : reference to pump object
            `source_port' (int) : 'pump' port for media reservoir
            `in_port' (int) : 'pump' port for reagent delivery (to well)
            'out_port' (int) : 'pump' port for reagent extraction (to waste)
            'exhaust_port' (int) : port for non-fluidic, open exhaust
            'in_volume_ul' (float) : absolute volume (uL) to deliver at intervals
                                     of 'period_s'
            'out_volume_ul' (float) : absolute volume (uL) to aspirate at intervals
                                      of 'period_s'
            'period_s' (float) : frequency of reagent deliverance
            'tic' (int) : starting time of schedule (sec)
        Kwargs:
            'speed' (int)
            'disp_valve' (obj) : reference to dispensing valve object
            `disp_port' (int) : 'disp_valve' port for reagent delivery (to well)
            'aspir_valve' (obj) : reference to aspirating valve object
            'aspir_port' (int) : 'aspir_vavle' port for reagent extraction (to waste)
            `name' (str) : give a label to the well

        """
        self.pump = pump
        self.source_port = int(source_port)
        self.in_port = int(in_port)
        self.out_port = int(out_port)
        self.exhaust_port = int(exhaust_port)
        self.in_volume_ul = float(in_volume_ul)
        self.out_volume_ul = float(out_volume_ul)
        self.period_s = float(period_s)
        self.tic = int(tic)
        self.speed = int(speed)
        self.name = str(name)

        # State
        self.state = {
            'iteration': 0,
            'in_volume': 0,
            'out_volume': 0,
            'disp_valve': False,
            'aspir_valve': False,
            'syringe_volume': 0
        }
        self.disp_valve = disp_valve
        if self.disp_valve is not None:
            self.state['disp_valve'] = True
        self.disp_port = disp_port
        self.aspir_valve = aspir_valve
        if self.aspir_valve is not None:
            self.state['aspir_valve'] = True
        self.aspir_port = aspir_port

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

    def replenishmentCycle(self, source_port=None, in_volume_ul=None, in_port=None, out_volume_ul=None,
                           out_port=None):
        """
        Conduct a replenishment cycle: extract 'out_volume_ul' from 'out_port' and
        dispense 'in_volume_ul' from 'in_port'

        """

        source_port = source_port if source_port is not None else self.source_port
        in_volume_ul = in_volume_ul if in_volume_ul is not None else self.in_volume_ul
        in_port = in_port if in_port is not None else self.in_port
        out_volume_ul = out_volume_ul if out_volume_ul is not None else self.out_volume_ul
        out_port = out_port if out_port is not None else self.out_port

        # Check syringe fill
        self.checkSyringe()
        if self.state['syringe_volume'] < in_volume_ul:
            self.fillSyringe(source_port)
        self.pump.setSpeed(self.speed)

        # Aspirate - Dry pump
        if self.state['aspir_valve']:
            self.aspir_valve.changePort(self.aspir_port)
            self.aspir_valve.executeChain()
            self.aspir_valve.waitReady(delay=0.5)
        self.pump.aspirate(out_port, out_volume_ul)
        self.pump.executeChain()
        self.pump.waitReady(delay=2)

        self.pump.dispense(self.exhaust_port, out_volume_ul)
        self.pump.executeChain()
        self.pump.waitReady(delay=2)

        # Dispense - Wet pump
        if self.state['disp_valve']:
            self.disp_valve.changePort(self.disp_port)
            self.disp_valve.executeChain()
            self.disp_valve.waitReady(delay=0.5)
        self.pump.dispense(in_port, in_volume_ul)
        self.pump.delayExec(2000)
        self.pump.changePort(self.exhaust_port)
        self.pump.executeChain()
        self.pump.waitReady(delay=2)

        # State update
        self.state['iteration'] += 1
        self.state['in_volume'] += in_volume_ul
        self.state['out_volume'] += out_volume_ul
        self.checkSyringe()

    def checkSyringe(self):
        """
        Check the plunger position
        """

        # State update
        time.sleep(1)  # idle for 1 seconds
        plunger_pos = self.pump.getPlungerPos()
        self.state['syringe_volume'] = plunger_pos

    def fillSyringe(self, source_port=None, speed=14):
        """
        Fill the syringe vial from 'source_port'
        """

        source_port = source_port if source_port is not None else self.source_port

        # Fill syringe
        self.pump.setSpeed(speed)
        self.pump.changePort(source_port)
        self.pump.delayExec(1000)
        self.pump.movePlungerAbs(700)
        self.pump.delayExec(1000)
        delay = self.pump.executeChain()
        self.pump.waitReady(delay=3)

        # State update
        self.checkSyringe()

    def statusReport(self):
        """Print the contents of self.state in table format."""
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '{0} \t{1} \tIter: {2} \tVol In: {3} \tVol Out: {4} \tSyringe Vol: {5}'
        print(msg.format(time_stamp, self.name, self.state['iteration'],
                         self.state['in_volume'], self.state['out_volume'],
                         self.state['syringe_volume']))


if __name__ == '__main__':
    # Initialization
    centris_pump = CentrisB(com_link=TecanAPISerial(0, 'COM6', 9600), waste_port=6, microliter=True)
    vitalsSystem = Vitals(centris_pump)

    # Optional: When you want to initialize
    #centris_pump.init(in_port=6, out_port=6, init_force=10)

    time.sleep(1)  # idle for 1 seconds

    # Experimental design
    centris_pump.setSpeed(14)  # 14 is standard, higher for slower, lower for faster
    experiment_params = {
        'complete': False,
        'tic': time.time(),
        'duration': 60 * 60 * 24 * 30,
        'wells_list': []
    }
    # Well 1: 300uL every 20sec
    experiment_params['wells_list'].append(Well(pump=centris_pump,
                                                source_port=1,  # Reservoir source port
                                                in_port=2,  # Dispense IN port
                                                out_port=5,  # Aspirate OUT port
                                                exhaust_port=6,  # Purge bubbles from syringe port
                                                in_volume_ul=150,  # IN volume (uL)
                                                out_volume_ul=150,  # OUT volume (uL)
                                                period_s=30,  # Frequency (sec)
                                                tic=experiment_params['tic'],
                                                speed=18,  # 14 is standard, higher for slower, lower for faster
                                                name="Well #1"))

    # Optional: When you want to fill the syringe
    #experiment_params['wells_list'][0].fillSyringe()

    # Manage replenishment cycles
    while not experiment_params['complete']:
        toc = time.time()
        if toc - experiment_params['tic'] >= experiment_params['duration']:
            experiment_params['complete'] = True
            break
        for well in experiment_params['wells_list']:

            time.sleep(1.5)  # idle for 1.5 second

            if well.queryStatus(toc):
                well.replenishmentCycle()
                well.statusReport()
        time.sleep(5)  # idle for 5 seconds
