__author__ = 'au'
import argparse
from math import *
from evdev import *
from evdev import ecodes as e, util, device
from threading import Thread
from time import sleep
from collections import defaultdict
import pygame

REPEAT_INTERVAL = 0.00007

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

S_DEC = 0
S_INC = 1
S_FIXED = 2
S_PRESS = 3
S_DEFAULT = 4

mapping = {
    ((e.EV_KEY, e.KEY_LEFTCTRL),(e.EV_KEY, e.KEY_Q)): {(): [S_DEFAULT]},
    ((e.EV_KEY, e.KEY_LEFT),): {(e.EV_ABS, e.ABS_X): [S_DEC]},
    ((e.EV_KEY, e.KEY_RIGHT),): {(e.EV_ABS, e.ABS_X): [S_INC]},
    ((e.EV_KEY, e.KEY_DOWN),): {(e.EV_ABS, e.ABS_Y): [S_DEC]},
    ((e.EV_KEY, e.KEY_UP),): {(e.EV_ABS, e.ABS_Y): [S_INC]},
    ((e.EV_KEY, e.KEY_A),): {(e.EV_ABS, e.ABS_Z): [S_DEC]},
    ((e.EV_KEY, e.KEY_D),): {(e.EV_ABS, e.ABS_Z): [S_INC]},
    ((e.EV_KEY, e.KEY_S),): {(e.EV_ABS, e.ABS_RX): [S_DEC, S_FIXED]},
    ((e.EV_KEY, e.KEY_W),): {(e.EV_ABS, e.ABS_RX): [S_INC, S_FIXED]},
    ((e.EV_KEY, e.KEY_Z),): {(e.EV_ABS, e.ABS_RY): [S_DEC]},
    ((e.EV_KEY, e.KEY_Q),): {(e.EV_ABS, e.ABS_RY): [S_INC]},
    ((e.EV_KEY, e.KEY_C),): {(e.EV_ABS, e.ABS_RZ): [S_DEC]},
    ((e.EV_KEY, e.KEY_E),): {(e.EV_ABS, e.ABS_RZ): [S_INC]},
    ((e.EV_KEY, e.KEY_HOME),): {(e.EV_ABS, e.ABS_HAT0X): [S_DEC]},
    ((e.EV_KEY, e.KEY_END),): {(e.EV_ABS, e.ABS_HAT0X): [S_INC]},
    ((e.EV_KEY, e.KEY_PAGEDOWN),): {(e.EV_ABS, e.ABS_HAT0Y): [S_DEC]},
    ((e.EV_KEY, e.KEY_PAGEUP),): {(e.EV_ABS, e.ABS_HAT0Y): [S_INC]},
    ((e.EV_KEY, e.KEY_1),): {(e.EV_KEY, e.BTN_A): [S_PRESS]},
    ((e.EV_KEY, e.KEY_2),): {(e.EV_KEY, e.BTN_B): [S_PRESS]},
    ((e.EV_KEY, e.KEY_3),): {(e.EV_KEY, e.BTN_NORTH): [S_PRESS]},
    ((e.EV_KEY, e.KEY_4),): {(e.EV_KEY, e.BTN_WEST): [S_PRESS]},
    ((e.EV_KEY, e.KEY_5),): {(e.EV_KEY, e.BTN_TL): [S_PRESS]},
    ((e.EV_KEY, e.KEY_6),): {(e.EV_KEY, e.BTN_TR): [S_PRESS]},
    ((e.EV_KEY, e.KEY_7),): {(e.EV_KEY, e.BTN_SELECT): [S_PRESS]},
    ((e.EV_KEY, e.KEY_8),): {(e.EV_KEY, e.BTN_START): [S_PRESS]},
    ((e.EV_KEY, e.KEY_9),): {(e.EV_KEY, e.BTN_MODE): [S_PRESS]},
    ((e.EV_KEY, e.KEY_0),): {(e.EV_KEY, e.BTN_THUMBL): [S_PRESS]},
    ((e.EV_KEY, e.KEY_GRAVE),): {(e.EV_KEY, e.BTN_THUMBR): [S_PRESS]},
}

pressed = []

ranges = {}
for k in capability.keys():
    for v in capability[k]:
        ranges.update({(k, (v if type(v) is not tuple else v[0])): (0, 1) if type(v) is not tuple else (v[1][0], v[1][1])})
initial = {}
for k in capability.keys():
    for v in capability[k]:
        initial.update({(k, (v if type(v) is not tuple else v[0])): 0 if type(v) is not tuple else ceil(v[1][1] - (abs(v[1][0]) + abs(v[1][1]))/2)})
accelInitial = {}
for k in capability.keys():
    for v in capability[k]:
        accelInitial.update({(k, (v if type(v) is not tuple else v[0])): 0})
accel = accelInitial.copy()

current = initial.copy()

fixed = {}

ui = UInput(capability, name="Virtual Xbox360", vendor=1118, product=654, version=272, bustype=3)

print("Output:", ui.device)

class EventLoop(Thread):
    _terminate = False
    def stop(self):
        self._terminate = True
    def run(self):
        while True and not self._terminate:
            for k,v in current.items():
                ui.write(k[0], k[1], int(v))
                ui.syn()
            operates = []
            operates.append(mapping.get(tuple(pressed)))
            for i in pressed:
                operates.append(mapping.get(tuple([tuple(i)])))
            for operate in operates:
                if (operate is not None):
                    for k,v in operate.items():
                        if S_DEFAULT in v:
                            current.update(initial)
                            break
                        if S_FIXED in v: fixed.update({k: 1})
                        strategy = (-1 if S_DEC in v else 1 if S_INC in v else 0)
                        if (S_PRESS in v):
                            z = 1
                        else:
                            accel.update({k: (accel.get(k) + 0.01)})
                            z = strategy * accel.get(k) + current.get(k)
                        z = ranges.get(k)[0] if z <= ranges.get(k)[0] else ranges.get(k)[1] if z >= ranges.get(k)[1] else z
                        current.update({k: z})

            zz = []
            for operate in operates:
                if (operate is None): continue
                zz.extend(operate.keys())

            for k,v in current.items():
                if (k in zz): continue
                if (fixed.get(k, 0) == 1): continue
                current.update({k: initial.get(k)})

            print(current) if args.verbose else 1
            sleep(REPEAT_INTERVAL)

thread = EventLoop()
thread.start()

try:
    for event in kbd.read_loop():
        if (event.type not in [e.EV_KEY]): continue

        t = (event.type, event.code)
        if event.value != 0:
            pressed.append(t) if t not in pressed else 0
        else:
            accel = accelInitial.copy()
            pressed.remove(t) if t in pressed else 0

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
