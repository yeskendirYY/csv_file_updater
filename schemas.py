from pydantic import BaseModel


class EmitentData(BaseModel):
    emitent_id: str
    ticker: str
