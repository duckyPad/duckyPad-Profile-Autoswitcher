"""
duckyPad HID example: HID read AND write

https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md
"""

import hid
import time
from datetime import datetime, timezone

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

h = hid.device()

duckypad_pid = 0xd11c
duckypad_pro_pid = 0xd11d
DUCKYPAD_VID = 0x0483
DUCKYPAD_COUNTED_BUF_USAGE_ID = 58

def get_path_by_pid(my_pid):
    path_dict = {}
    for device_dict in hid.enumerate():
        if device_dict['vendor_id'] != DUCKYPAD_VID:
            continue
        if device_dict['product_id'] != my_pid:
            continue
        if device_dict['usage'] != DUCKYPAD_COUNTED_BUF_USAGE_ID:
            continue
        return device_dict['path']
    return None

def get_duckypad_path():
    dpp_path = get_path_by_pid(duckypad_pro_pid)
    if dpp_path is not None:
        return dpp_path
    dp_path = get_path_by_pid(duckypad_pid)
    if dp_path is not None:
        return dp_path
    return None

def duckypad_hid_write(hid_buf_64b):
	if len(hid_buf_64b) != PC_TO_DUCKYPAD_HID_BUF_SIZE:
		raise ValueError('PC-to-duckyPad buffer wrong size, should be exactly 64 Bytes')
	duckypad_path = get_duckypad_path()
	if duckypad_path is None:
		raise OSError('duckyPad Not Found!')
	h.open_path(duckypad_path)
	h.write(hid_buf_64b)
	result = h.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
	h.close()
	return result

def get_timestamp_and_utc_offset():
    now = datetime.now().astimezone()  # Local time with timezone info
    unix_timestamp = int(now.timestamp())
    utc_offset_minutes = int(now.utcoffset().total_seconds() // 60)
    return unix_timestamp, utc_offset_minutes

def u32_to_u8_list_be(value):
    return [
        (value >> 24) & 0xFF,
        (value >> 16) & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF]

def i16_to_u8_list_be(value):
    value &= 0xFFFF
    return [
        (value >> 8) & 0xFF,
        value & 0xFF ]


unix_ts, utc_offset_minutes = get_timestamp_and_utc_offset()

unix_ts_u8_list = u32_to_u8_list_be(unix_ts)
utc_offset_u8_list = i16_to_u8_list_be(utc_offset_minutes)

pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
pc_to_duckypad_buf[0] = 5   # HID Usage ID, always 5
pc_to_duckypad_buf[1] = 0   # Reserved
pc_to_duckypad_buf[2] = 0x1A    # Command: Set RTC

pc_to_duckypad_buf[3] = unix_ts_u8_list[0]
pc_to_duckypad_buf[4] = unix_ts_u8_list[1]
pc_to_duckypad_buf[5] = unix_ts_u8_list[2]
pc_to_duckypad_buf[6] = unix_ts_u8_list[3]

pc_to_duckypad_buf[7] = utc_offset_u8_list[0]
pc_to_duckypad_buf[8] = utc_offset_u8_list[1]

print(f"\n\n--------\nUNIX Timestamp: {unix_ts}\nUTC Offset (Minutes): {utc_offset_minutes}\n-----------\n")

print("Sending to duckyPad:\n", pc_to_duckypad_buf)
duckypad_to_pc_buf = duckypad_hid_write(pc_to_duckypad_buf)
print("\nduckyPad response:\n", duckypad_to_pc_buf)