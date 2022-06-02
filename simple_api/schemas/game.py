from pydantic import BaseModel

class Game(BaseModel):
    name: str
    platform: str
    timespend: float