"""
duckyPad HID example: List HID devices

https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md
"""

import hid

for device_dict in hid.enumerate():
    keys = list(device_dict.keys())
    keys.sort()
    print("---------")
    for key in keys:
        print(f"{key} : {device_dict[key]}")
    print()