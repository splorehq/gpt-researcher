from typing import Optional, List, Tuple, Any, Dict, Union, Literal
from pydantic import BaseModel, Field, model_validator, field_validator

class RespGenPromptConfig(BaseModel):
    rag_prompt: bool = Field(default=True)
    markdown_reformat: bool = Field(default=False)
    inline_citation: bool = Field(default=False)


class RespGenConfig(BaseModel):
    on: bool = Field(default=True)
    prompts: RespGenPromptConfig = Field(default=RespGenPromptConfig())

    @model_validator(mode="after")
    def format_prompts_config(self) -> "RespGenConfig":
        if self.prompts is None:
            self.prompts = RespGenPromptConfig()
        return self


class ContextQConfig(BaseModel):
    on: bool = Field(default=True)


class YQLConfig(BaseModel):
    target_hits: int = Field(default=10)
    limit: int = Field(default=7)


class RankProfileConfig(BaseModel):
    ratio: float = Field(default=None)
    match_factor: Dict[str, float] = Field(default=None)

    @model_validator(mode="after")
    def match_factor_to_dict(self) -> "RankProfileConfig":
        if self.match_factor is None:
            self.match_factor = {}
        return self


class RetrieveConfig(BaseModel):
    weights: Dict[str, Union[float, Dict[str, float]]] = Field(default=None)
    ranking_profiles: Dict[str, RankProfileConfig] = Field(default=None)
    vespa_config: YQLConfig = Field(default=YQLConfig())

    @model_validator(mode="after")
    def weights_dict(self) -> "RetrieveConfig":
        if self.weights is None:
            self.weights = {}
        return self

    @model_validator(mode="after")
    def rank_profiles_to_dict(self) -> "RetrieveConfig":
        if self.ranking_profiles is None:
            self.ranking_profiles = {}
        return self


class PostProcessConfig(BaseModel):
    enable_chunked_responses : bool = Field(default=False)
    threshold_length: int = Field(default=400)


class RelatedQConfig(BaseModel):
    required: bool = Field(default=False)
    questions: list[str] = Field(default_factory=list)
    query_buffer: int = Field(default=5)


class ChatConfig(BaseModel):
    resp_generation: RespGenConfig = RespGenConfig()
    context_q_rewrite: ContextQConfig = ContextQConfig()
    retrieve: RetrieveConfig = RetrieveConfig()
    related_question: RelatedQConfig = RelatedQConfig()
    post_process: PostProcessConfig = PostProcessConfig()


class TavilyConfig(BaseModel):
    enable: bool = Field(default=False)
    topic: Literal["general", "news"] = Field(default="general")
    search_depth: Literal["basic", "advanced"] = Field(default="basic")
    max_results: int = Field(default=10)
    days: Optional[int] = Field(default=5)
    include_answer: Optional[bool] = Field(default=False)
    include_raw_content: Optional[bool] = Field(default=False)
    include_domains: Optional[list[str]] = Field(default=None)
    exclude_domains: Optional[list[str]] = Field(default=None)


class BingConfig(BaseModel):
    enable: bool = Field(default=False)


class WebSearchConfig(BaseModel):
    tavily_config: TavilyConfig = Field(default=TavilyConfig())
    bing_config: Optional[BingConfig] = Field(default=BingConfig())


class QueryText(BaseModel):
    title: Optional[str] = Field(default=None)
    query: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def at_least_one_text(self) -> "QueryText":
        if not self.title and not self.query:
            raise ValueError("At least one of title and query needs to have certain text")
        return self


class ConversationText(BaseModel):
    title: Optional[str] = Field(default=None)
    messages: List[Tuple[str, str]] = Field(default=[])

    @model_validator(mode="after")
    def msgs_to_array(self) -> "ConversationText":
        if self.messages is None:
            self.messages = []
        return self


class ChatConfig(BaseModel):
    resp_generation: RespGenConfig = RespGenConfig()
    context_q_rewrite: ContextQConfig = ContextQConfig()
    retrieve: RetrieveConfig = RetrieveConfig()
    related_question: RelatedQConfig = RelatedQConfig()
    post_process: PostProcessConfig = PostProcessConfig()


class AgentConfig(BaseModel):
    enable_web_search: bool = Field(default=True)
    prompts: Optional[Dict] = Field(default=None)
    rewrite_queries: bool = Field(default=False)
    topk: int = Field(default=5)
    topk_offset: int = Field(default=0)
    use_internal_data: bool = Field(default=True)
    llm_model_name: str = Field(default="azure/gpt_35_turbo_chat")
    llm_temperature: float = Field(default=0.0)
    run_profanity_check: bool = Field(default=True)
    classify_queries: bool = Field(default=False)
    query_regen_count: int = Field(default=0)
    use_spr: bool = Field(default=True)
    ranking_profile: Optional[str] = Field(default="semantic_gte")
    reranking_profile: Optional[str] = Field(default=None)
    reranking_threshold: float = Field(default=0.55)
    exclude_sites: Optional[list] = Field(default=[])
    base_name: Optional[str] = Field(default=None)
    system_base_ids: Optional[List[str]] = Field(default=[])
    chat_config: Optional[Dict] = Field(default=None)
    web_search_config: Optional[Dict] = Field(default=None)
    prompts_id: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def exclude_sites_to_array(self) -> "AgentConfig":
        if self.exclude_sites is None:
            self.exclude_sites = []
        return self

    @model_validator(mode="after")
    def format_chat_config(self) -> "AgentConfig":
        if self.chat_config is None:
            self.chat_config = ChatConfig()
        return self

    @model_validator(mode="after")
    def format_web_search_config(self) -> "AgentConfig":
        if self.web_search_config is None:
            self.web_search_config = WebSearchConfig()
        return self

    @model_validator(mode="after")
    def system_ids_to_array(self) -> "AgentConfig":
        if self.system_base_ids is None:
            self.system_base_ids = []
        return self

    @model_validator(mode="after")
    def no_web_search_wo_reranker(self) -> "AgentConfig":
        if self.enable_web_search is True and self.reranking_profile is None:
            raise ValueError("Web search must be disabled when no reranker is specified")
        return self