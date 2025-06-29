import hid

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

this_dp = hid.device()

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

HID_COMMAND_DUMP_SD = 32

pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
pc_to_duckypad_buf[0] = 5	# HID Usage ID, always 5
pc_to_duckypad_buf[1] = 0	# Sequence Number
pc_to_duckypad_buf[2] = HID_COMMAND_DUMP_SD	# Command type

duckypad_path = get_duckypad_path()
if duckypad_path is None:
    print('duckyPad Not Found!')
    exit()

this_dp.open_path(duckypad_path)

try:
    while 1:
        print("\n\nSending to duckyPad:\n", pc_to_duckypad_buf)
        this_dp.write(pc_to_duckypad_buf)
        duckypad_to_pc_buf = this_dp.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        
        print(f"\nduckyPad response:\n{len(duckypad_to_pc_buf)}B {duckypad_to_pc_buf}")
        print("--------")
        if(len(duckypad_to_pc_buf) > 5 and duckypad_to_pc_buf[1] == 4):
            break
except KeyboardInterrupt:
    this_dp.close()

this_dp.close()

