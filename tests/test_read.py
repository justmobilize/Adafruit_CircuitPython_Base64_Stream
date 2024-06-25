# SPDX-FileCopyrightText: Copyright (c) 2024 Justin Myers for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import binascii

import pytest

from adafruit_base64_stream import Base64Stream


@pytest.mark.parametrize(
    ["size", "filename", "multiple_of_three"],
    (
        (None, "green_red.png", False),
        (-1, "green_red.png", False),
        (4, "green_red.png", False),
        (5, "green_red.png", False),
        (6, "green_red.png", False),
        (10, "green_red.png", False),
        (30, "green_red.png", False),
        (100, "green_red.png", False),
        (200, "green_red.png", False),
        (None, "red_green.png", True),
        (-1, "red_green.png", True),
        (4, "red_green.png", True),
        (5, "red_green.png", True),
        (6, "red_green.png", True),
        (10, "red_green.png", True),
        (30, "red_green.png", True),
        (100, "red_green.png", True),
        (200, "red_green.png", True),
        (None, "tiny.txt", False),
        (-1, "tiny.txt", False),
        (4, "tiny.txt", False),
        (5, "tiny.txt", False),
        (6, "tiny.txt", False),
        (10, "tiny.txt", False),
        (30, "tiny.txt", False),
        (100, "tiny.txt", False),
    ),
)
def test_read(size, filename, multiple_of_three):
    with open(f"tests/files/{filename}", "rb") as file_handle:
        raw_data = file_handle.read()
        encoded_expected = binascii.b2a_base64(raw_data).strip()

        extra = len(raw_data) % 3
        if multiple_of_three:
            assert extra == 0
        else:
            assert extra != 0

        file_handle.seek(0)
        wrapped_file_handle = Base64Stream(file_handle)
        encoded = b""
        while True:
            new_encoded = wrapped_file_handle.read(size)
            if not new_encoded:
                break
            encoded += new_encoded

        assert encoded == encoded_expected


def test_read_0():
    with open("tests/files/green_red.png", "rb") as file_handle:
        wrapped_file_handle = Base64Stream(file_handle)
        encoded = wrapped_file_handle.read(0)
        assert encoded == b""


def test_read_too_little():
    with open("tests/files/green_red.png", "rb") as file_handle:
        wrapped_file_handle = Base64Stream(file_handle)
        with pytest.raises(ValueError) as context:
            wrapped_file_handle.read(2)
    assert "To correctly encode, you must request at lease 4 bytes." in str(context)


@pytest.mark.parametrize(
    ["size", "filename", "multiple_of_three"],
    (
        (4, "green_red.png", False),
        (5, "green_red.png", False),
        (6, "green_red.png", False),
        (10, "green_red.png", False),
        (30, "green_red.png", False),
        (100, "green_red.png", False),
        (200, "green_red.png", False),
        (4, "red_green.png", True),
        (5, "red_green.png", True),
        (6, "red_green.png", True),
        (10, "red_green.png", True),
        (30, "red_green.png", True),
        (100, "red_green.png", True),
        (200, "red_green.png", True),
        (4, "tiny.txt", False),
        (5, "tiny.txt", False),
        (6, "tiny.txt", False),
        (10, "tiny.txt", False),
        (30, "tiny.txt", False),
        (100, "tiny.txt", False),
    ),
)
def test_readinto(size, filename, multiple_of_three):
    with open(f"tests/files/{filename}", "rb") as file_handle:
        raw_data = file_handle.read()
        encoded_expected = binascii.b2a_base64(raw_data).strip()

        extra = len(raw_data) % 3
        if multiple_of_three:
            assert extra == 0
        else:
            assert extra != 0

        file_handle.seek(0)
        wrapped_file_handle = Base64Stream(file_handle)
        encoded = b""
        buffer = bytearray(size)
        while True:
            bytes_read = wrapped_file_handle.readinto(buffer)
            if not bytes_read:
                break
            encoded += bytes(buffer[:bytes_read])

        assert encoded == encoded_expected


def test_seek_0_0_clears_read_buffer():
    with open("tests/files/green_red.png", "rb") as file_handle:
        wrapped_file_handle = Base64Stream(file_handle)
        wrapped_file_handle.read(10)
        assert wrapped_file_handle._read_buffer != b""
        wrapped_file_handle.seek(0)
        assert wrapped_file_handle._read_buffer == b""


def test_seek_middle_raises():
    with open("tests/files/green_red.png", "rb") as file_handle:
        wrapped_file_handle = Base64Stream(file_handle)
        with pytest.raises(ValueError) as context:
            wrapped_file_handle.seek(10)
    assert "Seeking to the middle of a file is not supported." in str(context)


@pytest.mark.parametrize(
    "filename",
    (
        "green_red.png",
        "red_green.png",
        "tiny.txt",
    ),
)
def test_tell(filename):
    with open(f"tests/files/{filename}", "rb") as file_handle:
        raw_data = file_handle.read()
        encoded_expected = binascii.b2a_base64(raw_data).strip()

        wrapped_file_handle = Base64Stream(file_handle)
        wrapped_file_handle.seek(0, 2)
        assert wrapped_file_handle.tell() == len(encoded_expected)
