import os

# Bot configuration settings
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Get token from environment variable
OWNER_ID = int(os.environ.get('OWNER_ID', '123456789'))  # Replace with actual owner's Telegram ID
SUPPORT_CHANNEL = "https://t.me/your_support_channel"  # Replace with actual support channel

# Welcome image URL - A default movie-themed image
WELCOME_IMAGE_URL = "https://files.catbox.moe/v3q694.jpg"  # Default cinema/movie themed image

# Welcome message
WELCOME_MESSAGE = """
🎬 *Welcome to Movie Database Bot!*
Your one-stop destination for movies.

Use the buttons below to:
• Browse movies
• Search for specific titles
• Get recommendations
• Contact support
"""

# Categories for movies
MOVIE_CATEGORIES = [
    "Action", "Comedy", "Drama", "Horror", 
    "Romance", "Sci-Fi", "Thriller", "Documentary"
]