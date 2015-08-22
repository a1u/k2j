__author__ = 'au'
import argparse
from math import *
from evdev import *
from evdev import ecodes as e, util, device
from threading import Thread
from time import sleep
from collections import defaultdict
import pygame

REPEAT_INTERVAL = 0.0007

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("input", help="Input keyboard device. E.g. /dev/input/eventX", type=str)
try:
    parser.parse_args()
except:
    devices = [InputDevice(fn) for fn in list_devices()]
    for dev in devices:
        print(dev.fn, dev.name, dev.phys, dev.info)
    exit()

args = parser.parse_args()

if args.verbose:
    print("Verbosity turned on")

kbd = InputDevice(args.input)
print("Input:", kbd)

capability = {
    e.EV_KEY: [304, 305, 307, 308, 310, 311, 314, 315, 316, 317, 318],
    e.EV_ABS: [
        (e.ABS_X, (-32768, 32767, 16, 0)),
        (e.ABS_Y, (-32768, 32767, 16, 0)),
        (e.ABS_Z, (-32768, 32767, 16, 0)),
        (e.ABS_RX, (-32768, 32767, 16, 0)),
        (e.ABS_RY, (-32768, 32767, 16, 0)),
        (e.ABS_RZ, (-32768, 32767, 16, 0)),
        (e.ABS_HAT0X, (-32768, 32767, 16, 0)),
        (e.ABS_HAT0X, (-32768, 32767, 16, 0)),
        (e.ABS_HAT0Y, (-32768, 32767, 16, 0)),
        (e.ABS_HAT0Y, (-32768, 32767, 16, 0))
    ]
}

initial = {}
for k in capability.keys():
    for v in capability[k]:
        initial.update({str(k) + ":" + str(v if type(v) is not tuple else v[0]): v if type(v) is not tuple else v[1]})

ui = UInput(capability, name="Virtual Xbox360", vendor=1118, product=654, version=272, bustype=3)

print("Output:", ui.device)

def c(a, side, limit):
    return a + limit * side

ev = {}
def default():
    for k, v in initial.items():
        ev.update({k: 0 if type(v) is not tuple else ceil(v[1] - (abs(v[0]) + abs(v[1]))/2)})

default()
a = {}

class MyThread(Thread):
    _terminate = False
    def stop(self):
        self._terminate = True
    def run(self):
        while True and not self._terminate:
            for k in a.keys():
                # if a[k] is not 0 :
                evi = int(k.split(":")[0])
                evt = int(k.split(":")[1])
                if (evi is e.EV_ABS):
                    if (a[k] is not 0):
                        c1 = c(ev.get(k, 0), a[k], 1 + initial.get(k)[2])
                        ev.update({k: initial.get(k)[0] if c1 < initial.get(k)[0] else initial.get(k)[1] if c1 > initial.get(k)[1] else c1})
                else:
                    ev.update({k: a[k]})

                ui.write(evi, evt, ev[k])
                ui.syn()

            print(ev) if args.verbose else 1
            sleep(REPEAT_INTERVAL)

thread = MyThread()
thread.start()

p = {}
r = {}
s = {}

def map(dt, dc, pc, sc, v):
    a.update({str(dt) + ':' + str(dc): v}) if pc == sc else 1

try:
    for event in kbd.read_loop():
        if event.type == e.EV_KEY:
            p.update({event.code: event.value}) if event.value != 0 else p.pop(event.code, 0)
            r.update({event.code: event.value}) if event.value == 0 else 1
            # if (e.KEY_LEFTCTRL in p and e.KEY_Q in p and len(p) == 2): kbd.grab()
            # if (e.KEY_LEFTCTRL in p and e.KEY_W in p and len(p) == 2): kbd.ungrab()
            (default()) if event.code == e.KEY_DELETE else 1
            map(e.EV_ABS, e.ABS_X, e.KEY_LEFT, event.code, -event.value)
            map(e.EV_ABS, e.ABS_X, e.KEY_RIGHT, event.code, event.value)
            map(e.EV_ABS, e.ABS_Y, e.KEY_DOWN, event.code, -event.value)
            map(e.EV_ABS, e.ABS_Y, e.KEY_UP, event.code, event.value)
            map(e.EV_ABS, e.ABS_Z, e.KEY_A, event.code, -event.value)
            map(e.EV_ABS, e.ABS_Z, e.KEY_D, event.code, event.value)
            map(e.EV_ABS, e.ABS_RX, e.KEY_S, event.code, -event.value)
            map(e.EV_ABS, e.ABS_RX, e.KEY_W, event.code, event.value)
            map(e.EV_ABS, e.ABS_RY, e.KEY_Z, event.code, -event.value)
            map(e.EV_ABS, e.ABS_RY, e.KEY_Q, event.code, event.value)
            map(e.EV_ABS, e.ABS_RZ, e.KEY_C, event.code, -event.value)
            map(e.EV_ABS, e.ABS_RZ, e.KEY_E, event.code, event.value)
            map(e.EV_ABS, e.ABS_HAT0X, e.KEY_HOME, event.code, -event.value)
            map(e.EV_ABS, e.ABS_HAT0X, e.KEY_END, event.code, event.value)
            map(e.EV_ABS, e.ABS_HAT0Y, e.KEY_PAGEDOWN, event.code, -event.value)
            map(e.EV_ABS, e.ABS_HAT0Y, e.KEY_PAGEUP, event.code, event.value)
            # if event.code == e.KEY_1:
            #     a.update({str(e.ABS_THROTTLE): event.value})
            # if event.code == e.KEY_2:
            #     a.update({str(e.ABS_THROTTLE): -event.value})
            map(e.EV_KEY, 304, e.KEY_1, event.code, event.value)
            map(e.EV_KEY, 305, e.KEY_2, event.code, event.value)
            map(e.EV_KEY, 307, e.KEY_3, event.code, event.value)
            map(e.EV_KEY, 308, e.KEY_4, event.code, event.value)
            map(e.EV_KEY, 310, e.KEY_5, event.code, event.value)
            map(e.EV_KEY, 311, e.KEY_6, event.code, event.value)
            map(e.EV_KEY, 314, e.KEY_7, event.code, event.value)
            map(e.EV_KEY, 315, e.KEY_8, event.code, event.value)
            map(e.EV_KEY, 316, e.KEY_9, event.code, event.value)
            map(e.EV_KEY, 317, e.KEY_0, event.code, event.value)
            map(e.EV_KEY, 318, e.KEY_GRAVE, event.code, event.value)
except KeyboardInterrupt:
    pass
finally:
    thread.stop()
    ui.close()


# (e.ABS_X, (-32768, 32767, 16, 128)),
# (e.ABS_Y, (-32768, 32767, 16, 128)),
# (e.ABS_Z, (0, 255, 0, 0)),
# (e.ABS_RX, (-32768, 32767, 16, 128)),
# (e.ABS_RY, (-32768, 32767, 16, 128)),
# (e.ABS_RZ, (0, 255, 0, 0)),
# (e.ABS_HAT0X, (-1, 1, 0, 0)),
# (e.ABS_HAT0X, (-1, 1, 0, 0)),
# (e.ABS_HAT0Y, (-1, 1, 0, 0)),
# (e.ABS_HAT0Y, (-1, 1, 0, 0))
