import os
from pydantic import BaseModel, AnyHttpUrl


class Settings(BaseModel):
    base_url: AnyHttpUrl = ''
    userkey: str

    @classmethod
    def from_env(cls) -> 'Settings':
        base_url = os.getenv('TEXT_API_BASE_URL')
        userkey = os.getenv('TEXT_API_USERKEY')
        if not userkey:
            raise RuntimeError('env TEXT_API_USERKEY is not set')
        return cls(base_url=base_url, userkey=userkey)