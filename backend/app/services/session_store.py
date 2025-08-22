# services/session_store.py
from typing import Dict, List
from uuid import uuid4
from langchain.schema import Document

_SESSIONS: Dict[str, List[Document]] = {}

def create_session() -> str:
    sid = uuid4().hex
    _SESSIONS[sid] = []
    return sid

def add_docs(session_id: str, docs: List[Document]) -> None:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = []
    _SESSIONS[session_id].extend(docs)

def get_docs(session_id: str) -> List[Document]:
    return _SESSIONS.get(session_id, [])

def clear_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)
