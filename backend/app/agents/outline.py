from pydantic_ai import Agent

from app.templates import outline_dict
from pydantic_ai import Agent, RunContext
from app.llm import llm_model
from dataclasses import dataclass
from typing import Optional

sys_prompt = """
你是一名专业的演示文稿创建专家。根据用户需求生成结构化演示文稿，并按照指定的 JSON 模板格式化内容，使用 Markdown 编写。

    指南：
    - 为每一张幻灯片提供 Markdown 格式的内容。
    - 确保演示文稿的逻辑和内容连贯。
    - 更加注重数值数据的呈现。
    - 如果提供了“附加信息”，请将其分割到多张幻灯片中。
    - 内容中不要包含任何图片。
    - 确保内容遵循语言规范。
    - 用户指令应始终被遵循，并优先于其他指令。
    - 不生成目录幻灯片。
    - 即使提供了目录，也不要生成目录幻灯片。
    - 第一张幻灯片必须为标题幻灯片。
"""


@dataclass
class StructureDependencies:
    instructions: Optional[str] = None
    


outline_agent = Agent(llm_model, deps_type=StructureDependencies, system_prompt=sys_prompt, output_type=outline_dict)

@outline_agent.system_prompt  
def add_instructions(ctx: RunContext[str]) -> str:
    return f"\n# 用户指令：\n {ctx.deps['instructions']} \n\n"