from typing import List, Optional, Dict
from datetime import datetime
import uuid

from pydantic import BaseModel

from models.sql.slide import SlideModel


class PresentationWithSlides(BaseModel):
    id: uuid.UUID
    content: str
    n_slides: int
    language: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tone: Optional[str] = None
    verbosity: Optional[str] = None
    slides: List[SlideModel]

class PresentationWithSlidesCache:
    """演示文稿与幻灯片内存缓存管理器"""
    
    def __init__(self):
        self._cache: Dict[uuid.UUID, PresentationWithSlides] = {}
    
    def create(self, presentation_with_slides: PresentationWithSlides) -> PresentationWithSlides:
        """创建新的演示文稿与幻灯片"""
        self._cache[presentation_with_slides.id] = presentation_with_slides
        return presentation_with_slides
    
    def get(self, presentation_id: uuid.UUID) -> Optional[PresentationWithSlides]:
        """根据ID获取演示文稿与幻灯片"""
        return self._cache.get(presentation_id)
    
    def update(self, presentation_with_slides: PresentationWithSlides) -> PresentationWithSlides:
        """更新演示文稿与幻灯片"""
        presentation_with_slides.updated_at = datetime.utcnow()
        self._cache[presentation_with_slides.id] = presentation_with_slides
        return presentation_with_slides
    
    def delete(self, presentation_id: uuid.UUID) -> bool:
        """删除演示文稿与幻灯片"""
        if presentation_id in self._cache:
            del self._cache[presentation_id]
            return True
        return False
    
    def list_all(self) -> List[PresentationWithSlides]:
        """获取所有演示文稿与幻灯片"""
        return list(self._cache.values())
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
    
    def count(self) -> int:
        """获取缓存中的演示文稿与幻灯片数量"""
        return len(self._cache)


# 全局缓存实例
presentation_with_slides_cache = PresentationWithSlidesCache()