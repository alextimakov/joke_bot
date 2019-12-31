import app.config as config
import app.mongo_worker as mg
import app.utils as utils
from app.scripts import *
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext
from telegram.error import TelegramError, Unauthorized
import logging.config
from bson.objectid import ObjectId

# initialize updater
updater = Updater(token=config.token, use_context=True)
dp = updater.dispatcher

# set up logging
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logger.config')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    # get tg_id
    # check if in whitelist
    # if yes then go to menu
    return 1


def menu(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("Menu by user {}.".format(user.id))
    try:
        tg_id = utils.select_user_attribute(user.id, 'tg_id')
        if tg_id and tg_id in config.whitelist:
            # send keyboard
            return mg.States.MENU
        else:
            bot.send_message(user.id, text='Отказано в доступе')
    except AttributeError:
        bot.send_message(chat_id=user.id, text=access_denied['RU'])
        return mg.States.START




def set_state(update: Update, context: CallbackContext):
    user = update.message.from_user
    utils.assign_state(user.id, mg.States.SET_STATE.value)
    if update.message.text == new_comment['RU']:
        enter_new_comment(update, context)
        return mg.States.NO_ATTACH
    elif update.message.text == predict_menu['RU']:
        predict(update, context)
        return mg.States.EDIT_MODERATOR
    elif update.message.text == reset_menu['RU']:
        reset_comments(update, context)
        return mg.States.MENU
    else:
        utils.assign_state(user.id, mg.States.MENU.value)
        return mg.States.MENU


def enter_new_comment(update: Update, context: CallbackContext):
    # send message with request to send new comment
    return 1


def comment_entered(update: Update, context: CallbackContext):
    # read comment
    # append it to users' comments
    return 1


def predict(update: Update, context: CallbackContext):
    # call all users' comments
    # check if any comments exists
    # if true send keyboard with model selection
    return 1


def select_model(update: Update, context: CallbackContext):
    # catch result of model selection
    # read selected model
    # upload them to model
    # send back model result
    # back to menu
    return 1


def reset_comments(update: Update, context: CallbackContext):
    return 1


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("User {} canceled".format(user.id))
    utils.assign_state(user.id, mg.States.START.value)
    bot.send_message(chat_id=user.id, text=cancel_text['RU'], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def log_error(update: Update, context: CallbackContext):
    error = context.error
    bot = context.bot
    logger.warning('Update "%s" caused error "%s"', update, error)
    try:
        user = update.message.from_user
        keyboard = [[restart['RU']]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        bot.send_message(chat_id=user.id, text=error_text['RU'], reply_markup=reply_markup)
    except AttributeError:
        logger.warning('System mistake')
        menu(update, context)
    return mg.States.START


def main():
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('menu', menu),
                      MessageHandler(Filters.regex('^({})$'.format(back2menu['RU'])), menu)],

        states={
            mg.States.MENU: [CommandHandler('menu', menu),
                             MessageHandler(Filters.regex('^({})$'.format(back2menu['RU'])), menu)],

            mg.States.SET_STATE: [MessageHandler(Filters.regex('^({}|{}|{})$'.format(
                    new_comment['RU'], predict_menu['RU'], reset_menu['RU'])), set_state)],

            mg.States.

        },

        fallbacks=[MessageHandler(Filters.regex('^({})$'.format(restart['RU'])), cancel),
                   CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conversation_handler)

    # Log all errors:
    dp.add_error_handler(log_error)


if __name__ == '__main__':
    main()
    updater.start_polling(clean=False)
