from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher, Defaults, CallbackQueryHandler, ChatJoinRequestHandler, PreCheckoutQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, LabeledPrice

from constants import *

from models import group, user, transaction, membership

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)


def waiting_message_wrapper(func):
    def wrapper(update, context):
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Please wait...',
        )
        error = None
        print('calling function')
        try:
            func(update, context)
        except Exception as e:
            error = e
            print(e)
        context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
        )
        if error:
            raise error

    return wrapper


def verify_payment(update, context):
    cmd = update.message.text.split(' ')[1]
    transaction_details = transaction.get_transaction(cmd)
    if not transaction_details:
        update.message.reply_text('Could not find this transaction')
        return

    verify_chapa = chapa.verify(cmd)
    print(verify_chapa)
    if verify_chapa.get('status') == 'success' and verify_chapa['data']['status'] == 'success':
        transaction.update_transaction(cmd, status='success')
        membership.create_membership(
            user=transaction_details.user,
            group=transaction_details.group,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=transaction_details.group.duration),
            status='active',
            transaction=transaction_details,
        )
        keyboard = [[
            InlineKeyboardButton('Join', url=INVITE_LINK)
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(INVITE_MESSAGE.format(
            link=INVITE_LINK),
            parse_mode='HTML',
            reply_markup=reply_markup,
        )

    else:
        update.message.reply_text(PAYMENT_FAILED_MESSAGE)

    return


def chat_join_request(update, context):
    bot = context.bot
    query = update.chat_join_request
    user_detail = user.get_user(query.from_user.id)
    if not user_detail:
        tg_user = query.from_user
        user.create_user(
            tg_user.id, tg_user.first_name, tg_user.last_name, tg_user.username
        )

    group_detail = group.get_group(query.chat.id)

    have_valid_membership = membership.check_valid_membership(
        user_detail, group_detail)
    if have_valid_membership:
        bot.approve_chat_join_request(query.chat.id, query.from_user.id)
        return

    bot.decline_chat_join_request(query.chat.id, query.from_user.id)
    print('declined')
    return


@waiting_message_wrapper
def start(update, context):
    cmd = update.message.text.split(' ')
    if len(cmd) > 1:
        return verify_payment(update, context)
    groups = group.get_all_groups()
    user_detail = user.get_user(update.effective_user.id)
    if not user_detail:
        tg_user = update.effective_user
        user.create_user(
            tg_user.id, tg_user.first_name, tg_user.last_name, tg_user.username
        )

    keyboard = []
    for g in groups:
        keyboard.append([InlineKeyboardButton(
            g.name, callback_data=f'group_{g.id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = WELCOME_MESSAGE.format(user=update.message.from_user.first_name)
    update.message.reply_text(text, reply_markup=reply_markup)


@waiting_message_wrapper
def select_group(update, context):
    query = update.callback_query
    query.answer()

    group_id = int(query.data.split('_')[1])
    group_detail = group.get_group(group_id)
    context.user_data['group_id'] = group_id
    payment_keyboard = [
        [InlineKeyboardButton(
            i[0], callback_data=f'payment_{i[1]}') for i in PAYMENT_METHODS
         ]
    ]
    reply_markup = InlineKeyboardMarkup(payment_keyboard)
    text = GROUP_DETAIL_MESSAGE.format(
        group_name=group_detail.name,
        price=group_detail.price,
        duration=group_detail.duration,
    )
    query.edit_message_text(text=text, reply_markup=reply_markup)


@waiting_message_wrapper
def select_payment_method(update, context):
    query = update.callback_query
    query.answer()

    group_detail = group.get_group(context.user_data['group_id'])
    if not group_detail:
        query.edit_message_text(text='Group not found')
        return
    bot_username = context.bot.username
    payment_method = query.data.split('_')[1]
    user_detail = user.get_user(update.effective_user.id)
    txt = transaction.create_transaction(
        user=user_detail, group=group_detail, amount=group_detail.price, status='pending', payment_method=payment_method)
    if payment_method == 'chapa':
        data = {
            'email': f'{update.effective_user.first_name}@gmail.com',
            'amount': group_detail.price,
            'currency': 'ETB',
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name or 'None',
            'tx_ref': str(txt.transaction_id),
            'currency': 'ETB',
            'return_url': f'https://t.me/{bot_username}?start={txt.transaction_id}'
        }
        payment = chapa.initialize(**data)
        if payment['status'] == 'success':
            checkout_url = payment['data']['checkout_url']
            keyboard = [
                [
                    InlineKeyboardButton(
                        'Pay', url=checkout_url
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text=PAY_MESSAGE.format(
                    link=checkout_url,
                ),
                reply_markup=reply_markup,
                parse_mode='HTML',
            )
            return
        query.edit_message_text(text='Payment failed')
        return
    # TODO: add other payment methods
    else:
        title = "Payment Example"
        description = "Payment Example using python-telegram-bot"
        payload = str(txt.transaction_id)
        provider_token = STRIPE_SECRET
        currency = 'ETB'
        price = 100

        prices = [LabeledPrice("Test", price * 100)]
        context.bot.send_invoice(
            user_detail.user_id, title, description, payload, provider_token, currency, prices
        )


def precheckout_callback(update, context):
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    transaction_details = transaction.get_transaction(query.invoice_payload)
    # check the payload, is this from your bot?
    if not transaction_details:
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update, context):
    print(update, context)
    tx_ref = update.message.successful_payment.invoice_payload
    transaction_details = transaction.get_transaction(tx_ref)
    transaction.update_transaction(tx_ref, status='success')
    membership.create_membership(
        user=transaction_details.user,
        group=transaction_details.group,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=transaction_details.group.duration),
        status='active',
        transaction=transaction_details,
    )
    keyboard = [[
        InlineKeyboardButton('Join', url=INVITE_LINK)
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(INVITE_MESSAGE.format(
        link=INVITE_LINK),
        parse_mode='HTML',
        reply_markup=reply_markup,
    )


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # register handlers
    dispatcher.add_handler(CommandHandler('start', start))
    # handle callback for group + _ + group_id
    dispatcher.add_handler(CallbackQueryHandler(
        select_group, pattern='^group_-?[0-9]+$'))
    dispatcher.add_handler(CallbackQueryHandler(
        select_payment_method, pattern='^payment_.+$'))

    # chat join request handler
    dispatcher.add_handler(
        ChatJoinRequestHandler(callback=chat_join_request, pass_chat_data=True))

    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, successful_payment_callback))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
