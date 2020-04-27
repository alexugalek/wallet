from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request
from finance.models import TelegramCredentials, SubCategories, FinancialExpenses, AccountSettings
from django.contrib.auth.models import User
from django.db.models import Sum
from wallet.settings import TODAY_IS, PERMANENT_URL
import re


def get_message(text, chat_id):
    now = TODAY_IS
    year, month, day = now.year, now.month, now.day
    username = TelegramCredentials.objects.get(telegram_id=chat_id).user.username
    subcategories_names = '\n'.join([subcategory.name for subcategory in SubCategories.objects.all() if subcategory.name != 'Other'])
    raw_text = text.strip().lower()

    if raw_text == 'balance':
        common_limit = AccountSettings.objects.filter(user__username=username, report=True).values('user__id').annotate(value=Sum('limit_value'))
        common_limit = common_limit.get()['value'] if common_limit else 0

        today_expenses = FinancialExpenses.objects.filter(created__year=year, created__month=month, created__day=day, user__username=username).values('user__id').annotate(value=Sum('expense_value'))
        today_expenses = today_expenses.get()['value'] if today_expenses else 0

        common_limit_text_part = f'Hello my friend!\nYour balance for today is still : {round((common_limit - today_expenses), 2)}$'

        expense_text_part = f'Your spent today : {round((today_expenses), 2)}$'

        if common_limit == 0:
            return expense_text_part
        else:
            return f'{common_limit_text_part}\n{expense_text_part}'

    try:
        subcategory, value = re.split(r'\W+', text, maxsplit=1)
        subcategory = subcategory.strip().title()
        value = round(float(value.replace(',', '.')), 2)
        if subcategory not in subcategories_names:
            return f"Category --{subcategory}-- doesn't exist"

        try:
            expense = FinancialExpenses()
            expense.user = User.objects.get(username=username)
            expense.expense_value = value
            expense.subcategory = SubCategories.objects.get(name=subcategory)
            expense.save()
            text_part = f'{value}$ was successful added to {subcategory} category'

            try:
                category_name = SubCategories.objects.get(name=subcategory).category.name
                category_limit = AccountSettings.objects.filter(user__username=username, category__name=category_name, report=True).first()
                if category_limit:
                    category_limit = category_limit.limit_value.amount
                    today_category_expenses = FinancialExpenses.objects.filter(created__year=year, created__month=month, created__day=day, user__username=username, subcategory__category__name=category_name).values('subcategory__category__name').annotate(value=Sum('expense_value')).get()['value']
                    today_category_balance = round((category_limit - today_category_expenses), 2)
                    return text_part + f'\nYour balance in {category_name} for today is: {today_category_balance}$'
                else:
                    return text_part

            except Exception:
                return text_part

        except Exception:
            pass

    except Exception:
        return f'If you want to add some expenses use next format:\n\n"Category  Value"\n\nYou can add cost to the next categories:\n{subcategories_names}\n\n\nIf you want to see you balance for today use command\n\n\nBALANCE'


def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if not TelegramCredentials.objects.filter(telegram_id=chat_id).exists():

        try:
            user = User.objects.filter(username=text).get()
            telegram_credentials = TelegramCredentials()
            telegram_credentials.user = user
            telegram_credentials.telegram_id = chat_id
            telegram_credentials.save()
            update.message.reply_text(
                f'Your account was successful created\n'
                f'Your account id is {telegram_credentials.id}\n'
                f'Try command\nBALANCE\nto know your limit balance for today'
            )

        except Exception:
            update.message.reply_text(
                f"If you have registered already then Send correct username to us :)\n"
                f"If you haven't then visit our website for registration!\n"
                f"{PERMANENT_URL}"
            )

    else:
        reply_text = get_message(text, chat_id)
        update.message.reply_text(
            text=reply_text
        )


class Command(BaseCommand):
    help = 'Telegram-bot'

    def handle(self, *args, **kwargs):
        # correct connection
        request = Request(connect_timeout=0.5, read_timeout=1.0)
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )
        # print(bot.get_me())

        # handler install
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        # non stop runner
        updater.start_polling()
        updater.idle()
