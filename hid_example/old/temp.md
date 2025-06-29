
### ⚠️⚠️⚠️ Commands Below are duckyPad (2020) ONLY ⚠️⚠️⚠️

### List files (0x0a)

If command type is 0x0a, duckyPad will start listing the files and directories on the SD card. Names are ASCII-encoded.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0a        |
| 3 ... 63 | relative path (ASCII-encoded) or 0x00 for root-dir listing |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY, 3 = EOF |
| 3 ... 63 | file or directory name (ASCII-encoded) |

As each byte is only 64 bytes the following entry must be requested via Resume operation (0x0c). End of listing is indicated by EOF (0x03) while data chunk contains NULL bytes.

### Read file (0x0b)

If command type is 0x0b, duckyPad will read and return its content.


* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0a        |
| 3 ... 63 | relative path to file (ASCII-encoded) |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY, 3 = EOF |
| 3 ... 62 | 60B chunk of data |
| 63       | 0x00 |

Only 60 bytes of data are returned per each call thus next chunk must be requested via Resume operation (0x0c). End of file is indicated by EOF (0x03) while data chunk contains NULL bytes.

### Resume operation (0x0c)

If command type is 0x0c, duckyPad will - depending on the previous operation - either get another chunk of data (read file) or retrieve another line of file/dir listing (list files).

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0c        |
| 3 ... 63 | 0x00 |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 62 | data chunk / file or directory name  |
| 63       | 0x00 |

Only 60 bytes of data are returned per each call. This call should be repeated until byte[2] equals EOF (0x03) which indicates end of output.

### Abort operation (0x0d)

TODO

### Open file for writing (0x0e)

If command type is 0x0e, duckyPad will open a specified filename in write-mode. This is a required operation before the actual write command is called.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0e        |
| 3 ... 63 | path to file (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Write to file (0x0f)

If command type is 0x0f, duckyPad will write 60 bytes of data in payload to a file previously opened by "Open file for writing" command. Repeated call results in payload being appended. In order to finish the transfer, file must be closed.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0f        |
| 3 ... 62 | data to be written |
|     63   |        0x00        |


* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Close file (0x10)

If command type is 0x10, duckyPad will close currently opened (in write mode) file.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x10        |
| 3 ... 63 | 0x00 |


* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Delete file (0x11)

If command type is 0x11, duckyPad will delete file name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x11        |
| 3 ... 63 | relative path to a file (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Create dir (0x12)

If command type is 0x12, duckyPad will create a directory with name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x12        |
| 3 ... 63 | relative path to a directory (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Delete dir (0x13)

If command type is 0x13, duckyPad will create a directory with name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x13        |
| 3 ... 63 | relative path to a directory (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |