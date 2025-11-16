import hid
import sys
from datetime import datetime
import threading

hid_txrx_lock = threading.Lock()

dp20_pid = 0xd11c
dpp_pid = 0xd11d
all_dp_pids = [dp20_pid, dpp_pid]

def is_duckypad_pid(this_pid):
    return this_pid in all_dp_pids

def get_duckypad_path():
    dp_path_list = set()
    if 'win32' in sys.platform:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']) and \
            device_dict['usage'] == 58:
                dp_path_list.add(device_dict['path'])
    else:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == 0x0483 and \
            is_duckypad_pid(device_dict['product_id']):
                dp_path_list.add(device_dict['path'])
    return list(dp_path_list)

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

HID_RESPONSE_OK = 0
HID_RESPONSE_ERROR = 1
HID_RESPONSE_BUSY = 2
HID_RESPONSE_EOF = 3

def make_dp_info_dict(hid_msg, hid_path):
    this_dict = {}
    this_dict['fw_version'] = f"{hid_msg[3]}.{hid_msg[4]}.{hid_msg[5]}"
    this_dict['dp_model'] = hid_msg[6]
    serial_number_uint32_t = int.from_bytes(hid_msg[7:11], byteorder='big')
    this_dict['serial'] = f'{serial_number_uint32_t:08X}'.upper()
    this_dict['hid_path'] = hid_path
    this_dict['hid_msg'] = hid_msg
    return this_dict

def get_all_dp_info(dp_path_list):
    dp_info_list = []
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    for this_path in dp_path_list:
        # print(this_path)
        myh = hid.device()
        myh.open_path(this_path)
        myh.write(pc_to_duckypad_buf)
        result = myh.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        myh.close()
        # print(result)
        if result[2] != HID_RESPONSE_OK:
            continue
        this_dict = make_dp_info_dict(result, this_path)
        dp_info_list.append(this_dict)
    return dp_info_list

def scan_duckypads():
    all_dp_paths = get_duckypad_path()
    if len(all_dp_paths) == 0:
        return []
    try:
        dp_info_list = get_all_dp_info(all_dp_paths)
    except Exception:
        return None
    return dp_info_list

def get_empty_pc_to_duckypad_buf():
    ptd_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    ptd_buf[0] = 5   # HID Usage ID
    return ptd_buf

def hid_txrx_nolock(buf_64b, hid_obj):
    print("\n\nSending to duckyPad:\n", buf_64b)
    hid_obj.write(buf_64b)
    duckypad_to_pc_buf = hid_obj.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=500)
    print("\nduckyPad response:\n", duckypad_to_pc_buf)
    return duckypad_to_pc_buf

def hid_txrx(buf_64b, hid_obj):
    if not hid_txrx_lock.acquire(timeout=2):
        return None
    try:
        return hid_txrx_nolock(buf_64b, hid_obj)
    finally:
        hid_txrx_lock.release()

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

def duckypad_sync_rtc(hid_obj):
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    unix_ts, utc_offset_minutes = get_timestamp_and_utc_offset()
    unix_ts_u8_list = u32_to_u8_list_be(unix_ts)
    utc_offset_u8_list = i16_to_u8_list_be(utc_offset_minutes)
    pc_to_duckypad_buf[2] = 0x1A    # Command: Set RTC
    pc_to_duckypad_buf[3] = unix_ts_u8_list[0]
    pc_to_duckypad_buf[4] = unix_ts_u8_list[1]
    pc_to_duckypad_buf[5] = unix_ts_u8_list[2]
    pc_to_duckypad_buf[6] = unix_ts_u8_list[3]
    pc_to_duckypad_buf[7] = utc_offset_u8_list[0]
    pc_to_duckypad_buf[8] = utc_offset_u8_list[1]
    print(pc_to_duckypad_buf)
    result = hid_txrx(pc_to_duckypad_buf, hid_obj)
    print("duckypad_sync_rtc:", result)

DP_MODEL_OG_DUCKYPAD = 20
DP_MODEL_DUCKYPAD_PRO = 24

class dp_type:
    def __init__(self):
        self.dp20 = DP_MODEL_OG_DUCKYPAD
        self.dp24 = DP_MODEL_DUCKYPAD_PRO
        self.local_dir = 2
        self.usbmsc = 3
        self.hidmsg = 4
        self.unknown = 255
        self.device_type = self.unknown
        self.connection_type = self.unknown
        self.info_dict = None

    def __str__(self):
        return (
            f"dp_type(\n"
            f"  device_type={self.device_type},\n"
            f"  connection_type={self.connection_type},\n"
            f"  info_dict={self.info_dict}\n"
            f")"
        )