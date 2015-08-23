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
    e.EV_KEY: [
        e.BTN_A,
        e.BTN_B,
        e.BTN_NORTH,
        e.BTN_WEST,
        e.BTN_TL,
        e.BTN_TR,
        e.BTN_SELECT,
        e.BTN_START,
        e.BTN_MODE,
        e.BTN_THUMBL,
        e.BTN_THUMBR
    ],
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

def correct(a, side, limit):
    return a + limit * side

ev = {}
def default():
    for k, v in initial.items():
        ev.update({k: 0 if type(v) is not tuple else ceil(v[1] - (abs(v[0]) + abs(v[1]))/2)})

default()
a = {}

class EventLoop(Thread):
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
                        c1 = correct(ev.get(k, 0), a[k], 1 + initial.get(k)[2])
                        ev.update({k: initial.get(k)[0] if c1 < initial.get(k)[0] else initial.get(k)[1] if c1 > initial.get(k)[1] else c1})
                else:
                    ev.update({k: a[k]})

                ui.write(evi, evt, ev[k])
                ui.syn()

            print(ev) if args.verbose else 1
            sleep(REPEAT_INTERVAL)

thread = EventLoop()
thread.start()

pressed = {}
released = {}
s = {}

def map(sourceCode, expectedCode, destType, destCode, value):
    a.update({str(destType) + ':' + str(destCode): value}) if expectedCode == sourceCode else 1

try:
    for event in kbd.read_loop():
        if event.type == e.EV_KEY:
            pressed.update({event.code: event.value}) if event.value != 0 else pressed.pop(event.code, 0)
            released.update({event.code: event.value}) if event.value == 0 else 1
            # if (e.KEY_LEFTCTRL in p and e.KEY_Q in p and len(p) == 2): kbd.grab()
            # if (e.KEY_LEFTCTRL in p and e.KEY_W in p and len(p) == 2): kbd.ungrab()
            (default()) if event.code == e.KEY_DELETE else 1
            map(event.code, e.KEY_LEFT, e.EV_ABS, e.ABS_X, -event.value)
            map(event.code, e.KEY_RIGHT, e.EV_ABS, e.ABS_X, event.value)
            map(event.code, e.KEY_DOWN, e.EV_ABS, e.ABS_Y, -event.value)
            map(event.code, e.KEY_UP, e.EV_ABS, e.ABS_Y, event.value)
            map(event.code, e.KEY_A, e.EV_ABS, e.ABS_Z, -event.value)
            map(event.code, e.KEY_D, e.EV_ABS, e.ABS_Z, event.value)
            map(event.code, e.KEY_S, e.EV_ABS, e.ABS_RX, -event.value)
            map(event.code, e.KEY_W, e.EV_ABS, e.ABS_RX, event.value)
            map(event.code, e.KEY_Z, e.EV_ABS, e.ABS_RY, -event.value)
            map(event.code, e.KEY_Q, e.EV_ABS, e.ABS_RY, event.value)
            map(event.code, e.KEY_C, e.EV_ABS, e.ABS_RZ, -event.value)
            map(event.code, e.KEY_E, e.EV_ABS, e.ABS_RZ, event.value)
            map(event.code, e.KEY_HOME, e.EV_ABS, e.ABS_HAT0X, -event.value)
            map(event.code, e.KEY_END, e.EV_ABS, e.ABS_HAT0X, event.value)
            map(event.code, e.KEY_PAGEDOWN, e.EV_ABS, e.ABS_HAT0Y, -event.value)
            map(event.code, e.KEY_PAGEUP, e.EV_ABS, e.ABS_HAT0Y, event.value)
            map(event.code, e.KEY_1, e.EV_KEY, e.BTN_A, event.value)
            map(event.code, e.KEY_2, e.EV_KEY, e.BTN_B, event.value)
            map(event.code, e.KEY_3, e.EV_KEY, e.BTN_NORTH, event.value)
            map(event.code, e.KEY_4, e.EV_KEY, e.BTN_WEST, event.value)
            map(event.code, e.KEY_5, e.EV_KEY, e.BTN_TL, event.value)
            map(event.code, e.KEY_6, e.EV_KEY, e.BTN_TR, event.value)
            map(event.code, e.KEY_7, e.EV_KEY, e.BTN_SELECT, event.value)
            map(event.code, e.KEY_8, e.EV_KEY, e.BTN_START, event.value)
            map(event.code, e.KEY_9, e.EV_KEY, e.BTN_MODE, event.value)
            map(event.code, e.KEY_0, e.EV_KEY, e.BTN_THUMBL, event.value)
            map(event.code, e.KEY_GRAVE, e.EV_KEY, e.BTN_THUMBR, event.value)
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
