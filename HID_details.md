# duckyPad HID Command Protocols

[Get duckyPad](https://duckypad.com) | [Official Discord](https://discord.gg/4sJCBx5)

------------

This article describes duckyPad HID command protocols, and how it can be used to control duckyPad from your PC.

## Table of Contents

- [HID Basics](#hid-basics)
- [HID Packet Structure](#hid-packet-structure)
- [HID Examples](#hid-examples)
- [HID Commands](#hid-commands)
    - [Query Info (0x00)](#query-info-0x00)
    - [Goto Profile by **NUMBER** (0x01)](#goto-profile-by-number-0x01)
    - [Goto Profile by **NAME** (0x17)](#goto-profile-by-name-0x17)
    - [Previous Profile (0x02)](#previous-profile-0x02)
    - [Next Profile (0x03)](#next-profile-0x03)
    - [Set RGB Colour: Single (0x04)](#set-rgb-colour-single-0x04)
    - [Software reset (0x14)](#software-reset-0x14)
    - [Sleep (0x15)](#sleep-0x15)
    - [Wake up (0x16)](#wake-up-0x16)
    - [Dump Persistent Global Variables (0x18)](#dump-persistent-global-variables-0x18)
    - [Write Persistent Global Variables (0x19)](#write-persistent-global-variables-0x19)
    - [Update RTC (0x1A)](#update-rtc-0x1a)

## HID Basics

duckyPad enumerates as 4 HID devices:

* Keyboard

* Mouse

* Keypad with Media Keys

* Counted Buffer 

	* Used for two-way communication between DP and PC

------

**Vendor ID**: 0x0483 (1155)

**Product ID**

* **duckyPad (2020)**: 0xd11c (53532) 

* **duckyPad Pro (2024)**: 0xd11d (53533) 

The `Counted Buffer` device has the usage ID of 0x3a (58).

------

## HID Message Structure

### PC-to-duckyPad

duckyPad expects a **fixed 64-byte** message from PC:

|   Byte#  |         Description        |
|:--------:|:--------------------------:|
|     0    | HID Usage ID (always 0x05) |
|     1    |       Reserved      |
|     2    |        Command Type      |
| 3 ... 63 |          Payload          |

### duckyPad-to-PC

duckyPad will reply with a **fixed 64-byte** response:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    HID Usage ID (always 0x04)    |
|     1    |          Reserved         |
|     2    | Status<br>0 = SUCCESS<br>1 = ERROR<br>2 = BUSY||
| 3 ... 63 |             Payload             |

* `BUSY` is returned if duckyPad is executing a script, or in a menu.

### Endianness

All multi-byte values are **Big-Endian**.

## HID Examples

[`cython-hidapi`](https://github.com/trezor/cython-hidapi) is used for HID communication. You can install it with `pip3 install hidapi`.

A couple of [sample scripts](https://github.com/duckyPad/duckyPad-Profile-Autoswitcher/tree/master/hid_example) are provided.

### List HID Devices

First off, try [this script](hid_example/ex0_list.py) to list all available HID devices.

duckyPad should look something like this:

```
manufacturer_string : dekuNukem
path : b'\\\\?\\hid#vid_0483&pid_d11c&col04#8&3a0783ae&0&0003#{4d1e55b2-f16f-11cf-88cb-001111000030}'
product_id : 53532
product_string : duckyPad(2020)
release_number : 512
serial_number : DP20_78426107
usage : 58
usage_page : 1
vendor_id : 1155
```

### Write to duckyPad

Try [this script](hid_example/ex1_open.py) to send a command to go to the next profile.

### Read from duckyPad

[Try this](hid_example/ex2_read_write.py) to send duckyPad a command, AND receive its response.

### Setting Real-time Clock (RTC)

Finally, [this script](hid_example/ex2_read_write.py) sets the [RTC](#update-rtc-0x1a) with your local timezone.

----

You can use those scripts as the starting point of your own program!

## HID Commands

### Query Info (0x00)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0        |
| 3 ... 63 |        0        |

💬 duckyPad to PC:

|  Byte# |           Description          |
|:------:|:------------------------------:|
|    0   |              0x04              |
|    1   |         Reserved        |
|    2   |0 = SUCCESS|
|    3   |     Firmware version Major     |
|    4   |     Firmware version Minor     |
|    5   |     Firmware version Patch     |
|    6   |     Hardware revision<br>20 = duckyPad<br>24 = duckyPad Pro     |
| 7-10 | Serial number (unsigned 32bit) |
|   11   |     Current profile number     |
|   12   |     `is_sleeping`  |
| 13 | `is_rtc_valid` |
| 14-15 | UTC Offset<br>(Minutes)|
| 16-19 | UNIX timestamp |
| 20-63  |              0                 |

-----------

### Goto Profile by **NUMBER** (0x01)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x01        |
|     3    |   Profile number<br>(**1-indexed**)    |
| 4 ... 63 |        0        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

-----------

### Goto Profile by **NAME** (0x17)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x17        |
|     3 ... 63    |   Profile Name String<br>**Case Sensitive**<br>ASCII encoded<br>Zero terminated  |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

-----------

### Previous Profile (0x02)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x02        |
| 3 ... 63 |        0        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |


-----------

### Next Profile (0x03)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x03        |
| 3 ... 63 |        0        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

-----------

### Set RGB Colour: Single (0x04)

Change color of a single LED.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x04        |
|     3    |LED index, 0 to 19  |
|     4    |Red  |
|     5    |Green  |
|     6    |Blue  |
| 7 ... 63 |        0        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

-----------

### Software reset (0x14)

Perform a software reset.

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x14        |
|     3    |        Reboot options<br>0 = Normal<br>1 = Reboot into USB MSC mode  |
| 3 ... 63 | 0 |

💬 duckyPad to PC:

Nothing, because it's rebooting!

**Wait at least 5 seconds** before trying to talk to it again.

-----------

### Sleep (0x15)

Make duckyPad go to sleep.

Screen and RGB LEDs are turned off.

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x15        |
| 3 ... 63 | 0 |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

-----------

### Wake up (0x16)

Wake up from sleep

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x16        |
| 3 ... 63 | 0 |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

----------

### Dump Persistent Global Variables (0x18)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x18        |
| 3 ... 63 | 0 |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3-4 | GV0 |
| 5-6 | GV1 |
|....|....|
| 61-62 | GV29 |


### Write Persistent Global Variables (0x19)

* You can write to multiple GVs at once
* To select a GV to write, add 127 to its index. (aka setting its top bit to 1)
* Leave rest of the payload to 0

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x19        |
| 3 | GV index + 127 |
| 4 | Upper Byte |
| 5 | Lower Byte |
|6-8| Next GV (if needed)|
|9-11| Next GV (if needed)|
|....|....|

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |

### Update RTC (0x1A)

* A **clock icon** should appear on screen if successful.

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x1A        |
| 3-6 | UNIX Timestamp|
| 7-8 | UTC Offset<br>(Minutes) |
|9 ... 63|0|

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |


## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.
