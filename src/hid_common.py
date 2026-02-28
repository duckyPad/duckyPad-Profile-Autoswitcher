import hid
import sys
import time
import os
import select
from datetime import datetime
import threading

hid_txrx_lock = threading.Lock()

dp20_pid = 0xd11c
dpp_pid = 0xd11d
all_dp_pids = [dp20_pid, dpp_pid]

DUCKYPAD_VID = 0x0483
DUCKYPAD_VID_STR_UPPER = '00000483'
DUCKYPAD_PID_STRS_UPPER = ['0000D11C', '0000D11D']

def is_duckypad_pid(this_pid):
    return this_pid in all_dp_pids

_use_hidraw = 'linux' in sys.platform

# ---------------------------------------------------------------------------
# Linux hidraw backend: communicates via /dev/hidraw* without detaching the
# kernel HID driver. This is critical because duckyPad Pro exposes keyboard,
# mouse, consumer-control AND custom-HID reports on a single USB interface.
# The libusb backend calls libusb_claim_interface() which detaches the kernel
# driver from the entire interface, blocking ALL keyboard/mouse input.
# hidraw operates alongside the kernel driver — both receive HID reports.
# ---------------------------------------------------------------------------

def _linux_find_duckypad_hidraw_paths():
    """Scan /sys/class/hidraw/ for duckyPad devices, return list of /dev/hidrawN paths."""
    paths = []
    hidraw_base = '/sys/class/hidraw'
    if not os.path.isdir(hidraw_base):
        return paths
    for entry in os.listdir(hidraw_base):
        uevent_path = os.path.join(hidraw_base, entry, 'device', 'uevent')
        try:
            with open(uevent_path) as f:
                content = f.read()
        except OSError:
            continue
        if DUCKYPAD_VID_STR_UPPER not in content:
            continue
        if not any(pid in content for pid in DUCKYPAD_PID_STRS_UPPER):
            continue
        paths.append(f'/dev/{entry}')
    return paths

def _linux_hidraw_txrx(path, buf_64b, timeout_sec=0.5):
    """Send a 64-byte HID output report and read the response via hidraw.

    Returns the response as a list of ints, or None on timeout/error.
    The kernel driver stays attached — keyboard input is not disrupted.
    """
    fd = os.open(path, os.O_RDWR)
    try:
        os.write(fd, bytes(buf_64b))
        deadline = time.monotonic() + timeout_sec
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            ready, _, _ = select.select([fd], [], [], min(remaining, 0.05))
            if not ready:
                continue
            data = os.read(fd, 256)
            if data and len(data) > 0 and data[0] in CUSTOM_HID_REPORT_ID_READ:
                return list(data)
    except OSError:
        return None
    finally:
        os.close(fd)

def _linux_get_all_dp_info(hidraw_paths):
    """Get device info for all duckyPads found via hidraw."""
    dp_info_list = []
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    for path in hidraw_paths:
        result = _linux_hidraw_txrx(path, pc_to_duckypad_buf, timeout_sec=1.0)
        if result is None or len(result) < 3 or result[2] != HID_RESPONSE_OK:
            continue
        this_dict = make_dp_info_dict(result, path)
        dp_info_list.append(this_dict)
    return dp_info_list

# ---------------------------------------------------------------------------
# Cross-platform public API
# ---------------------------------------------------------------------------

def get_duckypad_path():
    if _use_hidraw:
        return _linux_find_duckypad_hidraw_paths()
    dp_path_list = set()
    if 'win32' in sys.platform:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == DUCKYPAD_VID and \
            is_duckypad_pid(device_dict['product_id']) and \
            device_dict['usage'] == 58:
                dp_path_list.add(device_dict['path'])
    else:
        for device_dict in hid.enumerate():
            if device_dict['vendor_id'] == DUCKYPAD_VID and \
            is_duckypad_pid(device_dict['product_id']):
                dp_path_list.add(device_dict['path'])
    return list(dp_path_list)

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64
CUSTOM_HID_REPORT_ID_WRITE = 5
CUSTOM_HID_REPORT_ID_READ = [4, 5]

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
    if _use_hidraw:
        return _linux_get_all_dp_info(dp_path_list)
    dp_info_list = []
    pc_to_duckypad_buf = get_empty_pc_to_duckypad_buf()
    for this_path in dp_path_list:
        myh = hid.device()
        try:
            myh.open_path(this_path)
        except Exception:
            continue
        myh.write(pc_to_duckypad_buf)
        start_time = time.time()
        result = None
        while (time.time() - start_time) < 1.0:
            remaining_ms = int((1.0 - (time.time() - start_time)) * 1000)
            if remaining_ms <= 0:
                break
            buf = myh.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=min(remaining_ms, 100))
            if buf and len(buf) > 0 and buf[0] in CUSTOM_HID_REPORT_ID_READ:
                result = buf
                break
        myh.close()
        if result is None or len(result) < 3 or result[2] != HID_RESPONSE_OK:
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
    ptd_buf[0] = CUSTOM_HID_REPORT_ID_WRITE
    return ptd_buf

def hid_txrx_nolock(buf_64b, hid_obj):
    print("\n\nSending to duckyPad:\n", buf_64b)
    hid_obj.write(buf_64b)
    start_time = time.time()
    timeout_sec = 0.5
    while (time.time() - start_time) < timeout_sec:
        remaining_ms = int((timeout_sec - (time.time() - start_time)) * 1000)
        if remaining_ms <= 0:
            break
        duckypad_to_pc_buf = hid_obj.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=min(remaining_ms, 50))
        if duckypad_to_pc_buf and len(duckypad_to_pc_buf) > 0 and duckypad_to_pc_buf[0] in CUSTOM_HID_REPORT_ID_READ:
            print("\nduckyPad response:\n", duckypad_to_pc_buf)
            return duckypad_to_pc_buf
    return None

_cached_hid_path = None

def set_cached_hid_path(path):
    global _cached_hid_path
    _cached_hid_path = path

def get_cached_hid_path():
    return _cached_hid_path

def hid_txrx_open_close(buf_64b):
    """Send command and receive response, opening device only for this operation.

    On Linux, uses /dev/hidraw directly so the kernel HID driver stays attached
    and keyboard/mouse input continues to work.
    On other platforms, falls back to the hidapi library (libusb/IOKit).
    """
    path = get_cached_hid_path()
    if path is None:
        return None
    if _use_hidraw:
        return _linux_hidraw_txrx(path, buf_64b)
    try:
        temp_hid = hid.device()
        temp_hid.open_path(path)
    except Exception:
        return None
    try:
        temp_hid.write(buf_64b)
        start_time = time.time()
        timeout_sec = 0.5
        while (time.time() - start_time) < timeout_sec:
            remaining_ms = int((timeout_sec - (time.time() - start_time)) * 1000)
            if remaining_ms <= 0:
                break
            buf = temp_hid.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=min(remaining_ms, 50))
            if buf and len(buf) > 0 and buf[0] in CUSTOM_HID_REPORT_ID_READ:
                return buf
        return None
    finally:
        temp_hid.close()

def hid_txrx(buf_64b, hid_obj):
    if _use_hidraw:
        return hid_txrx_open_close(buf_64b)
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

def duckypad_sync_rtc(hid_obj, use_open_close=False):
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
    if use_open_close:
        hid_txrx_open_close(pc_to_duckypad_buf)
    else:
        hid_txrx(pc_to_duckypad_buf, hid_obj)

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