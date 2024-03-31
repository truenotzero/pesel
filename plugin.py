
import importlib
import types
import typing
import os

Plugin: typing.TypeAlias = types.ModuleType

# plugins should define these
REQUIRED_APIS = [
    "on_reload",    # function(old: Plugin)
    "request_data", # function() -> int
    "handle_data"   # function(data: bytes) -> Option[bytes]
]

class Plugin:
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.path = module_name + ".py"
        self.timestamp = 0
        self.module = None

        self.__request_reload()

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
                self.__request_reload()
                func = getattr(self.module, func_name)
                return func(*args, **kwargs)
            return wrapper

        for api in REQUIRED_APIS:
            setattr(self, api, make_wrapper(api))

    def __request_reload(self):
        if not self.__check_and_update_timestamp():
            return
        old_module = self.module
        self.module = importlib.import_module(self.module_name)
        self.__validate()
        self.__emplace_apis()
        if not old_module is None:
            # pylint: disable=no-member
            self.on_reload(old_module)



