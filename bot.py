import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from config import BOT_TOKEN
from handlers import (
    start,
    owner_info,
    search_movie,
    recommend_movies,
    show_movie_details,
    add_movie,
    process_movie_name,
    process_movie_description,
    process_movie_poster,
    process_movie_link,
    process_movie_categories,
    process_search,
    STATES
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for movie addition
    movie_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addmovie', add_movie)],
        states={
            STATES['MOVIE_NAME']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_name)
            ],
            STATES['MOVIE_DESC']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_description)
            ],
            STATES['MOVIE_POSTER']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_poster)
            ],
            STATES['MOVIE_LINK']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_link)
            ],
            STATES['MOVIE_CATEGORIES']: [
                CallbackQueryHandler(process_movie_categories, pattern=r'^category_')
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
            CallbackQueryHandler(start, pattern='^cancel$')
        ],
        per_user=True,
        allow_reentry=True,
        name="movie_conversation"
    )

    # Add search conversation handler
    search_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(search_movie, pattern='^search$')],
        states={
            STATES['AWAITING_SEARCH']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_search)
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
            CallbackQueryHandler(start, pattern='^cancel$')
        ],
        per_user=True,
        allow_reentry=True,
        name="search_conversation"
    )

    # Add handlers in specific order
    application.add_handler(CommandHandler('start', start))
    application.add_handler(movie_conv_handler)  # Movie handler first
    application.add_handler(search_conv_handler)  # Search handler second
    application.add_handler(CallbackQueryHandler(owner_info, pattern='^owner_info$'))
    application.add_handler(CallbackQueryHandler(recommend_movies, pattern='^recommend$'))
    application.add_handler(CallbackQueryHandler(show_movie_details, pattern='^movie_'))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()