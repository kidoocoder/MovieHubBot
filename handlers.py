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

# Conversation states
MOVIE_NAME, MOVIE_DESC, MOVIE_POSTER, MOVIE_LINK, MOVIE_CATEGORIES = range(5)

db = MovieDatabase()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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
    await query.answer()
    await query.message.reply_text(
        "Please enter the movie name you want to search:"
    )
    return "awaiting_search"

async def process_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie search query"""
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
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("This command is only for the bot owner!")
        return ConversationHandler.END

    await update.message.reply_text("Please enter the movie name:")
    return MOVIE_NAME

async def process_movie_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie name"""
    context.user_data['movie_name'] = update.message.text
    await update.message.reply_text("Please enter the movie description:")
    return MOVIE_DESC

async def process_movie_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie description"""
    context.user_data['movie_description'] = update.message.text
    await update.message.reply_text("Please enter the movie poster URL:")
    return MOVIE_POSTER

async def process_movie_poster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie poster"""
    poster_url = update.message.text
    if not validate_image_url(poster_url):
        await update.message.reply_text("Invalid image URL. Please try again:")
        return MOVIE_POSTER

    context.user_data['poster_url'] = poster_url
    await update.message.reply_text("Please enter the download link:")
    return MOVIE_LINK

async def process_movie_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie download link"""
    context.user_data['download_link'] = update.message.text
    keyboard = create_category_keyboard()
    await update.message.reply_text(
        "Select movie categories:",
        reply_markup=keyboard
    )
    return MOVIE_CATEGORIES

async def process_movie_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process movie categories and save movie"""
    query = update.callback_query
    await query.answer()

    selected_category = query.data.split('_')[1]
    if 'categories' not in context.user_data:
        context.user_data['categories'] = []

    context.user_data['categories'].append(selected_category)

    movie_data = {
        'name': context.user_data['movie_name'],
        'description': context.user_data['movie_description'],
        'poster_url': context.user_data['poster_url'],
        'download_link': context.user_data['download_link'],
        'categories': context.user_data['categories']
    }

    db.add_movie(movie_data)
    await query.message.reply_text("Movie added successfully!")
    return ConversationHandler.END