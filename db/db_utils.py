import logging
from typing import Tuple, Union, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from db.chat_agents import read_agent_conf_by_id, read_agent_conf

logger = logging.getLogger(__name__)

async def get_agent(psql_sess: AsyncSession, base_id: Union[str, None], agent_id: str = None,
                    agent_name: Union[str, None] = "splore") -> Tuple[dict, str, str, Union[str, None]]:
    """
    This async function wraps some psql calls to retrieve the corresponding chat agent information.

    Args:
        psql_sess (AsyncSession): psql connection session.
        base_id (str|None): the base the agent belongs to.
        agent_id (str): the agent to retrieve.
        agent_name (str|None): the agent name together with the base id.

    Returns:
        tuple[dict, str, str, str|None]: retrieved agent config, base_id, agent_id and error message.

    """
    base_conf_cols = [
        "id", "base_id", "topk", "use_internal_data", "enable_web_search", "llm_model_name", "llm_temperature",
        "classify_queries", "rewrite_queries", "query_regen_count", "use_spr", "prompts", "ranking_profile",
        "reranking_profile", "exclude_sites", "run_profanity_check", "reranking_threshold", "chat_config","web_search_config"
    ]
    agent_conf = await read_agent_conf_by_id(psql_sess, base_conf_cols, agent_id)

    return agent_conf