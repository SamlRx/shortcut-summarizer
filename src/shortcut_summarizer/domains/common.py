from datetime import datetime

from pydantic import BaseModel


class BaseModelWithUpdatedAt(BaseModel):
    updated_at: datetime
