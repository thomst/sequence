import unittest
import datetime
import time
import logging
import signal
from daytime import DayTime
from sequence import Timer
from sequence import Sequence
from sequence import Cmd


#TODO: tests for the DayTimeTimer...

class TestSequence(unittest.TestCase):
    def setUp(self):
        logger = self.init_logger()

        self.output0 = list()
        self.output1 = list()
        self.output2 = list()
        self.output3 = list()

        # this is for catching the start-times of every round
        def cmd0():
            logger = logging.getLogger('cmd0')
            self.output0.append(DayTime.daytime())
            logger.info(self.output0[-1].strftime('%T.%f'))

        def cmd1(wait):
            logger = logging.getLogger('cmd1')
            self.output1.append(DayTime.daytime())
            logger.info(self.output1[-1].strftime('%T.%f'))
            time.sleep(wait)
            self.output1.append(DayTime.daytime())
            logger.info(self.output1[-1].strftime('%T.%f'))

        def cmd2(wait):
            logger = logging.getLogger('cmd2')
            self.output2.append(DayTime.daytime())
            logger.info(self.output2[-1].strftime('%T.%f'))
            time.sleep(wait)
            self.output2.append(DayTime.daytime())
            logger.info(self.output2[-1].strftime('%T.%f'))

        def cmd3(wait):
            logger = logging.getLogger('cmd3')
            self.output3.append(DayTime.daytime())
            logger.info(self.output3[-1].strftime('%T.%f'))
            time.sleep(wait)
            self.output3.append(DayTime.daytime())
            logger.info(self.output3[-1].strftime('%T.%f'))

        self.interval = 6
        self.count = 3

        self.wait1 = 2
        self.wait2 = 4
        self.wait3 = 1
        times = list()
        daytime = DayTime.daytime()
        for x in [1,3]: times.append((daytime + self.interval*x))
        self.cmd0 = Cmd(cmd0)
        self.cmd1 = Cmd(cmd1, args=[self.wait1], join=True, stall=0.5, wait=0.2)
        self.cmd2 = Cmd(cmd2, args=[self.wait2], wait=1)
        self.cmd3 = Cmd(cmd3, args=[self.wait3], times=times, delay=self.cmd1.wait + self.wait1 + self.cmd1.stall + 1)

        sequence = Sequence(Timer(self.interval), [self.cmd0, self.cmd1, self.cmd2, self.cmd3])

        #start as non-daemonized thread
        sequence.thread(daemon=False)

        #stop after <self.count> finished sequences and one started
        try: time.sleep(self.interval * self.count + 2)
        except KeyboardInterrupt: logger.error('KeyboardInterrupt')
        sequence.stop(True)
        logging.shutdown()

    def init_logger(self):
        logformat = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        LOGGER = logging.getLogger(str())
        LOGGER.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(logformat))
        LOGGER.addHandler(handler)
        return logging.getLogger('sequence')

    def test_sequence(self):
        times0 = [t.as_seconds for t in self.output0]
        times1 = [t.as_seconds for t in self.output1]
        times2 = [t.as_seconds for t in self.output2]
        times3 = [t.as_seconds for t in self.output3]

        self.assertAlmostEqual(times1[0]+self.wait1,times1[1], 1)
        self.assertAlmostEqual(times1[1]+self.cmd1.stall+self.cmd2.wait,times2[0], 1)
        self.assertAlmostEqual(times2[0]+self.wait2, times2[1], 1)
        self.assertAlmostEqual(times0[0]+self.interval, times1[2]-self.cmd1.wait, 1)
        self.assertAlmostEqual(times1[2]+self.wait1,times1[3], 1)
        self.assertAlmostEqual(times1[3]+self.cmd1.stall+self.cmd2.wait,times2[2], 1)
        self.assertAlmostEqual(times1[-2] + self.wait1 + self.cmd1.stall + self.cmd2.wait + self.wait2, times2[-1], 1)

        self.assertGreater(times3[0], self.cmd3.times[0])
        self.assertGreater(times3[2], self.cmd3.times[1])

        #find the appropriate start-round-time
        for t in times0:
            if t > times3[0]: break
            time = t
        self.assertAlmostEqual(time + self.cmd3.delay, times3[0], 1)


if __name__ == '__main__':
    unittest.main()
