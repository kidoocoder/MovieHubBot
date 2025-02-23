import os

# Bot configuration settings
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Get token from environment variable
OWNER_ID = int(os.environ.get('OWNER_ID', '123456789'))  # Replace with actual owner's Telegram ID
SUPPORT_CHANNEL = "https://t.me/your_support_channel"  # Replace with actual support channel
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID')  # Log group for movie requests

# Welcome image URL - A default movie-themed image
WELCOME_IMAGE_URL = "https://files.catbox.moe/v3q694.jpg"  # Default cinema/movie themed image

# Welcome message with enhanced formatting
WELCOME_MESSAGE = """
🎬 *Welcome to Movie Database Bot!* 🎥
Your personal movie companion 🌟

✨ *What can I do?*
• 🎯 Browse movies by category
• 🔍 Search for specific titles
• 🎲 Get personalized recommendations
• 📥 Access direct download links
• 📢 Join our movie channel

🚀 *Get Started:*
Use the buttons below to explore!
"""

# Categories for movies with emojis
MOVIE_CATEGORIES = [
    "🎬 Action", "😄 Comedy", "🎭 Drama", "👻 Horror", 
    "💝 Romance", "🚀 Sci-Fi", "🔍 Thriller", "📚 Documentary"
]