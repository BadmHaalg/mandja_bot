import os
import telebot
import psycopg2
import config

from telebot import types
from utils.fuzzy_wuzzy import standart_fuzzy_wuzzy, custom_fuzzy_wuzzy

test_bot = os.getenv('TBOT_TOKEN')

bot = telebot.TeleBot(test_bot)


@bot.message_handler(commands=['start'])
def start_message(message):
    user = message.from_user.username
    bot.send_message(message.chat.id,
                     f'Менд, {user}! Меня зовут Манджа, я буду твоим помощником-переводчиком! Я могу переводить и '
                     f'русские, и калмыцкие слова. Просто начни мне писать! ')


similarity_percentage = 0.1


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    con = psycopg2.connect(
        database=os.getenv('db_name'),
        user=os.getenv('db_user'),
        password=os.getenv('db_pswd'),
        host=os.getenv('db_host'),
        port=os.getenv('db_port'),
    )
    curr = con.cursor()
    if call:
        curr.execute(f"SELECT word, article, dictionary FROM all_words WHERE word='{call.data.replace(' ', '')}'")
        response = curr.fetchall()
        word = response[0][0].replace(' ', '')
        translate = response[0][1]
        dictionary = response[0][2]
        r = f"{word} - {translate}. \n ---------- \n Словарь: {dictionary}"
        bot.answer_callback_query(call.id, word)
        bot.send_message(call.message.chat.id, r)
    con.close()

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    try:
        con = psycopg2.connect(
            database=os.getenv('db_name'),
            user=os.getenv('db_user'),
            password=os.getenv('db_pswd'),
            host=os.getenv('db_host'),
            port=os.getenv('db_port'),
        )
        cur = con.cursor()
        text = message.text.lower()
        cur.execute(
            f"WITH ts AS (SELECT word, article, (similarity(all_words.word, '{text}')) AS similarity, dictionary "
            f"FROM all_words ORDER BY similarity DESC) SELECT * FROM ts WHERE similarity >= {similarity_percentage} "
            f"AND LENGTH(word) BETWEEN {len(text)} AND {len(text) + 1};")
        row = cur.fetchall()
        if row:
            exact_math = []
            similar = []
            for r in row:
                word = r[0].replace(' ', '')
                translate = r[1]
                similarity = r[2]
                dictionary = r[3]
                if similarity == 1:
                    exact_math.append(f"{word} - {translate}. \n ---------- \n Словарь: {dictionary}")
                else:
                    similar.append([word, standart_fuzzy_wuzzy(text, word), similarity])
            if exact_math:
                for article in exact_math:
                    bot.send_message(
                        message.from_user.id,
                        article)
            else:
                to_send = custom_fuzzy_wuzzy(similar, text)
                if to_send:
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    buttons = []
                    for t in to_send.split(','):
                        itembtn = types.InlineKeyboardButton(t, callback_data=t)
                        buttons.append(itembtn)
                    markup.add(*buttons)
                    bot.send_message(message.from_user.id,
                                     f'К сожалению, я не нашел слова "{text}". Вот похожие на ваш запрос слова:',
                                     reply_markup=markup)
                    bot.send_message(message.from_user.id,
                                     'Если среди них есть нужно вам, пришлите мне его и я его переведу.')
                else:
                    raise IndexError
        else:
            raise IndexError

        con.close()
    except IndexError:
        bot.send_message(message.from_user.id, 'К сожалению, ничего похожего я не нашел.')


bot.polling()
