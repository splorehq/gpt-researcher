import logging
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from db.psql_tables import ChatAgents

logger = logging.getLogger(__name__)

async def read_agent_conf(psql_sess: AsyncSession, cols: List[str], base_id: str, agent_name: str = "splore") -> dict:
    """
    This async function retrieve agent config from chat_agents wrt to the base.

    Args:
        psql_sess (AsyncSession): the psql db connection session.
        cols (list[str]): list of fields to retrieve.
        base_id (str): the base for retrieval.
        agent_name (str): the agent name defined for the agent.

    Returns:
        dict: the chat_agents entry for the chat config.

    """
    cols_attr = [getattr(ChatAgents, col) for col in cols]
    result = (
        await psql_sess.scalars(select(ChatAgents).options(load_only(*cols_attr)).
                                where(ChatAgents.base_id == base_id, ChatAgents.name == agent_name))
    ).first()
    if not result:
        error = f"base search config not found for base_id: {base_id}"
        logger.error(error)
    resp = {col: getattr(result, col) for col in cols}
    return resp

async def read_agent_conf_by_id(psql_sess: AsyncSession, cols: List[str], agent_id: str) -> dict:
    """
    This async function retrieve agent config from chat_agents wrt to the agent.

    Args:
        psql_sess (AsyncSession): the psql db connection session.
        cols (list[str]): list of fields to retrieve.
        agent_id (str): the agent for retrieval.

    Returns:
        dict: the chat_agents entry for the chat config.

    """
    cols_attr = [getattr(ChatAgents, col) for col in cols]
    result = (
        await psql_sess.scalars(select(ChatAgents).options(load_only(*cols_attr)).
                                where(ChatAgents.id == agent_id))
    ).first()
    if not result:
        error = f"base search config not found for id: {agent_id}"
        logger.error(error)
    resp = {col: getattr(result, col) for col in cols}
    return resp