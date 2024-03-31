
reloads = 0

def on_reload(old_plugin):
    global reloads
    reloads = old_plugin.reloads + 1

def request_data() -> int:
    print(f'number of reloads: {reloads}')

def handle_data(data: bytes):
    pass
