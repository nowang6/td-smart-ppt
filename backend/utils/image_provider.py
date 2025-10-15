from enums.image_provider import ImageProvider
from app.core.config import settings
from utils.get_env import (
    get_google_api_key_env,
    get_image_provider_env,
    get_openai_api_key_env,
    get_pexels_api_key_env,
    get_pixabay_api_key_env,
)


def is_pixels_selected() -> bool:
    return True


def is_pixabay_selected() -> bool:
    return False


def is_gemini_flash_selected() -> bool:
    return False


def is_dalle3_selected() -> bool:
    return False


def get_selected_image_provider() -> ImageProvider | None:
    """
    Get the selected image provider from environment variables.
    Returns:
        ImageProvider: The selected image provider.
    """
    image_provider_env = get_image_provider_env()
    if image_provider_env:
        return ImageProvider(image_provider_env)
    return None


def get_image_provider_api_key() -> str:
    return settings.PEXELS_API_KEY
