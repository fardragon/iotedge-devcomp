
from typing import Optional
from azure.identity import AuthenticationRecord

import appdirs
import os
from pathlib import Path


class AuthRecord:

    __config_dir = appdirs.user_config_dir('iotedge-devcomp')
    __record_file = 'record.json'

    @staticmethod
    def get() -> Optional[AuthenticationRecord]:
        filepath = os.path.join(AuthRecord.__config_dir, AuthRecord.__record_file)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return AuthenticationRecord.deserialize(f.read())
        else:
            return None

    @staticmethod
    def save(record: AuthenticationRecord) -> None:
        Path(AuthRecord.__config_dir).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(AuthRecord.__config_dir, AuthRecord.__record_file)
        with open(filepath, 'w') as f:
            f.write(record.serialize())
