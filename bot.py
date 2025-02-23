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
    delete_movie,  # New import
    process_movie_name,
    process_movie_description,
    process_movie_poster,
    process_movie_link,
    process_movie_categories,
    process_search,
    confirm_delete_movie,  # New import
    process_delete_confirmation,  # New import
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
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_name),
                CallbackQueryHandler(process_movie_name, pattern='^cancel$')
            ],
            STATES['MOVIE_DESC']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_description),
                CallbackQueryHandler(process_movie_description, pattern='^cancel$')
            ],
            STATES['MOVIE_POSTER']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_poster),
                CallbackQueryHandler(process_movie_poster, pattern='^cancel$')
            ],
            STATES['MOVIE_LINK']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_link),
                CallbackQueryHandler(process_movie_link, pattern='^cancel$')
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

    # Add delete movie conversation handler
    delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delmovie', delete_movie)],
        states={
            STATES['DELETE_CONFIRMATION']: [
                CallbackQueryHandler(confirm_delete_movie, pattern=r'^movie_'),
                CallbackQueryHandler(process_delete_confirmation, pattern=r'^confirm_delete_'),
                CallbackQueryHandler(process_delete_confirmation, pattern='^cancel_delete$')
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
            CallbackQueryHandler(start, pattern='^cancel$')
        ],
        per_user=True,
        allow_reentry=True,
        name="delete_conversation"
    )

    # Add handlers in specific order - movie handler BEFORE search handler
    application.add_handler(CommandHandler('start', start))
    application.add_handler(movie_conv_handler)  
    application.add_handler(search_conv_handler)  
    application.add_handler(delete_conv_handler)  # Add the new handler
    application.add_handler(CallbackQueryHandler(owner_info, pattern='^owner_info$'))
    application.add_handler(CallbackQueryHandler(recommend_movies, pattern='^recommend$'))
    application.add_handler(CallbackQueryHandler(show_movie_details, pattern='^movie_'))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()