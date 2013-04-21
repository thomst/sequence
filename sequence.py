#! /usr/bin/env python
# coding=utf-8

# This source-code is part of the fotobox-distribution,
# which is written by Thomas Leichtfuss.
# Copyright 2012, all rights reserved


import time
import logging
import datetime
from threading import Thread
from daytime import DayTime

LOGGER = logging.getLogger('sequence')


class Timer:
    """
    Provides timer-facilities regarding to the needs of Sequenz-class.
    
    Attributes:
        count:      number of passes through a sequenz as an integer
        interval:   interval used for a sequenz as an integer (or float)
        timelag:    latency the check-method was called after interval run down.
                    timelag is set to None if the latency is smaller than or 
                    equal to the latency_tolerance given to the constructor
                    (defaults to 0.01).

    """
    def __init__(self, interval_data, max_count=None, snap=False, latency_tolerance=0.01):
        """
        Constructor of Timer.
        
        Args:
            interval_data:
                Data to generate the interval (s.a. self.actualize).

            snap:
                a boolean specifies if the timer-start will be instantly or
                snapped into a reproduce-able rhythm depending on the value of
                interval.
            
            max_count:
                maximal counts a sequenz should passing through.

            latency_tolerance:
                a float that defines the limit in which timelag is set to None.
        
        Returns a Timer-instance.
        """
        self._data = interval_data
        self._interval = None
        self._snap = snap
        self._max_count = max_count
        self._latency_tolerance = latency_tolerance
        self._stage = None
        self._count = 0
        self._timelag = None
        self._stopped = False

    @property
    def count(self):
        return self._count

    @property
    def interval(self):
        return self._interval

    @property
    def timelag(self):
        return self._timelag

    @property
    def alive(self):
        return bool(self._stage)

    @property
    def runtime(self):
        """
        Returns the seconds the actual sequenz-pass is running.
        
        Returns None if the timer has not started yet or is already stopped.
        
        Mind that this does not mean the seconds since last call to check. The
        check-call actualizes the values whithin a sequenz-pass, but don't set
        the starting point of this pass. The starting Point is evaluated by
        adding the value of interval to a staged point of time, that the whole
        thing started at.
        """
        if self.alive: return time.time() - self._stage
        else: return None

    def actualize(self):
        """
        This is a hook for dynamical evaluation of intervals.

        The initial interval_data will be processed to generate the interval
        and save it as self._interval.
        The method will be called once for each sequence.
        """
        self._interval = self._data

    def start(self):
        """
        Start a timer (Set the the starting time).
        
        If the timer was initialized with snap set to True the starting-time
        will be evaluated depending on the actual interval.
        On that way all sequenzes running with the same interval will be
        synchronized. Stopped and restarted sequenzes will snap into the same
        "rhythm".
        
        With a "snapstart" returns the seconds to wait until first time check()
        returns True.
        Otherwise returns None.
        """
        self.actualize()
        self._first_time = True

        if not self._snap:
            self._stage = time.time()
            return 0
        else:
            now = time.time()
            seconds_to_wait = self.interval - now % self.interval
            self._stage = now + seconds_to_wait
            return seconds_to_wait

    def check(self):
        """
        Checks within every loop if a new sequenz-pass has begun.
        
        Actualize all values according to the new pass, such as runtime, count
        and timelag.
        
        Returns:
            True:   if you are in a new (not yet checked) sequenz-pass.
            False:  otherwise
            None:   if timer has not started yet or were already stopped.
            
        """
        
        # if the timer is not running:
        if not self.alive: return

        # if interval is 0:
        elif not self.interval:
            self.actualize()
            if self.interval: time.sleep(self.start())
            else: return False

        # Because the timer was started outside the loop, the first check
        # must return True.
        elif self._first_time:
            self._count += 1
            self._first_time = False
            return True

        # actual sequenz hasn't finished yet:
        elif time.time() - self._stage < self._interval: return False

        else:
            lag = self.runtime - self._interval
            self._timelag = None if lag <= self._latency_tolerance else lag

            self.actualize()
            if not self.interval: return False

            self._count += 1
            self._stage += self.interval
            return True

    def run_check(self):
        """
        Checks if the timer is running and max_count has not reached.
        
        Returns a boolean.
        """
        if self._stopped: self.reset()
        return self.alive and not self.count is self._max_count

    def reset(self):
        """
        Reset all values.
        """
        self._count = 0
        self._stage = None
        self._stopped = False

    def stop(self):
        """
        Stop the timer/sequenz as soon as all left cmds has been processed.
        """
        self._stopped = True


class DaytimeTimer(Timer):
    """
    Extension of Timer.
    
    The constructor expects a sorted list of tuples with each tuple consisting of
    a daytime and an interval. From each daytime on the particular interval will
    be used.
    """
    def actualize(self):
        """Actualizes the interval based on the actual daytime.
        """
        now = DayTime.daytime()
        if now < self._data[-1][0]:
            self._interval = self._data[0][1]
        else:
            for daytime, interval in self._data:
                if daytime < now: self._interval = interval


