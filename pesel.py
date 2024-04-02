"""
Copyright 2024 truenotzero

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import asyncio
from plugin import Plugin

# parse command line args to configure local socket & remote endpoint

def read_config() -> tuple[int, str, int]:
    try:
        first_arg = sys.argv[1]
        if first_arg is None or first_arg == '--help':
            print('./pesel.py <local-port> <remote-address> <remote-port>')

        remote_address = sys.argv[2]
        remote_port = sys.argv[3]
        return first_arg, remote_address, remote_port

    except IndexError:

        print('./pesel.py <local-port> <remote-address> <remote-port>')

        return None, None, None


async def bridge(left_rx: asyncio.StreamReader, right_tx: asyncio.StreamWriter, handler: Plugin, do_close: asyncio.Event):
    try:
        while not do_close.is_set():
            data = await left_rx.read(handler.request_data())
            if data:
                # process by the plugin
                output = handler.handle_data(data) or data
                right_tx.write(output)
            else:
                break
    except Exception as e:
        print(f"Terminating bridge, caught exception: {e}")
        do_close.set()


def load_plugin(*path) -> Plugin:
    try:
        return Plugin(*path)
    except (ModuleNotFoundError, AttributeError) as e:
        raise RuntimeError(e) from e


async def on_connect(local_port: int, remote_address: str, remote_port: int, local_rx: asyncio.StreamReader, local_tx: asyncio.StreamWriter):
    # once a connection is received, connect to the remote endpoint (localhost:25565)
    remote_rx, remote_tx = await asyncio.open_connection(remote_address, remote_port)

    # create plugin
    # the plugin name should be in the format
    # <local-port>-<remote-address>-<remote-port>/sv.py for server handler
    # <local-port>-<remote-address>-<remote-port>/cl.py for client handler
    base = f"{local_port}-{remote_address}-{remote_port}"
    ltr_handler = load_plugin(base, "cl")
    rtl_handler = load_plugin(base, "sv")

    # async
    # read all input from client, forward to server
    # read all input from server, forward to client
    do_close = asyncio.Event()
    local_to_remote = bridge(local_rx, remote_tx, ltr_handler, do_close)
    remote_to_local = bridge(remote_rx, local_tx, rtl_handler, do_close)

    await asyncio.gather(local_to_remote, remote_to_local)


async def create_listener(local_port, remote_address, remote_port) -> asyncio.events.AbstractServer:
    return await asyncio.start_server(lambda rx, tx: on_connect(local_port, remote_address, remote_port, rx, tx), 'localhost', local_port)


async def main():
    # read the config (localhost:7777 -> localhost:25565)
    local_port, remote_address, remote_port = read_config()

    if local_port is None:
        return

    # listen on TCP localohost:7777
    lsock = await create_listener(local_port, remote_address, remote_port)

    # await incoming connections
    async with lsock:
        await lsock.serve_forever()



def teckst():
    from plugin import Plugin
    import time
    p = Plugin("test")
    while True:
        # pylint: disable=no-member
        p.request_data()
        time.sleep(1.0)

if __name__ == '__main__':
    asyncio.run(main())
