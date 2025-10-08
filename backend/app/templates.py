

from pydantic_ai import StructuredDict


HumanDict = StructuredDict(
    {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'}
        },
        'required': ['name', 'age']
    },
    name='Human',
    description='A human with a name and age',
)

outline_dict = StructuredDict(
    {
        "properties": {
            "slides": {
                "description": "List of slide outlines",
                "items": {
                    "properties": {
                        "content": {
                            "description": "Markdown content for each slide",
                            "maxLength": 300,
                            "minLength": 100,
                            "title": "Content",
                            "type": "string"
                        }
                    },
                    "required": [
                        "content"
                    ],
                    "title": "SlideOutlineModelWithNSlides",
                    "type": "object"
                },
                "maxItems": 2,
                "minItems": 2,
                "title": "Slides",
                "type": "array"
            }
        },
        "required": [
            "slides"
        ],
        "title": "PresentationOutlineModelWithNSlides",
        "type": "object"
    }

)

# 用于演示文稿结构的模板，返回布局索引数组
structure_dict = StructuredDict(
    {
        "properties": {
            "slides": {
                "description": "List of slide layout indexes",
                "items": {
                    "type": "integer",
                    "minimum": 0
                },
                "type": "array"
            }
        },
        "required": [
            "slides"
        ],
        "title": "PresentationStructureModel",
        "type": "object"
    }
)
