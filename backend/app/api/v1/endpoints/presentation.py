import asyncio
import json
import math
import os
import random
from typing import Annotated, List, Literal, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from models.presentation_outline_model import (
    PresentationOutlineModel,
    SlideOutlineModel
)
from pydantic_ai import Agent, RunContext, StructuredDict
from models.presentation_layout import PresentationLayoutModel
from models.presentation_structure_model import PresentationStructureModel
from dataclasses import dataclass

from enums.tone import Tone
from enums.verbosity import Verbosity
import uuid
from app.agents.structure import structure_agent as structure_agent
from app.agents.structure import StructureDependencies
from app.agents.slide_content import llm
from models.sql.presentation import PresentationModel, presentation_cache
from models.presentation_with_slides import (
    PresentationWithSlides,
    presentation_with_slides_cache,
)
from services.image_generation_service import ImageGenerationService
from models.sql.slide import SlideModel
from models.sse_response import SSECompleteResponse, SSEErrorResponse, SSEResponse
from utils.process_slides import (
    process_slide_add_placeholder_assets,
    process_slide_and_fetch_assets,
)
from models.presentation_layout import SlideLayoutModel
from utils.schema_utils import (
    add_field_in_schema,
    remove_fields_from_schema,
)



router = APIRouter()


@router.post("/create", response_model=PresentationModel)
async def create_presentation(
    content: Annotated[str, Body()],
    n_slides: Annotated[int, Body()],
    language: Annotated[str, Body()],
    file_paths: Annotated[Optional[List[str]], Body()] = None,
    tone: Annotated[Tone, Body()] = Tone.DEFAULT,
    verbosity: Annotated[Verbosity, Body()] = Verbosity.STANDARD,
    instructions: Annotated[Optional[str], Body()] = None,
    include_table_of_contents: Annotated[bool, Body()] = False,
    include_title_slide: Annotated[bool, Body()] = True,
    web_search: Annotated[bool, Body()] = False,
):


    presentation_uuid = uuid.uuid4()
    presentation_id = str(presentation_uuid)

    
    presentation = PresentationModel(
        id=presentation_id,
        content=content,
        n_slides=n_slides,
        language=language,
        file_paths=file_paths,
        tone=tone.value,
        verbosity=verbosity.value,
        instructions=instructions,
        include_table_of_contents=include_table_of_contents,
        include_title_slide=include_title_slide,
        web_search=web_search,
    )
    # 将 presentation 缓存起来
    presentation_cache.create(presentation)

    return presentation

