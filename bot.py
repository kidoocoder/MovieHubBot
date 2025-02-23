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
    process_search
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for movie addition
    movie_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addmovie', add_movie)],
        states={
            'MOVIE_NAME': [MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_name)],
            'MOVIE_DESC': [MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_description)],
            'MOVIE_POSTER': [MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_poster)],
            'MOVIE_LINK': [MessageHandler(filters.TEXT & ~filters.COMMAND, process_movie_link)],
            'MOVIE_CATEGORIES': [CallbackQueryHandler(process_movie_categories, pattern=r'^category_')]
        },
        fallbacks=[],
        per_user=True,
        name="movie_conversation"
    )

    # Add search conversation handler
    search_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(search_movie, pattern='^search$')],
        states={
            'awaiting_search': [MessageHandler(filters.TEXT & ~filters.COMMAND, process_search)]
        },
        fallbacks=[],
        per_user=True,
        name="search_conversation"
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(movie_conv_handler)
    application.add_handler(search_conv_handler)
    application.add_handler(CallbackQueryHandler(owner_info, pattern='^owner_info$'))
    application.add_handler(CallbackQueryHandler(recommend_movies, pattern='^recommend$'))
    application.add_handler(CallbackQueryHandler(show_movie_details, pattern='^movie_'))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()