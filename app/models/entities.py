
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict
class NamespaceId(BaseModel):
    organization: Optional[str] = None
    name: Optional[str] = None
class Namespace(BaseModel):
    id: NamespaceId
    description: Optional[str] = None
    contact_email: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
class Organization(BaseModel):
    identifier: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
class EntityId(BaseModel):
    namespace: Optional[NamespaceId] = None
    name: Optional[str] = None
class Subject(BaseModel):
    id: EntityId
    kind: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    gateways: List[Any] = Field(default_factory=list)
class Sample(BaseModel):
    id: EntityId
    subject: Optional[EntityId] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    gateways: List[Any] = Field(default_factory=list)
class File(BaseModel):
    id: EntityId
    samples: List[EntityId] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    gateways: List[Any] = Field(default_factory=list)
class Counts(BaseModel):
    current: int
    all: int
class Summary(BaseModel):
    counts: Counts
class SubjectPage(BaseModel):
    summary: Summary
    data: List[Subject]
class SamplePage(BaseModel):
    summary: Summary
    data: List[Sample]
class FilePage(BaseModel):
    summary: Summary
    data: List[File]
class InfoServer(BaseModel):
    owner: Optional[str] = None
    contact_email: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    about_url: Optional[str] = None
    repository_url: Optional[str] = None
    issues_url: Optional[str] = None
class InfoApi(BaseModel):
    api_version: Optional[str] = None
    documentation_url: Optional[str] = None
class InfoData(BaseModel):
    version: Optional[dict] = None
    last_updated: Optional[str] = None
    wiki_url: Optional[str] = None
    documentation_url: Optional[str] = None
class InfoResponse(BaseModel):
    server: InfoServer
    api: InfoApi
    data: InfoData
class FieldDescription(BaseModel):
    harmonized: Optional[bool] = None
    path: Optional[str] = None
    wiki_url: Optional[str] = None
class FieldDescriptions(BaseModel):
    fields: List[FieldDescription]
# --- by/count result models (match components: responses.by.count.*) ---
class ValueCount(BaseModel):
    value: Any
    count: int

class ByCountSubjectResults(BaseModel):
    total: int
    missing: int
    values: List[ValueCount]

class ByCountSampleResults(BaseModel):
    total: int
    missing: int
    values: List[ValueCount]

class ByCountFileResults(BaseModel):
    total: int
    missing: int
    values: List[ValueCount]