@router.post("/prepare", response_model=PresentationModel)
async def prepare_presentation(
    presentation_id: Annotated[uuid.UUID, Body()],
    outlines: Annotated[List[SlideOutlineModel], Body()],
    layout: Annotated[PresentationLayoutModel, Body()],
    title: Annotated[Optional[str], Body()] = None,
):
    if not outlines:
        raise HTTPException(status_code=400, detail="Outlines are required")
    
    presentation = presentation_cache.get(presentation_id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_outline_model = PresentationOutlineModel(slides=outlines)

    total_slide_layouts = len(layout.slides)
    total_outlines = len(outlines)

    if layout.ordered:
        presentation_structure = layout.to_presentation_structure()
    else:
        presentation_structure: PresentationStructureModel = (
            await generate_presentation_structure(
                presentation_outline=presentation_outline_model,
                presentation_layout=layout,
                instructions=presentation.instructions,
            )
        )

    presentation_structure.slides = presentation_structure.slides[: len(outlines)]
    for index in range(total_outlines):
        random_slide_index = random.randint(0, total_slide_layouts - 1)
        if index >= total_outlines:
            presentation_structure.slides.append(random_slide_index)
            continue
        if presentation_structure.slides[index] >= total_slide_layouts:
            presentation_structure.slides[index] = random_slide_index



    # 更新缓存中的presentation
    presentation.set_layout(layout)
    presentation.set_structure(presentation_structure)
    presentation.update_outlines(presentation_outline_model.model_dump())
    if title:
        presentation.title = title
    presentation_cache.update(presentation)

    return presentation

@router.get("/stream/{id}", response_model=PresentationWithSlides)
async def stream_presentation(id: uuid.UUID):
    presentation = presentation_cache.get(id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    if not presentation.structure:
        raise HTTPException(
            status_code=400,
            detail="Presentation not prepared for stream",
        )
    if not presentation.outlines:
        raise HTTPException(
            status_code=400,
            detail="Outlines can not be empty",
        )
        
    images_directory = "app_data/images"

    image_generation_service = ImageGenerationService(images_directory)

    async def inner():
        structure = presentation.get_structure()
        layout = presentation.get_layout()
        outline = presentation.get_presentation_outline()

        # These tasks will be gathered and awaited after all slides are generated
        async_assets_generation_tasks = []

        slides: List[SlideModel] = []
        yield SSEResponse(
            event="response",
            data=json.dumps({"type": "chunk", "chunk": '{ "slides": [ '}),
        ).to_string()
        for i, slide_layout_index in enumerate(structure.slides):
            slide_layout = layout.slides[slide_layout_index]

            try:
                slide_content = await get_slide_content_from_type_and_outline(
                    slide_layout,
                    outline.slides[i],
                    presentation.instructions,
                )
            except HTTPException as e:
                yield SSEErrorResponse(detail=e.detail).to_string()
                return

            slide = SlideModel(
                presentation=id,
                layout_group=layout.name,
                layout=slide_layout.id,
                index=i,
                speaker_note=slide_content.get("__speaker_note__", ""),
                content=slide_content,
            )
            slides.append(slide)

            # This will mutate slide and add placeholder assets
            process_slide_add_placeholder_assets(slide)

            # This will mutate slide
            async_assets_generation_tasks.append(
                process_slide_and_fetch_assets(image_generation_service, slide)
            )

            yield SSEResponse(
                event="response",
                data=json.dumps({"type": "chunk", "chunk": slide.model_dump_json()}),
            ).to_string()

        yield SSEResponse(
            event="response",
            data=json.dumps({"type": "chunk", "chunk": " ] }"}),
        ).to_string()

        generated_assets_lists = await asyncio.gather(*async_assets_generation_tasks)
        generated_assets = []
        for assets_list in generated_assets_lists:
            generated_assets.extend(assets_list)


        presentationWithSlides = PresentationWithSlides(
            **presentation.model_dump(),
            slides=slides,
        )
        
        # 缓存 presentationWithSlides
        presentation_with_slides_cache.create(presentationWithSlides)
        
        yield SSECompleteResponse(
            key="presentation",
            value=presentationWithSlides.model_dump(mode="json"),
        ).to_string()

    return StreamingResponse(inner(), media_type="text/event-stream")

@router.get("/{id}", response_model=PresentationWithSlides)
async def get_presentation(
    id: uuid.UUID
):
    presentation_with_slides = presentation_with_slides_cache.get(id)  
    return presentation_with_slides

@router.patch("/update", response_model=PresentationWithSlides)
async def update_presentation(
    id: Annotated[uuid.UUID, Body()],
    n_slides: Annotated[Optional[int], Body()] = None,
    title: Annotated[Optional[str], Body()] = None,
    slides: Annotated[Optional[List[SlideModel]], Body()] = None,
):
    presentation = presentation_cache.get(id)
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")

    presentation_update_dict = {}
    if n_slides:
        presentation_update_dict["n_slides"] = n_slides
    if title:
        presentation_update_dict["title"] = title

    if slides:
        # Just to make sure id is UUID
        for slide in slides:
            slide.presentation = uuid.UUID(slide.presentation)
            slide.id = uuid.UUID(slide.id)



    presentation_with_slides = PresentationWithSlides(
        **presentation.model_dump(),
        slides=slides or [],
    )
    
    # 缓存或更新 presentationWithSlides
    if presentation_with_slides_cache.get(id):
        presentation_with_slides_cache.update(presentation_with_slides)
    else:
        presentation_with_slides_cache.create(presentation_with_slides)
    
    return presentation_with_slides




async def generate_presentation_structure(
    presentation_outline: PresentationOutlineModel,
    presentation_layout: PresentationLayoutModel,
    instructions: Optional[str] = None,
) -> PresentationStructureModel:
    deps = StructureDependencies(presentation_layout=presentation_layout, instructions=instructions, n_slides=len(presentation_outline.slides))
    res = await structure_agent.run(presentation_outline.to_string(), deps=deps)
    # 将字典转换为 PresentationStructureModel 对象
    return PresentationStructureModel(**res.output)

async def get_slide_content_from_type_and_outline(
    slide_layout: SlideLayoutModel,
    slide_outline: SlideOutlineModel,
    instructions: Optional[str] = None,
) -> str:
    response_schema = remove_fields_from_schema(
    slide_layout.json_schema, ["__image_url__", "__icon_url__"]
    )
    response_schema = add_field_in_schema(
        response_schema,
        {
            "__speaker_note__": {
                "type": "string",
                "minLength": 100,
                "maxLength": 250,
                "description": "Speaker note for the slide",
            }
        },
        True,
    )
    
    # 将 JSON Schema 转换为 StructuredDict
    structured_schema = StructuredDict(
        response_schema,
        name="SlideContent",
        description="Slide content structure"
    )
    
    sys_prompt = f"""
        根据提供的大纲生成结构化幻灯片，遵循以下步骤和注意事项，并输出结构化结果。
        
        {"# 用户说明:" if instructions else ""}
        {instructions or ""}

        # 步骤
        1. 分析大纲。
        2. 根据大纲生成结构化幻灯片内容。

        # 注意事项
        - 幻灯片正文中不要使用诸如"This slide"、"This presentation"等词语。
        - 重新组织幻灯片正文，使其表达自然流畅。
        - 仅使用 Markdown 来突出重点内容。
        - 确保遵循语言规范。
        - 严格遵守幻灯片中每个字段的最大和最小字符限制。
        - 绝对不要超过最大字符限制。请控制叙述内容以确保不超过最大字符数。
        - 项目数量不得超过幻灯片架构（schema）中指定的最大数量。如需表达多个要点，请合并后符合最大数量要求。
        - 对每个字段生成的字数要非常谨慎。超过最大字符限制会导致设计溢出，因此请提前分析并严格控制生成字数。
        - 内容中不要使用表情符号。
        - 度量（metrics）应使用缩写形式，尽量简短，不要使用冗长的描述。
        用户说明应始终被遵守，并优先于其他所有规则，但不得违反最大/最小字符限制、幻灯片架构和项目数量限制。

        - 输出应为 JSON 格式，且**不要包含 <parameters> 标签**。

        # 图片与图标输出格式
        image: {{
            __image_prompt__: string,
        }}
        icon: {{
            __icon_query__: string,
            }}
    """
    
    outline_agent = Agent(llm, deps_type=StructureDependencies, system_prompt=sys_prompt, output_type=structured_schema)
    res = await outline_agent.run(slide_outline.content, deps={"instructions": instructions})
    return res.output