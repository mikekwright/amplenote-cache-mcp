from typing import TypedDict


class Note(TypedDict):
    remote_uuid: str
    local_uuid: str
    name: str
    metadata: str | None
    text: str | None
    remote_content: str | None
    remote_digest: str | None


class NoteBasic(TypedDict):
    remote_uuid: str
    local_uuid: str
    name: str


class NoteWithTimestamp(TypedDict):
    remote_uuid: str
    local_uuid: str
    name: str
    updated_at: str


class NoteSearchResult(TypedDict):
    uuid: str
    name: str
    snippet: str


class NoteReference(TypedDict):
    uuid: str
    name: str | None


class NoteReferences(TypedDict):
    referenced_by: list[NoteReference]
    references: list[NoteReference]


