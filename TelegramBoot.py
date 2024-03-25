from config import my_token
import telebot
from telebot import types
import requests
import json
import re

bot = telebot.TeleBot(my_token, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start_message(message):
    if message.text == '/start':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text='Выберите тест!'), types.KeyboardButton(text='Пройти тест!'))
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text)
def action_selection(message):
    if message.text == 'Выберите тест!':
        select_test(message)
    elif message.text == 'Пройти тест!':
        print('Пройти тест!')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print('Вызвана функция - callback_query')
    selected_option = call.data
    bot.send_message(call.message.chat.id, f"Вы выбрали опцию: ✅ {selected_option}")
    message_split = re.split(r'[Выбран тест № ](\d+)$', selected_option, 2)
    if len(message_split) == 3 and message_split[0] == 'Выбран тест №' and message_split[1].isdigit():
        take_test(call.message, message_split[1])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)


def select_test(message):
    requests_test_info = requests.get('http://127.0.0.1:8000/drf_employees_test/')
    parsing_test_info = json.loads(requests_test_info.text)
    keyboard = telebot.types.InlineKeyboardMarkup()
    for key_test in parsing_test_info:
        button_test_id = telebot.types.InlineKeyboardButton(text=f"✅ {key_test['id']}. {key_test['NameTest']}",
                                                            callback_data=f"Выбран тест № {key_test['id']}")
        keyboard.add(button_test_id)
        bot.send_message(message.chat.id, f"<b><u>{key_test['DescriptionTest']}</u></b>", reply_markup=keyboard)


def take_test(message, test_id):
    requests_test_info = requests.get(f'http://127.0.0.1:8000/drf_employees_test/{test_id}/')
    parsing_test_info = json.loads(requests_test_info.text)
    bot.send_message(message.chat.id,
                     f"<b><u>{parsing_test_info['NameTest']}\n{parsing_test_info['DescriptionTest']}</u></b>")
    requests_questions = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/questions_test/')
    parsing_questions = json.loads(requests_questions.text)
    for key_questions in parsing_questions:
        bot.send_message(message.chat.id, f'<b><i>{parsing_questions[key_questions][0]}</i></b>')
        requests_answers = requests.get(f'http://127.0.0.1:8000/drf_questions/{key_questions}/question_answers/')
        parsing_answers = json.loads(requests_answers.text)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for key_answers in parsing_answers:
            name_button = parsing_answers[key_answers][0]
            button_save = telebot.types.InlineKeyboardButton(text=f'✅ {name_button}', callback_data=name_button[-34:])
            keyboard.add(button_save)
        bot.send_message(message.chat.id, 'Выберите правильный ответ?', reply_markup=keyboard)
    requests_questions_count = requests.get(f'http://127.0.0.1:8000/drf_questions/{test_id}/question_count/')
    parsing_questions_count = json.loads(requests_questions_count.text)
    bot.send_message(message.chat.id,
                     f"<i><u>Общее количество вопросов тесте - {parsing_questions_count['QuestionCount']}</u></i>")


if __name__ == '__main__':
    print('Бот запущен!')
    bot.infinity_polling(none_stop=True)
