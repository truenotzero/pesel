"""
Copyright 2024 truenotzero

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

HANDLERS = {}

def handler(opcode: int):
    def decorator(func):
        print(f"client: [0x{opcode:02X}] => '{func.__name__}'")
        HANDLERS[opcode] = func
        return func
    return decorator

def on_reload(old_plugin):
    print('client: reloaded!')

def request_data() -> int:
    return 1024

def handle_data(data: bytes):
    try:
        opcode = data[0]
        HANDLERS[opcode](data[1:])
    except KeyError:
        fallback(data)

def fallback(data: bytes):
    print(f"-> [0x{data[0]:02X}] {data[1:].hex(' ').upper()}")

import struct

@handler(0x01)
def login(data: bytes):
    protocol_version, user_len = struct.unpack("!IH", data[:6])
    user = struct.unpack(f"!{user_len}s", data[6:6+user_len])[0].decode("utf-8")
    pssw_len = struct.unpack("!H", data[6+user_len:6+user_len+2])[0]
    pssw = struct.unpack(f"!{pssw_len}s", data[6+user_len+2:])[0].decode("utf-8")

    print(f"-> login: protocol={protocol_version} user={user} pass={pssw}")