

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
