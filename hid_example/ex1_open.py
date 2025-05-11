"""
duckyPad HID example: HID write

For more details, see:

https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md

"""

import hid

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64

h = hid.device()

duckypad_pid = 0xd11c
duckypad_pro_pid = 0xd11d

def get_path_by_pid(my_pid):
    path_dict = {}
    for device_dict in hid.enumerate():
        if device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] == my_pid:
            path_dict[device_dict['usage']] = device_dict['path']
    if len(path_dict) == 0:
        return None
    if 58 in path_dict:
        return path_dict[58]
    return list(path_dict.values())[0]

def get_duckypad_path():
    dpp_path = get_path_by_pid(duckypad_pro_pid)
    if dpp_path is not None:
        return dpp_path
    dp_path = get_path_by_pid(duckypad_pid)
    if dp_path is not None:
        return dp_path
    return None

pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
pc_to_duckypad_buf[1] = 0   # Sequence Number
pc_to_duckypad_buf[2] = 3   # Command type

# print("----\nsudo is needed on Linux!\n----")

duckypad_path = get_duckypad_path()

if duckypad_path is None:
    print("duckyPad not found!")
    exit()
h.open_path(duckypad_path)
print("\n\nSending to duckyPad:\n", pc_to_duckypad_buf)
h.write(pc_to_duckypad_buf)
h.close()
print('done!')
