from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings
from app.templates import outline_dict


sys_prompt = """
你是一名专业的演示文稿创建专家。根据用户需求生成结构化演示文稿，并按照指定的 JSON 模板格式化内容，使用 Markdown 编写。

    指南：
    - 为每一张幻灯片提供 Markdown 格式的内容。
    - 确保演示文稿的逻辑和内容连贯。
    - 更加注重数值数据的呈现。
    - 如果提供了“附加信息”，请将其分割到多张幻灯片中。
    - 内容中不要包含任何图片。
    - 确保内容遵循语言规范。
    - 用户指令应始终被遵循，并优先于其他指令，**但幻灯片编号除外。请不要遵循用户指示中的幻灯片编号。**
    - 不生成目录幻灯片。
    - 即使提供了目录，也不要生成目录幻灯片。
    - 第一张幻灯片必须为标题幻灯片。
"""

llm_provider = OpenAIProvider(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
llm = OpenAIChatModel(model_name=settings.LLM_MODEL, provider=llm_provider)
agent = Agent(llm, instructions=sys_prompt, output_type=outline_dict)