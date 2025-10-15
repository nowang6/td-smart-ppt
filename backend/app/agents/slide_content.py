from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings
from app.templates import structure_dict


sys_prompt = f"""
        根据提供的大纲生成结构化幻灯片，遵循以下步骤和注意事项，并输出结构化结果。

        # 步骤
        1. 分析大纲。
        2. 根据大纲生成结构化幻灯片内容。

        # 注意事项
        - 幻灯片正文中不要使用诸如“This slide”、“This presentation”等词语。
        - 重新组织幻灯片正文，使其表达自然流畅。
        - 仅使用 Markdown 来突出重点内容。
        - 确保遵循语言规范。
        - 严格遵守幻灯片中每个字段的最大和最小字符限制。
        - 绝对不要超过最大字符限制。请控制叙述内容以确保不超过最大字符数。
        - 项目数量不得超过幻灯片架构（schema）中指定的最大数量。如需表达多个要点，请合并后符合最大数量要求。
        - 对每个字段生成的字数要非常谨慎。超过最大字符限制会导致设计溢出，因此请提前分析并严格控制生成字数。
        - 内容中不要使用表情符号。
        - 度量（metrics）应使用缩写形式，尽量简短，不要使用冗长的描述。
        用户说明（User instructions）应始终被遵守，并优先于其他所有规则，但不得违反最大/最小字符限制、幻灯片架构和项目数量限制。

        - 输出应为 JSON 格式，且**不要包含 <parameters> 标签**。

        # 图片与图标输出格式
        image: {{
            __image_prompt__: string,
        }}
        icon: {{
            __icon_query__: string,
        }}
"""


llm_provider = OpenAIProvider(base_url=settings.LLM_BASE_URL, api_key=settings.LLM_API_KEY)
llm = OpenAIChatModel(model_name=settings.LLM_MODEL, provider=llm_provider)
agent = Agent(llm, deps_type=str, system_prompt=sys_prompt, output_type=structure_dict)


@agent.system_prompt  
def add_instructions(ctx: RunContext[str]) -> str:
    return f"用户说明：\n {ctx.deps['instructions']} \n\n"


agent.run_sync("演示文稿布局：\n{presentation_layout}\n\n", deps={"instructions": "演示文稿布局"})
