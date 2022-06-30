import telebot
from telebot import types
import psycopg2

from utils.fuzzy_wuzzy import standart_fuzzy_wuzzy, custom_fuzzy_wuzzy

test_bot = '2080377181:AAHZ234eNUgd28wcYQXacMGosjYiqrjbwMI'

bot = telebot.TeleBot(test_bot)


# lang = ''


@bot.message_handler(commands=['start'])
def start_message(message):
    user = message.from_user.username
    bot.send_message(message.chat.id,
                     f'Менд, {user}! Меня зовут Манджа, я буду твоим помощником-переводчиком! Я могу переводить и '
                     f'русские, и калмыцкие слова. Просто начни мне писать! ')


# @bot.message_handler(commands=['lang'])
# def lang_buttons(message):
#     keyboard = types.InlineKeyboardMarkup()
#     rus_kalm = types.InlineKeyboardButton(text='Русско-калмыцкий', callback_data='rus_kalm')
#     kalm_rus = types.InlineKeyboardButton(text='Калмыцко-русский', callback_data='kalm_rus')
#     keyboard.add(rus_kalm, kalm_rus)
#     bot.send_message(message.chat.id, 'Выбери режим', reply_markup=keyboard)


# @bot.callback_query_handler(func=lambda call: True) def callback_worker(call): global lang if call.data ==
# 'rus_kalm': bot.send_message(call.message.chat.id, '''Вы выбрали режим перевода с русского на калмыцкий. Количество
# словарный статей в данном режиме VAR ''') lang = 'rus_kalm' elif call.data == 'kalm_rus': bot.send_message(
# call.message.chat.id, '''Вы выбрали режим перевода с русского на калмыцкий. Количество словарный статей в данном
# режиме VAR ''') lang = 'kalm_rus'

similarity_percentage = 0.1

# сделать режим есть калмыцкие буквы или нет?
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    con = psycopg2.connect(
        database='testdb',
        user='andrey',
        password="Yashkul08#",
        host="127.0.0.1",
        port="5432"
    )
    cur = con.cursor()
    try:  # в этом блоке - выбираем  с помощью триграмм.
        # 1. если есть полное совпадение (индекс 1), то высылаем его (а если несколько)
        # 2. Если нет полного "сори, но возможно вы имели ввиду .... - список ближайших совпадений"
        # cur.execute(f"SELECT * FROM all_words WHERE word='{message.text.lower()}' AND type='{lang}';")
        text = message.text.lower()
        cur.execute(
            f"WITH ts AS (SELECT word, article, (similarity(all_words.word, '{text}')) AS similarity, dictionary "
            f"FROM all_words ORDER BY similarity DESC) SELECT * FROM ts WHERE similarity >= {similarity_percentage} "
            f"AND LENGTH(word) BETWEEN {len(text)} AND {len(text)+1};")
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
                for artilce in exact_math:
                    bot.send_message(
                        message.from_user.id,
                        artilce
                    )
            else:
                to_send = custom_fuzzy_wuzzy(similar, text)
                if to_send:
                    bot.send_message(message.from_user.id,
                                     f'К сожалению, я не нашел слова "{text}". Вот похожие на ваш запрос слова:')
                    bot.send_message(message.from_user.id, to_send)
                    bot.send_message(message.from_user.id,
                                     'Если среди них есть нужно вам, пришлите мне его и я его переведу.')
                else:
                    raise IndexError
        else:
            raise IndexError

        con.close()

    # except psycopg2.errors.SyntaxError:
    #     bot.send_message(message.from_user.id, 'Вы не выбрали режим. Для выбора режима напишите /lang')
    except IndexError:
        bot.send_message(message.from_user.id, 'К сожалению, ничего похожего я не нашел.')


bot.polling()
