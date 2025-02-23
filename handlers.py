import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import (
    OWNER_ID, 
    WELCOME_MESSAGE, 
    MOVIE_CATEGORIES,
    WELCOME_IMAGE_URL
)
from database import MovieDatabase
from utils import (
    create_movie_keyboard,
    create_category_keyboard,
    validate_image_url,
    format_movie_details,
    create_main_menu_keyboard
)
from typing import List

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states as string constants for clarity
STATES = {
    'MOVIE_NAME': 'MOVIE_NAME',
    'MOVIE_DESC': 'MOVIE_DESC',
    'MOVIE_POSTER': 'MOVIE_POSTER',
    'MOVIE_LINK': 'MOVIE_LINK',
    'TELEGRAM_LINK': 'TELEGRAM_LINK',  # New state
    'MOVIE_CATEGORIES': 'MOVIE_CATEGORIES',
    'AWAITING_SEARCH': 'AWAITING_SEARCH',
    'DELETE_CONFIRMATION': 'DELETE_CONFIRMATION'
}

db = MovieDatabase()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info("User %s started the bot", update.effective_user.id)
    keyboard = create_main_menu_keyboard()

    # First send the welcome image
    try:
        await update.message.reply_photo(
            photo=WELCOME_IMAGE_URL,
            caption=WELCOME_MESSAGE,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Failed to send welcome image: {str(e)}")
        # Fallback to text-only message if image fails
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=keyboard
        )

