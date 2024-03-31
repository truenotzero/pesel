
import importlib
import types
import typing
import os

Plugin: typing.TypeAlias = types.ModuleType

# REQUIRED_APIS = [
#     "request_bytes",
#     "handle_data"
#     "on_reload",
# ]

REQUIRED_APIS = [
    "test"
]

class Plugin:
    def __init__(self, path: str):
        self.path = path + ".py"
        self.timestamp = 0

        self.module = importlib.import_module(path)
        self.__validate()
        self.__emplace_apis()

    # returns True if the timestamp is newer, as well as updating the saved timestamp
    # returns False otherwise
    def __check_and_update_timestamp(self) -> bool:
        next_time = os.path.getmtime(self.path)
        if next_time > self.timestamp:
            self.timestamp = next_time
            return True
        return False

    # raises AttributeError if a required API is missing
    def __validate(self):
        for api in REQUIRED_APIS:
            if not hasattr(self.module, api):
                raise AttributeError
    
    def __emplace_apis(self):
        def make_wrapper(func_name: str):
            def wrapper(*args, **kwargs):
                self.__refresh()
                func = getattr(self.module, func_name)
                return func(*args, **kwargs)
            return wrapper

        for api in REQUIRED_APIS:
            setattr(self, api, make_wrapper(api))

    def __refresh(self):
        if not self.__check_and_update_timestamp():
            return
        importlib.reload(self.module)
