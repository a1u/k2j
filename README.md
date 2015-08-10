There are too many programs to map joystick to keyboard and nothing to map keyboard to joystick.
This small program creates virtual joystick/gamepad (device: Microsoft xbox 360) and map keyboard keys to joystick events.
Excellently works in Ubuntu. You can change mapping modifying program code.

Usage
-----------

```bash
    sudo python3 main.py /dev/input/event4
```bash

this will create new virtual device:
Input: device /dev/input/event4, name "AT Translated Set 2 keyboard", phys "isa0060/serio0/input0"
Output: device /dev/input/event15, name "Virtual Xbox360", phys ""

    sudo evtest /dev/input/event15
    Input driver version is 1.0.1
    Input device ID: bus 0x3 vendor 0x45e product 0x28e version 0x110
    Input device name: "Virtual Xbox360"

    You can also create virtual empty device by using prop file to compare with that that created by program:
    sudo evemu-device xbox360.prop