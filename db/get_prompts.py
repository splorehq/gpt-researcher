import logging
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession

from db.psql_tables import PromptTemplatesGroupsMapping, PromptTemplates, PromptTemplatesGroups


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
    group_query = (
        select(PromptTemplatesGroups.name)
        .filter(PromptTemplatesGroups.id == prompts_id)
    )
    group_result = await psql_sess.execute(group_query)
    specialisation = group_result.scalars().first()

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
    processed_resp = {item['name']: item['template'] for item in resp}
    flattened_resp = {}
    for name, templates in processed_resp.items():
        if isinstance(templates, list):
            # Flatten the list of dicts with 'role' and 'content' keys into a single dict
            flattened_dict = {d['role']: d['content'] for d in templates if 'role' in d and 'content' in d}
            flattened_resp[name] = flattened_dict
        else:
            flattened_resp[name] = templates


    return specialisation, flattened_resp