async def owner_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle owner info button"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        f"Bot Owner ID: {OWNER_ID}\n"
        "Contact owner for any queries."
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle movie search"""
    query = update.callback_query
    logger.info("User %s initiated search", update.effective_user.id)
    await query.answer()
    await query.message.reply_text(
        "Please enter the movie name you want to search:"
    )
    return STATES['AWAITING_SEARCH']

async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie search query"""
    logger.info("Processing search query from user %s", update.effective_user.id)
    search_query = update.message.text
    movies = db.search_movie(search_query)

    if not movies:
        await update.message.reply_text(
            "I don't have this movie, please wait 24 hours for it to be uploaded."
        )
        return ConversationHandler.END

    keyboard = create_movie_keyboard(movies)
    await update.message.reply_text(
        "Here are the matching movies:",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def recommend_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle movie recommendations"""
    query = update.callback_query
    await query.answer()

    movies = db.get_all_movies()
    if not movies:
        await query.message.reply_text("No movies available yet!")
        return

    keyboard = create_movie_keyboard(movies)
    await query.message.reply_text(
        "Here are all available movies:",
        reply_markup=keyboard
    )

async def show_movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show details for selected movie"""
    query = update.callback_query
    await query.answer()

    movie_id = int(query.data.split('_')[1])
    movie = db.get_movie(movie_id)

    if not movie:
        await query.message.reply_text("Movie not found!")
        return

    keyboard = [
        [InlineKeyboardButton(text="⬇️ Direct Download", url=movie['download_link'])],
        [InlineKeyboardButton(text="📢 Download from Channel", url=movie['telegram_link'])]
    ]

    try:
        # Send photo with caption and download buttons
        await query.message.reply_photo(
            photo=movie['poster_url'],
            caption=format_movie_details(movie),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Failed to send movie poster: {str(e)}")
        # Fallback to text-only message if image fails
        await query.message.reply_text(
            format_movie_details(movie),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

# Owner-only commands
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start movie addition process"""
    user_id = update.effective_user.id
    logger.info("User %s attempting to add movie", user_id)

    if user_id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", user_id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    context.user_data.clear()  # Clear any existing conversation data
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text(
        "Please enter the movie name:\n\nOr click Cancel to abort.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STATES['MOVIE_NAME']

async def process_movie_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie name"""
    user_id = update.effective_user.id
    logger.info("Processing movie name from user %s", user_id)

    if user_id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", user_id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    if not update.message or not update.message.text:
        logger.warning("Received update without message text")
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        await update.effective_message.reply_text(
            "Please enter a valid movie name:\n\nOr click Cancel to abort.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return STATES['MOVIE_NAME']

    logger.info("Movie name received: %s", update.message.text)
    context.user_data['movie_name'] = update.message.text
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text(
        "Please enter the movie description:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info("Transitioning to MOVIE_DESC state")
    return STATES['MOVIE_DESC']

async def process_movie_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie description"""
    if update.effective_user.id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", update.effective_user.id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    if not update.message or not update.message.text:
        logger.warning("Received update without message text")
        return STATES['MOVIE_DESC']  # Stay in the same state

    if 'movie_name' not in context.user_data:
        logger.error("Movie name not found in context")
        await update.message.reply_text("Something went wrong. Please start over with /addmovie")
        return ConversationHandler.END

    logger.info("Movie description received for movie: %s", context.user_data.get('movie_name', 'Unknown'))
    context.user_data['movie_description'] = update.message.text
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text(
        "Please enter the movie poster URL:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    logger.info("Transitioning to MOVIE_POSTER state")
    return STATES['MOVIE_POSTER']

async def process_movie_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie poster"""
    if update.effective_user.id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", update.effective_user.id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    logger.info("Processing movie poster from user %s", update.effective_user.id)
    poster_url = update.message.text
    logger.info("Validating poster URL: %s", poster_url)

    if not validate_image_url(poster_url):
        logger.warning("Invalid image URL provided: %s", poster_url)
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        await update.message.reply_text(
            "Invalid image URL. Please make sure:\n"
            "1. The URL is a direct link to an image (ends with .jpg, .png, etc.)\n"
            "2. The image is publicly accessible\n"
            "3. The URL starts with http:// or https://\n\n"
            "Please try again:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return STATES['MOVIE_POSTER']

    context.user_data['poster_url'] = poster_url
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text(
        "Please enter the download link:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STATES['MOVIE_LINK']

async def process_movie_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie download link"""
    if update.effective_user.id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", update.effective_user.id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    logger.info("Processing movie link from user %s", update.effective_user.id)
    context.user_data['download_link'] = update.message.text
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text(
        "Please enter the Telegram channel link where users can also download the movie:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STATES['TELEGRAM_LINK']

async def process_telegram_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process telegram channel link"""
    if update.effective_user.id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to add movie", update.effective_user.id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    logger.info("Processing telegram link from user %s", update.effective_user.id)
    context.user_data['telegram_link'] = update.message.text
    keyboard = create_category_keyboard()
    await update.message.reply_text(
        "Select movie categories:",
        reply_markup=keyboard
    )
    return STATES['MOVIE_CATEGORIES']

async def process_movie_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie categories and save movie"""
    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END
    query = update.callback_query
    await query.answer()
    logger.info("Processing movie categories from user %s", update.effective_user.id)

    selected_category = query.data.split('_')[1]
    if 'categories' not in context.user_data:
        context.user_data['categories'] = []

    if selected_category not in context.user_data['categories']:
        context.user_data['categories'].append(selected_category)

    movie_data = {
        'name': context.user_data['movie_name'],
        'description': context.user_data['movie_description'],
        'poster_url': context.user_data['poster_url'],
        'download_link': context.user_data['download_link'],
        'telegram_link': context.user_data['telegram_link'],  # Include telegram link
        'categories': context.user_data['categories']
    }

    try:
        db.add_movie(movie_data)
        logger.info("Successfully added movie: %s", movie_data['name'])
        await query.message.reply_text("Movie added successfully!")
    except Exception as e:
        logger.error("Failed to add movie: %s", str(e))
        await query.message.reply_text("Failed to add movie. Please try again.")

    context.user_data.clear()  # Clear the user data after completion
    return ConversationHandler.END


async def delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start movie deletion process"""
    user_id = update.effective_user.id
    logger.info("User %s attempting to delete movie", user_id)

    if user_id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to delete movie", user_id)
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    # Get all movies and create keyboard
    movies = db.get_all_movies()
    if not movies:
        await update.message.reply_text("No movies available to delete!")
        return ConversationHandler.END

    keyboard = create_movie_keyboard(movies)
    await update.message.reply_text(
        "Select the movie you want to delete:",
        reply_markup=keyboard
    )
    return STATES['DELETE_CONFIRMATION']

async def confirm_delete_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie deletion confirmation"""
    if update.effective_user.id != OWNER_ID:
        logger.warning("Unauthorized user %s tried to delete movie", update.effective_user.id)
        await update.callback_query.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    movie_id = int(query.data.split('_')[1])
    movie = db.get_movie(movie_id)

    if not movie:
        await query.message.reply_text("Movie not found!")
        return ConversationHandler.END

    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, delete", callback_data=f"confirm_delete_{movie_id}"),
            InlineKeyboardButton("❌ No, cancel", callback_data="cancel_delete")
        ]
    ]
    await query.message.reply_text(
        f"Are you sure you want to delete '{movie['name']}'?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STATES['DELETE_CONFIRMATION']

async def process_delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the final deletion confirmation"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_delete":
        await query.message.reply_text("Movie deletion cancelled.")
        return ConversationHandler.END

    try:
        # Extract movie ID from confirm_delete_X pattern
        movie_id = int(query.data.split('_')[2])  # Changed from [1] to [2] to get the actual ID
        if db.delete_movie(movie_id):
            await query.message.reply_text("Movie successfully deleted!")
        else:
            await query.message.reply_text("Failed to delete movie. Please try again.")
    except (ValueError, IndexError) as e:
        logger.error(f"Error processing delete confirmation: {str(e)}")
        await query.message.reply_text("Something went wrong. Please try again.")

    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command and help button"""
    # Base help text for all users
    help_text = """
🎬 *Movie Database Bot Commands*

*Available Commands:*
/start - Start the bot and show main menu
/search - Search for a movie
/help - Show this help message

*Available Buttons:*
• 🔍 Search Movie - Search for movies by name
• 🎬 Recommend Movies - Browse all available movies
• 👤 Owner Info - Show bot owner information
• 💬 Support Channel - Join our support channel
• ❓ Help - Show this help message
    """

    # Add owner-only commands if the user is the owner
    if update.effective_user.id == OWNER_ID:
        owner_help = """

*Owner-Only Commands:*
/addmovie - Add a new movie
/delmovie - Delete an existing movie
/listmovies - List all movies (including hidden)
/togglemovie [id] - Toggle movie visibility
        """
        help_text += owner_help

    await update.effective_message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def command_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    logger.info("User %s initiated search via command", update.effective_user.id)
    await update.message.reply_text(
        "Please enter the movie name you want to search:"
    )
    return STATES['AWAITING_SEARCH']

async def list_all_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Owner command to list all movies including hidden ones.
    Command: /listmovies
    """
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("This command is only for the bot owner!")
        return

    movies = db.get_all_movies(include_hidden=True)
    if not movies:
        await update.message.reply_text("No movies in database!")
        return

    # Create a formatted list of movies with visibility status
    movie_list = "*📽 All Movies (Including Hidden):*\n\n"
    for movie in movies:
        status = "🟢" if movie['visible'] else "🔴"
        movie_list += f"{status} *{movie['name']}*\n"
        movie_list += f"ID: `{movie['id']}`\n"
        movie_list += f"Categories: {', '.join(movie['categories'])}\n\n"

    # Split message if it's too long
    if len(movie_list) > 4096:
        chunks = [movie_list[i:i+4096] for i in range(0, len(movie_list), 4096)]
        for chunk in chunks:
            await update.message.reply_text(
                chunk,
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        await update.message.reply_text(
            movie_list,
            parse_mode=ParseMode.MARKDOWN
        )

    # Add instructions for toggling visibility
    await update.message.reply_text(
        "To toggle movie visibility, use:\n"
        "/togglemovie [movie_id]\n\n"
        "🟢 = Visible to users\n"
        "🔴 = Hidden from users"
    )

async def toggle_movie_visibility(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Owner command to toggle movie visibility.
    Command: /togglemovie <movie_id>
    """
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("This command is only for the bot owner!")
        return

    try:
        movie_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Please provide a valid movie ID.\n"
            "Usage: /togglemovie [movie_id]"
        )
        return

    movie = db.get_movie(movie_id)
    if not movie:
        await update.message.reply_text("Movie not found!")
        return

    if db.toggle_movie_visibility(movie_id):
        new_status = "visible" if db.get_movie(movie_id)['visible'] else "hidden"
        await update.message.reply_text(
            f"Successfully set movie '{movie['name']}' to {new_status}!"
        )
    else:
        await update.message.reply_text("Failed to toggle movie visibility!")