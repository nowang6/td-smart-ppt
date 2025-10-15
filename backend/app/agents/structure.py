from pydantic_ai import Agent, RunContext
from app.templates import structure_dict
from dataclasses import dataclass
from typing import Optional
from models.presentation_layout import PresentationLayoutModel
from app.llm import llm_model



sys_prompt = """
您是一位专业的演示文稿设计师，拥有创作自由来设计引人入胜的演示文稿。

选择最能匹配幻灯片内容的布局。
在创建演示文稿结构时，应考虑用户指令，但幻灯片数量除外。
"""

@dataclass
class StructureDependencies:  
    presentation_layout: PresentationLayoutModel
    n_slides: int
    instructions: Optional[str] = None
    

structure_agent = Agent(llm_model, deps_type=StructureDependencies, system_prompt=sys_prompt, output_type=structure_dict)


@structure_agent.system_prompt  
def add_instructions(ctx: RunContext[StructureDependencies]) -> str:
    return f"用户指令：\n {ctx.deps.instructions} \n\n"


@structure_agent.system_prompt
def add_layout(ctx: RunContext[StructureDependencies]) -> str:  
    return f"演示文稿布局：\n{ctx.deps.presentation_layout}\n\n"


@structure_agent.system_prompt
def add_sides_num(ctx: RunContext[StructureDependencies]) -> str:  
    return f"根据最能服务于演示文稿目标的原则，为每个{ctx.deps.n_slides}幻灯片选择布局索引。\n\n"