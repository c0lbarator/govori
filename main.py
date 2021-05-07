#библиотеки
import telebot
from telebot import types
import sqlite3 as db
#бодключение базы данных и курсора
users = db.connect('users.db', check_same_thread=False)
uc = users.cursor()
#токен бота
bot = telebot.TeleBot('1630515353:AAHh1DurX-O1I1wtWLcyOwBCEILBM3UeKrA')
#для создания поста
post_id = None
name = None
desc = None
tags = None
#храним теги для продвижения в случае лайка
ltags = None
uid = None
#num of sent posts
sent_posts = 0
#all posts from recomendation system
all = None
#chatid of current user
chatid = None
#function for making message for post
def post_rec_msg(sent_posts, all, chatid):
    global ltags
    like = types.InlineKeyboardMarkup(row_width=2)
    blike = types.InlineKeyboardButton('Лайкнуть👍', callback_data='like')
    glike = types.InlineKeyboardButton('След. пост', callback_data='next_post')
    like.add(blike, glike)
    bot.send_voice(chatid, all[0][0])
    msg = '''
                        *Название:*''' + str(all[0][1]) + '''
                    *Автор:*''' + str(all[0][2]) + '''
                    *Описание:*''' + str(all[0][3])
    ltags = str(all[0][4])
    bot.send_message(chatid, msg, parse_mode='Markdown', reply_markup=like)

#function for random posts
def random_posts(chatid, like):
    global ltags
    uc.execute('SELECT * FROM posts ORDER BY RANDOM() LIMIT 1;')
    all = uc.fetchall()
    bot.send_voice(chatid, all[0][0])
    msg = '''
                    *Название:*''' + str(all[0][1]) + '''
                *Автор:*''' + str(all[0][2]) + '''
                *Описание:*''' + str(all[0][3])
    ltags = str(all[0][4])
    bot.send_message(chatid, msg, parse_mode='Markdown', reply_markup=like)
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, добро пожаловать в бета-версию FaerCast'а! Здесь всё без инвайтов(ClubHouse, привет!). Для регистрации отправь сообщение с командой /register")
@bot.message_handler(commands=['register'])
def registration(message):
    register = bot.send_message(message.chat.id, 'Для регистрации введи своё имя и фамилию, либо псевдоним(да что хочешь) в следующем сообщении')
    bot.register_next_step_handler(register, name)
def name(message):
    uc.execute(('Select userid FROM users WHERE userid LIKE '+str(message.from_user.id)))
    result = uc.fetchall()
    if len(result) == 0:
        uc.execute('''insert into users(userid, name) VALUES(?, ?)''', (message.from_user.id, message.text))
        users.commit()
        bot.send_message(message.chat.id, 'Регистрация успешно завершена! Если хочешь послушать аудиоистории других юзеров введи команду /listen. Если хочешь создать пост, то отправь мне своё голосовое сообщение 😉. Все другие функции можешь узнать, отправив команду /help')
    else:
        bot.send_message(message.chat.id, 'Ты уже зарегистрирован в FaerCast. Можешь им пользоваться прямо сейчас!')
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '''
    /listen - лента постов других юзеров
    отправленное голосовое сообщение - создание твоего нового поста
    бот работает в бета версии, так что пока функционал урезанный.
    в будущем возсожно будут выходить обновления, но мы нацелены на создание веб платформы.
    по предложениям совершенствования платформы можешь обращаться к разработчику @faeroshi. только без спама, пожалуйста)''')
@bot.message_handler(content_types=['voice'])
def msg_link(message):
    global post_id
    post_id = message.voice.file_id
    post_name = bot.send_message(message.chat.id, 'Отлично! Теперь можешь указать название поста')
    bot.register_next_step_handler(post_name, set_post_name)
def set_post_name(message):
    global name
    name = message.text
    desc = bot.send_message(message.chat.id, 'Круто! Теперь опиши свой пост')
    bot.register_next_step_handler(desc, set_desc)
def set_desc(message):
    global desc
    desc = message.text
    tags = bot.send_message(message.chat.id, 'Последний шаг! Пожалуйста, укажи теги, которые лучше всего опишут твой пост. Перечисли их через запятую, без пробелов.')
    bot.register_next_step_handler(tags, set_tags)
def set_tags(message):
    global tags
    tags = message.text
    bot.send_message(message.chat.id, 'Пост создан!')
    uc.execute(('Select name FROM users WHERE userid LIKE '+str(message.from_user.id)))
    lol = uc.fetchall()
    uc.execute('''insert into posts(post_id, name, author_name, description, tags) VALUES(?, ?, ?, ?, ?)''', (post_id,name, lol[0][0],desc, tags))
    users.commit()
@bot.message_handler(commands=['listen'])
def send_post(message):
    global ltags
    global uid
    global sent_post
    global all
    global sent_posts
    global chatid
    chatid = message.chat.id
    sent_posts = 0
    #print(message.from_user.id)
    #неудавшееся система рекомендаций, заменена заглушкой, которая выплёвывает рандомные посты
    #uc.execute('''SELECT tags FROM users WHERE userid = ?''', (str(message.from_user.id),))
    #tags = str(uc.fetchall()[0][0])
    #print(tags)
    #uc.execute('''SELECT * FROM posts WHERE tags LIKE ?''', (str(tags),))
    like = types.InlineKeyboardMarkup(row_width=2)
    blike = types.InlineKeyboardButton('Лайкнуть👍', callback_data='like')
    glike = types.InlineKeyboardButton('След. пост', callback_data='next_post')
    like.add(blike, glike)
    #all = uc.fetchall()
    all = []
    #print(all)
    uid = message.from_user.id
    if all == []:
        random_posts(message.chat.id, like)
    else:
        #print(all[0][0])
        bot.send_voice(message.chat.id, all[0][0])
        msg = '''
            *Название:*''' + str(all[0][1]) + '''
        *Автор:*''' + str(all[0][2]) + '''
        *Описание:*''' + str(all[0][3])
        ltags = str(all[0][4])
        uid = str(message.from_user.id)
        bot.send_message(message.chat.id,msg, parse_mode='Markdown', reply_markup=like)
    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        global uid
        try:
            if call.message:
                if call.data == "like":
                    #print('good click on button!')
                    uc.execute('''update users set tags = case when tags is NULL then ? else (tags + ?) end where userid = ?''', (str(ltags), str(ltags), str(uid),))
                    users.commit()
                    #print('good like!')
                elif call.data == 'next_post':
                    if len(all) == 1 or len(all) == 0:
                        like = types.InlineKeyboardMarkup(row_width=2)
                        blike = types.InlineKeyboardButton('Лайкнуть👍', callback_data='like')
                        glike = types.InlineKeyboardButton('След. пост', callback_data='next_post')
                        like.add(blike, glike)
                        random_posts(uid, like)
                    else:
                        global sent_posts
                        global chatid
                        sent_posts += 1
                        if sent_posts >= len(all):
                            sent_posts = sent_posts - len(all)
                        post_rec_msg(sent_posts, all, chatid)

        except Exception as e:
            print(repr(e))


bot.polling()