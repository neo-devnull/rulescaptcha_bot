from ..config import (BOT_USERNAME, RULES_URI_HUMAN, ENABLE_WELCOME_MSG,
                      WELCOME_MSG)
from telegram.ext import MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from ..lib.common import db, mute_perms, get_mention
from tinydb import Query


def handle(update, ctx):
    # Ignore if self
    if update.message.new_chat_members[0].username == BOT_USERNAME:
        return None

    group_id = update.effective_chat.id
    user_id = update.message.new_chat_members[0].id
    msgid = None

    update.message.bot.restrict_chat_member(
        chat_id=group_id,
        user_id=user_id,
        permissions=mute_perms
    )

    if ENABLE_WELCOME_MSG:

        url = f't.me/{BOT_USERNAME}?start={update.effective_chat.id}'
        keyboard = [
            [
                InlineKeyboardButton(text='Click to unmute', url=url)
            ],
            [
                InlineKeyboardButton(text='Rules', url=RULES_URI_HUMAN)
            ]
        ]
        user_mention = get_mention(update.effective_user)
        msgid = update.message.bot.send_message(
            chat_id=group_id,
            text=WELCOME_MSG.format(username=user_mention),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MARKDOWN"
        ).message_id

    # Insert into database
    User = Query()
    db.upsert(
        {
            "group_id": group_id,
            "user_id": user_id,
            "message_id": msg.message_id
        },
        (
            (User.group_id == group_id) & (User.user_id == user_id)
        )
    )


handler = MessageHandler(Filters.status_update.new_chat_members, handle)
