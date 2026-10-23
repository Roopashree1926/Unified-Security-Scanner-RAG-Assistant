from pydantic import BaseModel
from typing import Optional


class Finding(BaseModel):
    scanner: str
    target: str
    title: str
    severity: str
    description: str
    port: Optional[int] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None