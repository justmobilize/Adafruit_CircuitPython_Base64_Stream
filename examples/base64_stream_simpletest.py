# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

from adafruit_base64_stream import Base64Stream

with open("image.png", "rb") as file_handle:
    wrapped_file_handle = Base64Stream(file_handle)
    while True:
        encoded_data = wrapped_file_handle.read(12)
        if not encoded_data:
            break
        print(encoded_data)
