from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings
from app.templates import structure_dict


sys_prompt = """
您是一位专业的演示文稿设计师，拥有创作自由来设计引人入胜的演示文稿。

选择最能匹配幻灯片内容的布局。
在创建演示文稿结构时，应考虑用户指令，但幻灯片数量除外。
"""

llm_provider = OpenAIProvider(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
llm = OpenAIChatModel(model_name=settings.LLM_MODEL, provider=llm_provider)
agent = Agent(llm, deps_type=str, system_prompt=sys_prompt, output_type=structure_dict)


@agent.system_prompt  
def add_instructions(ctx: RunContext[str]) -> str:
    return f"用户指令：\n {ctx.deps['instructions']} \n\n"


@agent.system_prompt
def add_layout(ctx: RunContext[str]) -> str:  
    return f"演示文稿布局：\n{ctx.deps['presentation_layout']}\n\n"


@agent.system_prompt
def add_sides_num(ctx: RunContext[str]) -> str:  
    return f"根据最能服务于演示文稿目标的原则，为每个{ctx.deps['n_slides']}幻灯片选择布局索引。\n\n"

agent.run_sync("演示文稿布局：\n{presentation_layout}\n\n", deps={"instructions": "演示文稿布局", "presentation_layout": "演示文稿布局", "n_slides": 10})
