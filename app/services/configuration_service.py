from pathlib import Path
from typing import Any, Dict
import os
from structlog import BoundLogger
import toml

class ConfigurationService():

    def __init__(self, 
                 app_name: str,
                 logger: BoundLogger):
        self.config: Dict[str, Any] = {}
        self.app_folder = Path(f"{os.path.expanduser('~')}/.{app_name}").resolve()
        self.config_file_name = f'.{app_name}_config.toml'
        self.logger = logger

    def load(self) -> bool:
        try:
            file_path = Path(f"{self.app_folder}/{self.config_file_name}")
            if not os.path.exists(str(self.app_folder)):
                os.mkdir(self.app_folder)

            if not os.path.exists(file_path):
                with open(file_path, "w") as toml_file:
                    toml.dump(self.config, toml_file)
            self.config = toml.load(file_path)
        except Exception as e:
            raise Exception('There was an issue loading the configuration file!')

    def get_value_by_key(self, key: str) -> Any:
        return self.config[key]