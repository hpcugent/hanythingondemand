#!/usr/bin/python

## from http://fleckenzwerg2000.blogspot.com/2011/10/running-and-controlling-gnu-screen-from.html
## script examples from http://aperiodic.net/screen/quick_reference

import pty
import os
import time
import subprocess

# prepare cmd that will start gdb in a screen session
# Note: it's actually two nested screen sessions - see text for explanation
cmdString = "screen -dmS dummyxc screen -S xc gdb -ex \"r\" xclock"

screenname = 'clientHOD'
cmd = '/bin/bash'
cmdString = "screen -dmS dummyxc screen -S %s %s" % (screenname, cmd)
cmdString = "screen -dmS dummyxc screen -S %s" % (screenname)
cmdString = "screen -dmS %s" % (screenname)

# allocate new pseudo-terminal and spawn screen sessions
(master, slave) = pty.openpty()
p = subprocess.Popen(cmdString, close_fds=True, shell=True, stdin=slave, stdout=slave, stderr=slave)

print "Screen session '%s' started (attached). You can use 'screen -x %s' now" % (screenname, screenname)

# send commands to the screen session to interrupt xclock
# prefix the screen commands
screenCmds = ["export TESTVARIABLE=test",
              "./script_with_output.sh",
              "/bin/echo DONE1",
              "/bin/echo $TESTVARIABLE",
              "echo DONE",
             ]
sl = 5
print "sleeping %d seconds" % sl
time.sleep(sl)
for cmd in screenCmds :
    completeCmd = "screen -S %s -X stuff $'%s\r'" % (screenname, cmd)


    print "Calling %s." % cmd
    subprocess.call(completeCmd, shell=True)
    print "Called %s. Sleeping 1s" % cmd
    time.sleep(1) # uncomment this to see the magic unfold

