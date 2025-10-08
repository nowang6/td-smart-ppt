from datetime import datetime
from typing import List, Optional, Dict
import uuid
from pydantic import BaseModel, Field

from models.presentation_layout import PresentationLayoutModel
from models.presentation_outline_model import PresentationOutlineModel
from models.presentation_structure_model import PresentationStructureModel
from utils.datetime_utils import get_current_utc_datetime


class PresentationModel(BaseModel):
    """内存缓存的演示文稿模型"""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    n_slides: int
    language: str
    title: Optional[str] = None
    file_paths: Optional[List[str]] = None
    outlines: Optional[dict] = None
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    layout: Optional[dict] = None
    structure: Optional[dict] = None
    instructions: Optional[str] = None
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    include_table_of_contents: bool = False
    include_title_slide: bool = True
    web_search: bool = False

    def model_post_init(self, __context) -> None:
        """在模型初始化后更新updated_at时间"""
        self.updated_at = get_current_utc_datetime()

    def get_new_presentation(self):
        return PresentationModel(
            id=uuid.uuid4(),
            content=self.content,
            n_slides=self.n_slides,
            language=self.language,
            title=self.title,
            file_paths=self.file_paths,
            outlines=self.outlines,
            layout=self.layout,
            structure=self.structure,
            instructions=self.instructions,
            tone=self.tone,
            verbosity=self.verbosity,
            include_table_of_contents=self.include_table_of_contents,
            include_title_slide=self.include_title_slide,
        )

    def get_presentation_outline(self):
        if not self.outlines:
            return None
        return PresentationOutlineModel(**self.outlines)

    def get_layout(self):
        if not self.layout:
            return None
        return PresentationLayoutModel(**self.layout)

    def set_layout(self, layout: PresentationLayoutModel):
        self.layout = layout.model_dump()
        self.updated_at = get_current_utc_datetime()

    def get_structure(self):
        if not self.structure:
            return None
        return PresentationStructureModel(**self.structure)

    def set_structure(self, structure: PresentationStructureModel):
        self.structure = structure.model_dump()
        self.updated_at = get_current_utc_datetime()

    def update_content(self, content: str):
        """更新内容并更新时间戳"""
        self.content = content
        self.updated_at = get_current_utc_datetime()

    def update_outlines(self, outlines: dict):
        """更新大纲并更新时间戳"""
        self.outlines = outlines
        self.updated_at = get_current_utc_datetime()


class PresentationCache:
    """演示文稿内存缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[uuid.UUID, PresentationModel] = {}
    
    def create(self, presentation: PresentationModel) -> PresentationModel:
        """创建新的演示文稿"""
        self._cache[presentation.id] = presentation
        return presentation
    
    def get(self, presentation_id: uuid.UUID) -> Optional[PresentationModel]:
        """根据ID获取演示文稿"""
        return self._cache.get(presentation_id)
    
    def update(self, presentation: PresentationModel) -> PresentationModel:
        """更新演示文稿"""
        presentation.updated_at = get_current_utc_datetime()
        self._cache[presentation.id] = presentation
        return presentation
    
    def delete(self, presentation_id: uuid.UUID) -> bool:
        """删除演示文稿"""
        if presentation_id in self._cache:
            del self._cache[presentation_id]
            return True
        return False
    
    def list_all(self) -> List[PresentationModel]:
        """获取所有演示文稿"""
        return list(self._cache.values())
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
    
    def count(self) -> int:
        """获取缓存中的演示文稿数量"""
        return len(self._cache)


# 全局缓存实例
presentation_cache = PresentationCache()
