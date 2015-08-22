__author__ = 'au'
import argparse
from collections import Counter
from math import *
from functools import partial
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
# parser.add_argument("outdev", help="Output joystick device. E.g. /dev/input/eventY", type=str)
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
# jst = InputDevice("/dev/input/event14")
# print(jst.capabilities(verbose=True))

# print(util.resolve_ecodes(e.EV_ABS))


# exit()
print("Input:", kbd)
# print("Output:", jst)

# print(jst.capabilities(verbose=True))
#
# for event in kbd.read_loop():
#      if event.type == e.EV_KEY:
#          print(categorize(event))

# cap = {}
#
# print(util.resolve_e(e.EV_ABS))
#

# print(jst.capabilities(verbose=True))
# cap = {}
# for key in jst.capabilities():
#     cap.update({key): [((x[0], (x[1].min, x[1].max, x[1].fuzz, x[1].flat)) if type(x) is tuple else x) for x in jst.capabilities().get(key)]})

# print(e.bytype[e.EV_ABS])
# exit()
#
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

cap = {
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
    ]}
capm = {}
for k in cap.keys():
    for v in cap[k]:
        capm.update({str(k) + ":" + str(v if type(v) is not tuple else v[0]) : v if type(v) is not tuple else v[1]})

# print(capm)
# exit()

ui = UInput(cap, name="Virtual Xbox360", vendor=1118, product=654, version=272, bustype=3)

print("Output:", ui.device)
# time.sleep(4)
# ui.write(e.EV_ABS, e.ABS_X, 5000)
# ui.syn()
# ui.write(e.EV_ABS, e.ABS_X, 5000)
# ui.syn()
# ui.write(e.EV_ABS, e.ABS_X, 100)
# ui.syn()
# ui.write(e.EV_KEY, e.KEY_A, 1)
# ui.write(e.EV_KEY, e.KEY_A, 0)
# # ui.write(e.ABS_X, e.ABS_BRAKE, 0)

def c(a, side, limit):
    return a + limit * side

ev = {}
def default():
    for k, v in capm.items():
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
                        c1 = c(ev.get(k, 0), a[k], 1 + capm.get(k)[2])
                        ev.update({k: capm.get(k)[0] if c1 < capm.get(k)[0] else capm.get(k)[1] if c1 > capm.get(k)[1] else c1})
                else:
                    ev.update({k: a[k]})
                    # ui.write(evi, evt, 0)
                    # ui.syn()
                ui.write(evi, evt, ev[k])
                ui.syn()

            print(ev) if args.verbose else 1
            sleep(REPEAT_INTERVAL)

thread = MyThread()
thread.start()
# thread.join()

# pygame.joystick.init()
# j = pygame.joystick.Joystick(0) # create a joystick instance
# j.init() # init instance
# print ('Enabled joystick: ', j.get_name())
# quit()

try:
    for event in kbd.read_loop():
        if event.type == e.EV_KEY:
            (default()) if event.code == e.KEY_DELETE else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_X): -event.value}) if event.code == e.KEY_LEFT else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_X): event.value}) if event.code == e.KEY_RIGHT else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_Y): -event.value}) if event.code == e.KEY_DOWN else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_Y): event.value}) if event.code == e.KEY_UP else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_Z): -event.value}) if event.code == e.KEY_A else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_Z): event.value}) if event.code == e.KEY_D else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RX): -event.value}) if event.code == e.KEY_S else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RX): event.value}) if event.code == e.KEY_W else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RY): -event.value}) if event.code == e.KEY_Z else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RY): event.value}) if event.code == e.KEY_Q else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RZ): -event.value}) if event.code == e.KEY_C else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_RZ): event.value}) if event.code == e.KEY_E else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_HAT0X): -event.value}) if event.code == e.KEY_HOME else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_HAT0X): event.value}) if event.code == e.KEY_END else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_HAT0Y): -event.value}) if event.code == e.KEY_PAGEDOWN else 1
            a.update({str(e.EV_ABS) + ':' + str(e.ABS_HAT0Y): event.value}) if event.code == e.KEY_PAGEUP else 1
            # if event.code == e.KEY_1:
            #     a.update({str(e.ABS_THROTTLE): event.value})
            # if event.code == e.KEY_2:
            #     a.update({str(e.ABS_THROTTLE): -event.value})
            a.update({str(e.EV_KEY) + ':' + str(304): event.value}) if event.code == e.KEY_1 else 1
            a.update({str(e.EV_KEY) + ':' + str(305): event.value}) if event.code == e.KEY_2 else 1
            a.update({str(e.EV_KEY) + ':' + str(307): event.value}) if event.code == e.KEY_3 else 1
            a.update({str(e.EV_KEY) + ':' + str(308): event.value}) if event.code == e.KEY_4 else 1
            a.update({str(e.EV_KEY) + ':' + str(310): event.value}) if event.code == e.KEY_5 else 1
            a.update({str(e.EV_KEY) + ':' + str(311): event.value}) if event.code == e.KEY_6 else 1
            a.update({str(e.EV_KEY) + ':' + str(314): event.value}) if event.code == e.KEY_7 else 1
            a.update({str(e.EV_KEY) + ':' + str(315): event.value}) if event.code == e.KEY_8 else 1
            a.update({str(e.EV_KEY) + ':' + str(316): event.value}) if event.code == e.KEY_9 else 1
            a.update({str(e.EV_KEY) + ':' + str(317): event.value}) if event.code == e.KEY_0 else 1
            a.update({str(e.EV_KEY) + ':' + str(318): event.value}) if event.code == e.KEY_GRAVE else 1
except KeyboardInterrupt:
    pass
finally:
    thread.stop()
    ui.close()
