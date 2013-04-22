sequence
=========

A Python module for looping over a sequence of commands with a focus on high configurability and extensibility.



Latest Version
--------------
The latest version of this project can be found at : http://github.com/thomst/sequence.


Installation
------------
* Option 1 : Install via pip ::

    pip install sequence

* Option 2 : If you have downloaded the source ::

    python setup.py install


Documentation
-------------
How to use? ::

    from sequence import Timer
    from sequence import Sequence
    from sequence import Cmd

    interval = 8
    timer = Timer(interval)

    def f(x): print x
    cmd1 = Cmd(f, args=['cmd1'], stall=3)   #stall the execution of cmd2 for 3 sec
    cmd2 = Cmd(f, args=['cmd2'])            #just right now (depending on the order)
    cmd3 = Cmd(f, args=['cmd3'], delay=4)   #soonest after 4 sec from loop-start
                                            #other options are available...

    sequence = Sequence(timer, [cmd1, cmd2, cmd3])
    sequence.go()




Reporting Bugs
--------------
Please report bugs at github issue tracker:
https://github.com/thomst/sequence/issues


Author
------
thomst <thomaslfuss@gmx.de>
Thomas Leichtfuß

* http://github.com/thomst
