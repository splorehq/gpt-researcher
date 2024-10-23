from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from backend.psql import Base

class ChatAgents(Base):
    __tablename__ = "chat_agents"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    enable_web_search: Mapped[Optional[bool]]
    base_id: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[Optional[datetime]]
    updated_at: Mapped[Optional[datetime]]
    name: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    role: Mapped[Optional[str]]
    tones: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    default_response: Mapped[Optional[str]]
    prompts: Mapped[Optional[dict]] = mapped_column(__type_pos=JSONB)
    include_source: Mapped[Optional[bool]]
    rewrite_queries: Mapped[Optional[bool]]
    topk: Mapped[Optional[int]]
    use_internal_data: Mapped[Optional[bool]]
    llm_model_name: Mapped[Optional[str]]
    llm_temperature: Mapped[Optional[float]]
    run_profanity_check: Mapped[Optional[bool]]
    classify_queries: Mapped[Optional[bool]]
    query_regen_count: Mapped[Optional[int]]
    use_spr: Mapped[Optional[bool]]
    ranking_profile: Mapped[Optional[str]]
    reranking_profile: Mapped[Optional[str]]
    reranking_threshold: Mapped[float]
    exclude_sites: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    exclude_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    chat_config: Mapped[Optional[dict]] = mapped_column(__type_pos=JSONB)
    web_search_config: Mapped[Optional[dict]] = mapped_column(__type_pos=JSONB)
    prompts_id: Mapped[str]


class PromptTemplates(Base):
    __tablename__ = "prompt_templates"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    template: Mapped[dict] = mapped_column("template", JSONB)
    version: Mapped[int]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    is_current: Mapped[bool]


class PromptTemplatesGroups(Base):
    __tablename__ = "prompt_templates_groups"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    variables: Mapped[dict] = mapped_column("variables", JSONB)


class PromptTemplatesGroupsMapping(Base):
    __tablename__ = "prompt_templates_groups_mapping"
    __table_args__ = {"schema": "public"}

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    group_id: Mapped[str] = mapped_column(index=True)
    template_id: Mapped[str] = mapped_column(index=True)