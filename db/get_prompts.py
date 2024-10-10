import logging
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from db.psql_tables import PromptTemplatesGroupsMapping, PromptTemplates


logger = logging.getLogger(__name__)


async def read_prompt_template_by_name(psql_sess: AsyncSession, cols: List[str], prompt_name: str):
    cols_attr = [getattr(PromptTemplates, col) for col in cols]
    result = (
        await psql_sess.scalars(select(PromptTemplates).options(load_only(*cols_attr)).
                                where(PromptTemplates.name == prompt_name))
    ).first()
    if not result:
        error = f"base search config not found for name: {prompt_name}"
        logger.error(error)
    resp = {col: getattr(result, col) for col in cols}
    return resp


async def read_prompt_template_by_prompts_id(psql_sess: AsyncSession, cols: List[str], prompts_id: str) -> dict:
    cols_attr = [getattr(PromptTemplates, col) for col in cols]
    query = (
            select(PromptTemplates)
            .join(PromptTemplatesGroupsMapping, PromptTemplates.id == PromptTemplatesGroupsMapping.template_id)
            .filter(PromptTemplatesGroupsMapping.group_id == prompts_id)
            .options(load_only(*cols_attr))
        )
    results = await psql_sess.execute(query)
   
    if not results:
        error = f"base search config not found for id: {prompts_id}"
        logger.error(error)
    
    resp = [{col: getattr(object, col) for object in result for col in cols} for result in results]

    return resp