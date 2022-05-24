import telebot
from telebot import types
import psycopg2


bot = telebot.TeleBot('')

lang = ''


@bot.message_handler(commands=['start'])
def start_message(message):
    user = message.from_user.username
    bot.send_message(message.chat.id, f'Менд, {user}! Меня зовут Манджа, я буду твоим помощником в переводе калмыцких слов. Я умею переводить в двух режимах: с русского на калмыцкий и с калмыцкого на русский. Для выбора или изменения режима напиши мне /lang')


@bot.message_handler(commands=['lang'])
def lang_buttons(message):
    keyboard = types.InlineKeyboardMarkup()
    rus_kalm = types.InlineKeyboardButton(text='Русско-калмыцкий', callback_data='rus_kalm')
    kalm_rus = types.InlineKeyboardButton(text='Калмыцко-русский', callback_data='kalm_rus')
    keyboard.add(rus_kalm, kalm_rus)
    bot.send_message(message.chat.id, 'Выбери режим', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):
    global lang
    if call.data == 'rus_kalm':
        bot.send_message(call.message.chat.id, 'Вы выбрали режим перевода с русского на калмыцкий')
        lang = 'rus_kalm'
    elif call.data == 'kalm_rus':
        bot.send_message(call.message.chat.id, 'Вы выбрали режим перевода с калмыцкого на русский')
        lang = 'kalm_rus'


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    con = psycopg2.connect(
        database='tbot',
        user='postgres',
        password="postgres",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    try:
        cur.execute(f"SELECT * FROM {lang} WHERE word='{message.text.lower()}';")
        row = cur.fetchall()
        bot.send_message(message.from_user.id, f"{row[0][0]} - {row[0][1]}")
        con.close()
    except psycopg2.errors.SyntaxError:
        bot.send_message(message.from_user.id, 'Вы не выбрали режим. Для выбора режима напишите /lang')
    except psycopg2.errors.UndefinedTable:
        bot.send_message(message.from_user.id, 'Режим калмыцко-русского перевода еще не реализован. Для смены напишите /lang')
    except IndexError:
        bot.send_message(message.from_user.id, 'Такого слова пока что нет в моих словарях')



bot.polling()