class Sequence():
    """
    Runs several commands in a repeated sequenz.
    """
    def __init__(self, timer, cmds=list()):
        """
        Constructor of Sequenz.
        
        Args:
            timer:  a Timer-instance. All characteristics of a sequenz depends
                    on the timer (like the interval of a sequenz or the maximal
                    count of passing through it).
            
            cmds:   a list of Command-instances. The way Commands are executed
                    whithin a sequenz depends first on the order of the cmds-list
                    and second on the configuration of each cmd itself.
        """
        self.timer = timer
        self.cmds = cmds

    @property
    def alive(self):
        return self._alive

    def add_cmd(self, cmd):
        """
        Add a Command-instance.
        """
        self.cmds.append(cmd)

    def thread(self, daemon=False):
        """
        Start the main-loop in a thread.
        
        Args:
            daemon: boolean to specify whether the thread that runs the
                    main-loop should be a daemon or not (This makes a difference
                    in the way signals are handeld. A daemonized thread will be
                    interrupted instantly by a signal, also every cmd that is
                    actually processed.
                    A non-daemonized thread will not be interupted by any signal
                    except SIGKILL. You have to catch the signal your own and
                    to call the sequenz' stop-method. Then the thread will
                    finish after all left cmds in the actual pass will be
                    processed.
        """
        #FIXME: With a non-daemonized thread the signals won't be catched
        # anymore after a certain while.
        thread = Thread(target=self.go)
        thread.daemon = daemon
        thread.start()

    def stop(self, wait=False):
        """
        Will cause the sequenz to stop after finishing his actual pass.
        """
        self.timer.stop()
        if wait:
            while self.alive: time.sleep(0.01)

    def go(self):
        """
        Start the sequenz as a non-threaded loop.
        
        If this method is called in the main-thread, the loop will be
        interrupted but the execution of the last cmd will be finished.
        """
        time.sleep(self.timer.start())
        self._alive = True
        while self.timer.run_check():

            # start a new round
            if self.timer.check():

                # check for a timelag
                if self.timer.timelag:
                    LOGGER.error('TIMELAG: %s sec!' % round(self.timer.timelag, 2))

                LOGGER.info('ROUND {0} (INTERVAL {1})'.format(
                    self.timer.count, self.timer.interval
                    ))

                threads = list()
                 # loop over cmd-list
                for cmd in self.cmds:
                    if not cmd.daytime_check(self.timer.interval): continue
                    if not cmd.frequenz_check(): continue
                    time.sleep(cmd.runtime_delay(self.timer.runtime))
                    time.sleep(cmd.wait)
                    LOGGER.info('EXECUTE %s.', cmd.__call__.__name__)
                    thread = Thread(target=cmd, args=cmd.args, kwargs=cmd.kwargs)
                    thread.start()
                    if cmd.join: thread.join()
                    threads.append(thread)
                    time.sleep(cmd.stall)


            time.sleep(0.002)

        else:
            # check if any thread is still alive and wait for it:
            if locals().has_key("threads"):
                while filter(lambda t: t.is_alive(), threads): time.sleep(0.01)

            self.timer.reset()
            self._alive = False
            LOGGER.info('finished')


class Cmd():
    """
    Callable with configuration-attributes to be used in a sequenz.
    """
    def __init__(self, cmd=None, delay = 0, frequenz = 1, times=list(),
    join=False, wait=0, stall = 0, args=list(), kwargs=dict()):
        """
        Constructor of Command.
        
        Args:
            cmd:
                a callable that will be run within the sequenz
            delay:
                the earliest point of time in seconds that the cmd will be
                run within the sequenz
            frequenz:
                cmd will be run every x time of the calls that usually would be
                made for cmd. Default is 1 (cmd will be called every time).
            times:
                list of daytimes in the format %H:%M. If the list is not empty,
                cmd will be run only within the sequenz that comes first after
                the specified daytime.(Mind that if frequenz is greater than 1,
                the respective times the call to cmd will be left out. E.g. 
                there are two daytimes specified and frequenz is set to 2, than
                the cmd-call will take place only for the first daytime.
                Is there though only one daytime specified, the call would take
                place every second day.)
            join:
                If join is True, the thread that runs the cmd will be joined
                (means the main-thread will wait for execution). Defaults to
                False.
            wait:
                time in seconds the cmd-call will be put back when his moment
                has actually came.
            stall:
                time in seconds that the next possible execution of the cmd that
                comes next will be stalled after running the current cmd.
            args:
                list of positional arguments that will be passed to the cmd.
            kwargs:
                dictonary of keyword-arguments that will be passed to the cmd.
        """
        self.__call__ = cmd
        self.delay = delay
        self.frequenz = frequenz
        self.join = join
        self.wait = wait
        self.stall = stall
        self.times = times
        self.args = args
        self.kwargs = kwargs
        self._count = -1

    def daytime_check(self, interval):
        """
        Checks the cmd's times-attribute.
        
        Determines whether the cmd should be run next sequenz, and increase his
        count by one if so.
        
        Args:
            timer:  a Timer-instance
        
        Returns a boolean.
        """

        if not self.times:
            self._count += 1
            return True

        d = DayTime.daytime()
        i = interval
        if any([d >= t and d - t < i for t in self.times]):
            self._count +=1
            return True

        else: return False

    def frequenz_check(self):
        """
        Checks the cmd's frequenz-attribute.
        
        Determines whether a cmd should be run by means of his count and the
        specified frequenz for this cmd.
        Note that this check should be run after the daytime-check. Think about
        these two checks like this. daytime_check determines when a cmd would be
        "normally" called, while the frequenz_check determines which times of
        the "normally" calls to the cmd, the cmd should be actually called.
        
        Returns a boolean.
        """
        return self._count % self.frequenz == 0

    def runtime_delay(self, runtime):
        """
        Returns the time that the cmd still has to wait depending on his delay.
        
        Args:
            timer:  a Timer-instance
        """
        delay = self.delay - runtime
        return delay if delay >= 0 else 0


