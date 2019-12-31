import sys, os
sys.path.append(os.path.abspath('.'))

import app.config as config
import app.mongo_worker as mg
import app.utils as utils
from app.scripts import *
import os
import pickle
import numpy as np
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext
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
    user = update.message.from_user.id
    bot = context.bot
    if utils.select_user_attribute(user, 'tg_id'):
        if not utils.select_user_attribute(user, 'state'):
            utils.assign_state(user, mg.States.START.value)
        state = utils.select_user_attribute(user, 'state')
        logger.info("User {} in state {}".format(user, int(state)))
        if update.message.text == new_comment['RU']:
            enter_new_comment(update, context)
            return mg.States.NO_ATTACH
        elif update.message.text == predict_menu['RU']:
            select_model(update, context)
            return mg.States.EDIT_MODERATOR
        elif update.message.text == reset_menu['RU']:
            reset_comments(update, context)
            return mg.States.MENU
        else:
            reply_markup = ReplyKeyboardMarkup([[back2menu['RU']]], one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(chat_id=user, text=state_menu['RU'], reply_markup=reply_markup)
            return mg.States.MENU
    else:
        bot.send_message(chat_id=user, text=access_denied['RU'])
        return mg.States.START


def menu(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("Menu by user {}.".format(user.id))
    try:
        tg_id = utils.select_user_attribute(user.id, 'tg_id')
        if tg_id:
            keyboard = [[new_comment['RU']], [predict_menu['RU']], [reset_menu['RU']]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(chat_id=user.id, text=menu_text['RU'], reply_markup=reply_markup)
            utils.assign_state(user.id, mg.States.MENU.value)
            return mg.States.SET_STATE
        else:
            bot.send_message(user.id, text=access_denied['RU'])
    except AttributeError:
        bot.send_message(chat_id=user.id, text=access_denied['RU'])
        return mg.States.START


def set_state(update: Update, context: CallbackContext):
    user = update.message.from_user
    utils.assign_state(user.id, mg.States.SET_STATE.value)
    if update.message.text == new_comment['RU']:
        enter_new_comment(update, context)
        return mg.States.ADD_COMMENT
    elif update.message.text == predict_menu['RU']:
        select_model(update, context)
        return mg.States.MAKE_PREDICT
    elif update.message.text == reset_menu['RU']:
        reset_comments(update, context)
        return mg.States.MENU
    else:
        utils.assign_state(user.id, mg.States.MENU.value)
        return mg.States.MENU


def enter_new_comment(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("News by user {}".format(user.id))
    bot.send_message(chat_id=user.id, text=add_comment['RU'])
    return mg.States.ADD_COMMENT


def comment_entered(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    text = update.message.text
    author_id = utils.select_user_attribute(user.id, '_id')
    logger.info("Comment added {}".format(user.id))
    utils.assign_state(user.id, mg.States.ADD_COMMENT.value)
    if mg.select_one('comments', 'comment', **{'author_id': author_id}):
        mg.add_to_array('comments', '_id', author_id, **{'comment': text})
    else:
        mg.insert('comments', **{'author_id': author_id, 'comment': text})
    bot.send_message(chat_id=user.id, text=comment_added['RU'])
    return mg.States.MENU


def select_model(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("Select model by user {}.".format(user.id))
    author_id = utils.select_user_attribute(user.id, '_id')
    comments = mg.select_many('comments', 'comment', **{'author_id': ObjectId(author_id)})
    if any(comments):
        reply_markup = ReplyKeyboardMarkup([[model_1['RU'], model_2['RU']],
                                            [model_3['RU'], model_4['RU']]],
                                           one_time_keyboard=True, resize_keyboard=True)
        bot.send_message(chat_id=user.id, text=choose_model['RU'], reply_markup=reply_markup)
        return mg.States.MAKE_PREDICT
    else:
        reply_markup = ReplyKeyboardMarkup([[back2menu['RU']]], one_time_keyboard=True, resize_keyboard=True)
        bot.send_message(chat_id=user.id, text=no_comments['RU'], reply_markup=reply_markup)
        return mg.States.MENU


def make_prediction(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("Make prediction by user {}.".format(user.id))
    utils.assign_state(user.id, mg.States.MAKE_PREDICT.value)
    author_id = utils.select_user_attribute(user.id, '_id')
    selected_model = 'sasha' + '_model.pkl'
    with open(selected_model, 'rb') as fid:
        model = pickle.load(fid)
    user_comments = mg.select_many('comments', 'comment', **{'author_id': ObjectId(author_id)})
    user_comments = np.array(user_comments).reshape(len(user_comments),)
    result_transformer = 'sasha' + '_transformer.pkl'
    with open(result_transformer, 'rb') as bt:
        transformer = pickle.load(bt)
    result_encoder = 'sasha' + '_labelencoder.pkl'
    with open(result_encoder, 'rb') as le:
        encoder = pickle.load(le)
    model_result = encoder.inverse_transform(model.predict(transformer.transform(user_comments)))
    model_result = max(set(list(model_result)), key=list(model_result).count)
    model_result = 'Скорее всего, Вы - {RESULT}'.format(RESULT=model_result)
    mg.insert('predictions', **{'author_id': author_id, 'model': selected_model,
                                'model_result': model_result})
    reply_markup = ReplyKeyboardMarkup([[back2menu['RU']]], one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(chat_id=user.id, text=model_result, reply_markup=reply_markup)
    return mg.States.MENU


def reset_comments(update: Update, context: CallbackContext):
    user = update.message.from_user
    bot = context.bot
    logger.info("User {} reset all comments".format(user.id))
    utils.assign_state(user.id, mg.States.RESET_ALL.value)
    reply_markup = ReplyKeyboardMarkup([[back2menu['RU']]], one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(chat_id=user.id, text=all_reset['RU'], reply_markup=reply_markup)
    return mg.States.MENU


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

            mg.States.ADD_COMMENT: [MessageHandler(Filters.text, comment_entered)],

            mg.States.MAKE_PREDICT: [MessageHandler(Filters.text, make_prediction)],

            mg.States.RESET_ALL: [CommandHandler('reset_all', reset_comments)]

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
