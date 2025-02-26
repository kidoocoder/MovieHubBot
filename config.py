import os

# Bot configuration settings
BOT_TOKEN = os.environ.get('7264247499:AAHZ1F3D5oPLOtLVomRtjrh1zMeOsf2kRbQ')  # Get token from environment variable
OWNER_ID = int(os.environ.get('OWNER_ID', '7799390858'))  # Replace with actual owner's Telegram ID
SUPPORT_CHANNEL = "https://t.me/Guppppp_Shuppppp"  # Replace with actual support channel
LOG_GROUP_ID = os.environ.get('-4684890007')  # Log group for movie requests
DATABASE_URL = "postgres://kfcdtwea:jxgqtvc1ji7lSMjAhUp0QbxrE8Ut0t7N@fanny.db.elephantsql.com/kfcdtwea"

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
