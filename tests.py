import unittest
import datetime
import time
import logging
import signal
from threading import Thread
from daytime import DayTime
from sequence import Timer
from sequence import DaytimeTimer
from sequence import Sequence
from sequence import Cmd


#TODO: tests for the DayTimeTimer...

class Mixin:
    def setUp(self):
        self.initlogger()
        self.inittimer()
        self.initcmds()
        self.initsequence()
        self.startsequence()

    def inittimer(self):
        self.interval = 6
        self.count = 3
        self.timer = Timer(self.interval)

    def initcmds(self):
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


        self.wait1 = 2
        self.wait2 = 4
        self.wait3 = 1
        times = list()
        daytime = DayTime.daytime()
        for x in [1,3]: times.append((daytime + self.interval*x))
        self.cmd0 = Cmd(cmd0)
        self.cmd1 = Cmd(cmd1, args=[self.wait1], join=True, stall=0.5, wait=0.2)
        self.cmd2 = Cmd(cmd2, args=[self.wait2], wait=1)
        self.cmd3 = Cmd(cmd3, args=[self.wait3], times=times, delay=self.cmd1._wait + self.wait1 + self.cmd1._stall + 1)

    def initsequence(self):
        self.sequence = Sequence(self.timer, [self.cmd0, self.cmd1, self.cmd2, self.cmd3])

    def startsequence(self):
        logger = logging.getLogger('startandstop')
        #start as non-daemonized thread
        thread = Thread(target=self.sequence.run)
        thread.start()

        #stop after <self.count> finished sequences and one started
        try: time.sleep(self.interval * self.count + 2)
        except KeyboardInterrupt: logger.error('KeyboardInterrupt')
        self.sequence.stop(True)
        logging.shutdown()

    def initlogger(self):
        logformat = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        LOGGER = logging.getLogger(str())
        LOGGER.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(logformat))
        LOGGER.addHandler(handler)
        return logging.getLogger('sequence')

class TestSequence(Mixin, unittest.TestCase):
    def test_sequence(self):
        times0 = [t.as_seconds for t in self.output0]
        times1 = [t.as_seconds for t in self.output1]
        times2 = [t.as_seconds for t in self.output2]
        times3 = [t.as_seconds for t in self.output3]

        self.assertAlmostEqual(times1[0]+self.wait1,times1[1], 1)
        self.assertAlmostEqual(times1[1]+self.cmd1._stall+self.cmd2._wait,times2[0], 1)
        self.assertAlmostEqual(times2[0]+self.wait2, times2[1], 1)
        self.assertAlmostEqual(times0[0]+self.interval, times1[2]-self.cmd1._wait, 1)
        self.assertAlmostEqual(times1[2]+self.wait1,times1[3], 1)
        self.assertAlmostEqual(times1[3]+self.cmd1._stall+self.cmd2._wait,times2[2], 1)
        self.assertAlmostEqual(times1[-2] + self.wait1 + self.cmd1._stall + self.cmd2._wait + self.wait2, times2[-1], 1)

        self.assertGreater(times3[0], self.cmd3._times[0])
        self.assertGreater(times3[2], self.cmd3._times[1])

        #find the appropriate start-round-time
        for t in times0:
            if t > times3[0]: break
            time = t
        self.assertAlmostEqual(time + self.cmd3._delay, times3[0], 1)

        self.assertEqual(self.cmd0.counter, len(times0))

class TestDaytimeTimer(Mixin, unittest.TestCase):
    def inittimer(self):
        self.interval = 6
        self.count = 4
        data = list()
        times = list()
        daytime = DayTime.daytime()
        for x in range(4): times.append(daytime + 10*x)
        for i, t in enumerate(times): data.append((t, self.interval+i))
        self.timer = DaytimeTimer(data=data)

    def test_daytimetimer(self):
        pass


if __name__ == '__main__':
    unittest.main()
