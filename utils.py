from typing import List
import requests
from PIL import Image
from io import BytesIO
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram._utils.types import ReplyMarkup
import logging
logger = logging.getLogger(__name__)

def create_movie_keyboard(movies: List[dict]) -> ReplyMarkup:
    """Create keyboard markup for movie list"""
    keyboard = []
    for movie in movies:
        keyboard.append([
            InlineKeyboardButton(
                text=movie['name'],
                callback_data=f"movie_{movie['id']}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)

def create_category_keyboard() -> ReplyMarkup:
    """Create keyboard markup for categories"""
    from config import MOVIE_CATEGORIES
    keyboard = []
    row = []
    for i, category in enumerate(MOVIE_CATEGORIES):
        row.append(InlineKeyboardButton(
            text=category,
            callback_data=f"category_{category}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def validate_image_url(url: str) -> bool:
    """Validate if URL points to an image"""
    try:
        # Use a longer timeout for slower servers
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        if response.status_code != 200:
            logger.warning(f"Failed to fetch image URL {url}. Status code: {response.status_code}")
            return False

        # Try to open as image regardless of content type
        try:
            img = Image.open(BytesIO(response.content))
            img.verify()  # Verify it's actually an image
            return True
        except Exception as e:
            logger.warning(f"Failed to verify image format for URL {url}. Error: {str(e)}")
            return False

    except requests.RequestException as e:
        logger.warning(f"Request failed for URL {url}. Error: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"Failed to validate image URL {url}. Error: {str(e)}")
        return False

def format_movie_details(movie: dict) -> str:
    """Format movie details for display"""
    return f"""
🎬 *{movie['name']}*

📝 *Description:*
{movie['description']}

🎭 *Categories:* {', '.join(movie['categories'])}
    """

def create_main_menu_keyboard() -> ReplyMarkup:
    """Create main menu keyboard"""
    from config import SUPPORT_CHANNEL
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Owner Info", callback_data="owner_info"),
            InlineKeyboardButton(text="💬 Support Channel", url=SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton(text="🎬 Recommend Movies", callback_data="recommend"),
            InlineKeyboardButton(text="🔍 Search Movie", callback_data="search")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)