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
from wallet.settings import PERMANENT_URL
import datetime
import re


def errors_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper


@errors_handler
def get_message(text, chat_id):

    now = datetime.datetime.utcnow()
    year, month, day = now.year, now.month, now.day

    # identify user
    username = TelegramCredentials.objects.get(telegram_id=chat_id).user.username

    # get all active subcategories
    subcategories_names = '\n'.join([subcategory.name for subcategory in SubCategories.objects.all() if subcategory.name != 'Other'])
    # input message handler
    raw_text = text.strip().lower()

    if raw_text == 'balance':

        # get common day limit value
        common_limit = AccountSettings.objects.filter(user__username=username, report=True).values('user__id').annotate(value=Sum('limit_value'))
        common_limit = common_limit.get()['value'] if common_limit else 0

        # get all categories where report in included
        reported_categories = set([setting.category.name for setting in AccountSettings.objects.filter(user__username=username, report=True)])

        # count total day expenses and total day expenses where report is included
        today_expenses = FinancialExpenses.objects.filter(created__year=year, created__month=month, created__day=day, user__username=username).values('user__id', 'subcategory__category__name').annotate(value=Sum('expense_value'))
        today_expenses_amount_in_report = 0
        today_expenses_amount_common = 0
        for expense in today_expenses:
            today_expenses_amount_common += expense['value']
            if expense['subcategory__category__name'] in reported_categories:
                today_expenses_amount_in_report += expense['value']

        # generate message part about balance as difference between limits and expenses where categories are included
        common_limit_text_part = f'Hello my friend!\nYour balance for today is still : {round((common_limit - today_expenses_amount_in_report), 2)}$'

        # generate message part about common daily expenses
        expense_text_part = f'Your spent today : {round(today_expenses_amount_common, 2)}$'

        # generate full message
        if common_limit == 0:
            return expense_text_part
        else:
            return f'{common_limit_text_part}\n{expense_text_part}'

    # try to handle message
    try:
        subcategory, value = re.split(r'\W+', text, maxsplit=1)
        subcategory = subcategory.strip().title()
        value = round(float(value.replace(',', '.')), 2)

        if subcategory not in subcategories_names:
            return f"Category --{subcategory}-- doesn't exist"

        if not value:
            return f"We don't accept 0 value"

        # try to save data to db
        try:
            expense = FinancialExpenses()
            expense.user = User.objects.get(username=username)
            expense.expense_value = value
            expense.subcategory = SubCategories.objects.get(name=subcategory)
            expense.save()
            text_part = f'{value}$ was successful added to {subcategory} category'

            # try to generate message with balance in category where report is included
            try:
                category_name = SubCategories.objects.get(name=subcategory).category.name
                category_limit = AccountSettings.objects.get(user__username=username, category__subcategories__name=subcategory, report=True)

                if category_limit:
                    category_limit = category_limit.limit_value.amount
                    today_category_expenses = FinancialExpenses.objects.filter(created__year=year, created__month=month, created__day=day, user__username=username, subcategory__category__subcategories__name=subcategory).values('subcategory__category__name').annotate(value=Sum('expense_value')).get()['value']
                    today_category_balance = round((category_limit - today_category_expenses), 2)

                    return text_part + f'\nYour balance in {category_name} for today is: {today_category_balance}$'
                else:
                    return text_part

            except Exception:
                return text_part

        except Exception:
            pass

    # generate help message
    except Exception:
        return f'If you want to add some expenses use next format:\n\n"Category  Value"\n\nYou can add cost to the next categories:\n{subcategories_names}\n\n\nIf you want to see you balance for today use command\n\n\nBALANCE'


@errors_handler
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    if not TelegramCredentials.objects.filter(telegram_id=chat_id).exists():

        # try to identify user username
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

        # generate help message
        except Exception:
            update.message.reply_text(
                f"If you have registered already then Send correct username to us :)\n"
                f"If you haven't then visit our website for registration!\n"
                f"{PERMANENT_URL}"
            )

    # generate answer
    else:
        reply_text = get_message(text, chat_id)
        update.message.reply_text(
            text=reply_text
        )


# common echo telegram bot
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
