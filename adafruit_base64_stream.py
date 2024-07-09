# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_base64_stream`
================================================================================


A wrapper around a file stream that will return the data as base64 when read


* Author(s): Justin Myers

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Base64_Stream.git"


import binascii


class Base64Stream:
    """A file wrapper that retuns base64 encoded data when read."""

    def __init__(self, file_handle):
        self._file_handle = file_handle
        self._read_buffer = b""

    def seek(self, target, whence=0):
        """Change the stream position to the given offset.
        Behaviour depends on the whence parameter."""

        if target == whence == 0:
            # move to start
            self._read_buffer = b""
        elif target == 0 and whence == 2:
            # move to end
            pass
        else:
            raise ValueError("Seeking to the middle of a file is not supported.")

        return self._file_handle.seek(target, whence)

    def tell(self):
        """Return the current stream position as an opaque number"""

        pos = self._file_handle.tell()
        pos = pos * 4 / 3
        if pos % 4:
            pos += 4 - pos % 4
        return int(pos)

    def read(self, size=-1):
        """Read and return at most size characters from the stream as a single str.
        If size is negative or None, reads until EOF."""

        encoded_data = b""

        if size == 0:
            return encoded_data

        if size in (-1, None):
            read_size = -1
        else:
            if size < 4:
                raise ValueError(
                    "To correctly encode, you must request at lease 4 bytes."
                )

            read_size = int((size - len(self._read_buffer)) * 3 / 4)

        data = self._read_buffer
        data += self._file_handle.read(read_size)
        len_data = len(data)

        if len_data == 0:
            # no data return b""
            return encoded_data

        if len_data == len(self._read_buffer):
            # no new data, clear out the _read_buffer and use
            self._read_buffer = b""
        elif len_data <= 3:
            # if we have less then 4 bytes, clear out the _read_buffer and use
            self._read_buffer = b""
        else:
            # calculate the extra bytes (we don't want to encode multiples that aren't of 3)
            extra_data = -1 * (len_data % 3)
            if extra_data != 0:
                # Store extra bytes into the _read_buffer and remove from what we want to encode
                self._read_buffer = data[extra_data:]
                data = data[:extra_data]
            else:
                self._read_buffer = b""

        encoded_data = binascii.b2a_base64(data).strip()

        return encoded_data

    def readinto(self, buffer):
        """Read and fill the supplied buffer with at most size characters from the stream."""
        size = len(buffer)
        data = self.read(size)
        read_size = len(data)
        buffer[0:read_size] = data
        return read_size
