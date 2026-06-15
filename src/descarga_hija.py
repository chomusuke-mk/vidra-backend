from tipos import Info, State
from typing import Dict, TypedDict


class Descarga_Hija_dict(TypedDict):
    sub_id: str
    parent_id: str
    info: Info
    state: State


class Descarga_Hija:
    def __init__(
        self,
        sub_id: str,
        parent_id: str,
        info: Info,
        state: State,
    ):
        self.sub_id = sub_id
        self.parent_id = parent_id
        self.info = info
        self.state = state

    def to_dict(self) -> Descarga_Hija_dict:
        return {
            "sub_id": self.sub_id,
            "parent_id": self.parent_id,
            "info": self.info,
            "state": self.state,
        }

    @staticmethod
    def from_dict(data: Dict):
        return Descarga_Hija(
            sub_id=data["sub_id"],
            parent_id=data["parent_id"],
            info=data["info"],
            state=data["state"],
        )
