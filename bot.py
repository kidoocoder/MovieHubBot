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
    delete_movie,
    process_movie_name,
    process_movie_description,
    process_movie_poster,
    process_movie_link,
    process_movie_categories,
    process_search,
    confirm_delete_movie,
    process_delete_confirmation,
    process_telegram_link,
    help_command,
    command_search,
    STATES,
    list_all_movies,
    hide_movie,
    show_movie,
    handle_visibility_callback,
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
            STATES['TELEGRAM_LINK']: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_telegram_link),
                CallbackQueryHandler(process_telegram_link, pattern='^cancel$')
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

    # Add search conversation handler with both command and button entry points
    search_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(search_movie, pattern='^search$'),
            CommandHandler('search', command_search)
        ],
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
                CallbackQueryHandler(confirm_delete_movie, pattern=r'^movie_\d+$'),
                CallbackQueryHandler(process_delete_confirmation, pattern=r'^confirm_delete_\d+$'),
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
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(movie_conv_handler)
    application.add_handler(search_conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(CallbackQueryHandler(owner_info, pattern='^owner_info$'))
    application.add_handler(CallbackQueryHandler(recommend_movies, pattern='^recommend$'))
    application.add_handler(CallbackQueryHandler(show_movie_details, pattern='^movie_'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    application.add_handler(CommandHandler('listmovies', list_all_movies))
    application.add_handler(CommandHandler('hide', hide_movie))
    application.add_handler(CommandHandler('show', show_movie))
    application.add_handler(CallbackQueryHandler(handle_visibility_callback, pattern='^(hide|show)_\d+$'))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()