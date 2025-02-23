import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import OWNER_ID, WELCOME_MESSAGE, MOVIE_CATEGORIES
from database import MovieDatabase
from utils import (
    create_movie_keyboard,
    create_category_keyboard,
    validate_image_url,
    format_movie_details,
    create_main_menu_keyboard
)

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
    'MOVIE_CATEGORIES': 'MOVIE_CATEGORIES',
    'AWAITING_SEARCH': 'AWAITING_SEARCH'
}

db = MovieDatabase()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info("User %s started the bot", update.effective_user.id)
    keyboard = create_main_menu_keyboard()
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

    keyboard = [[
        InlineKeyboardButton(text="⬇️ Download", url=movie['download_link'])
    ]]

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
    logger.info("Processing movie name from user %s", update.effective_user.id)
    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END

    if not update.message or not update.message.text:
        logger.warning("Received update without message text")
        return STATES['MOVIE_NAME']  # Stay in the same state

    if not isinstance(update.message.text, str):
        logger.warning("Invalid message type received")
        return STATES['MOVIE_NAME']  # Stay in the same state

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
    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END
    logger.info("Processing movie poster from user %s", update.effective_user.id)
    poster_url = update.message.text
    if not validate_image_url(poster_url):
        await update.message.reply_text("Invalid image URL. Please try again:")
        return STATES['MOVIE_POSTER']

    context.user_data['poster_url'] = poster_url
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
    await update.message.reply_text("Please enter the download link:", reply_markup=InlineKeyboardMarkup(keyboard))
    return STATES['MOVIE_LINK']

async def process_movie_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie download link"""
    if update.callback_query and update.callback_query.data == "cancel":
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Movie addition cancelled.")
        return ConversationHandler.END
    logger.info("Processing movie link from user %s", update.effective_user.id)
    context.user_data['download_link'] = update.message.text
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