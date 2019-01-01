#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram import InlineQueryResultArticle, InputTextMessageContent

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import InlineQueryHandler

"""
A telegram bot to track activites of the participants of GetSetCode Challenge.
"""

import logging
import dataset

from GitActivity import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

db = dataset.connect('sqlite:///todo.db')


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

HELP_TEXT = """/gitname `github username` to set your username
/todo `topicname` to add a new task
/done `topicname` to add a finished task
/reminder `on|off` to turn on or turn off reminder
@gsctbot <space> to mark tasks as finished

*Private commands*

/leaderboard to display leaderboard
/help to display this help
/tasks to list your tasks and delete them.
/streak to see number of days you've been active.
"""


users = db['users']
tasks = db['tasks']
github_activity = db['github_activity']


def addToDo(user, task):
    tasks.insert(dict(user_id=user.id, text=task, finished=False,
                      daystarted=date.today().isoformat()))


def addDone(user, task):
    tasks.insert(dict(
        user_id=user.id,
        text=task,
        finished=True,
        daystarted=date.today().isoformat(),
        dayfinished=date.today().isoformat()
    ))


def getTasks(user):
    its = []
    for task in tasks:
        if(task['user_id'] == user.id):
            its += [task['text']]
            print(task['text'])
    return its


def start(bot, update):
    """Send a message when the command /start is issued."""
    user = update.message.from_user
    reply = '_Dear {}_,\n\n *Welcome to GetSetCode* 💻 ,\n\n' + \
        'Start by setting your github username ' + \
        'using /gitname <space> _username_.'

    reply = reply.format(user.first_name.title())

    update.message.reply_text(
        reply,
        parse_mode='MarkDown',
        reply_markup=ReplyKeyboardRemove()
    )


def gitname(bot, update):
    user = update.message.from_user
    git_name = update.message.text.replace('/gitname', '')
    git_name = git_name.replace(' ', '')
    if(len(git_name) < 3):
        update.message.reply_text('🙌 Invalid github username, try again.')
    else:
        print('git name: {}'.format(git_name))
        if(users.count(user_id=user.id) > 0):
            users.update(dict(user_id=user.id, username=user.username,
                              gitname=git_name), ['user_id'])
        else:
            users.insert(dict(
                user_id=user.id,
                username=user.username,
                gitname=git_name,
                score=0
            ))
        update.message.reply_text(
            '🐙 Git username successfully set,\n' +
            'use /help to continue. Don\'t forget to join our group @gsc_tdc'
        )


def help(bot, update):
    # no need of reply for commands from group chats
    if update.message.chat_id < 0:
        return

    """Send a message when the command /help is issued."""
    # update.message.reply_text(HELP_TEXT, parse_mode = 'MarkDown',
    #    reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(HELP_TEXT, parse_mode='MarkDown')


def alarm(bot, job):
    """Send the alarm message."""
    usrname = str(bot.getChat(job.context).username)
    d = dataset.connect('sqlite:///todo.db')
    t = d['tasks']
    task = list(t.find(user_id=job.context, finished=False))
    task_count = len(task)

    REMINDER_TEXT = "Hi @{0},\nYou have {1} pending tasks.\n".format(
        usrname,
        task_count
    )

    for t in task:
        line = "• {0}\n".format(dict(t)['text'])
        REMINDER_TEXT += line
    bot.send_message(job.context, text=REMINDER_TEXT)


def todo(bot, update):
    # def todo(bot, update, args, job_queue, chat_data):
    """Send a message when the command /help is issued."""
    if update.message.chat_id != -1001187606231:
        update.message.reply_text(
            '💡 This command is a group only command!. ' +
            'Let others know what you are working on 😎'
        )
        return
    task = update.message.text[6:]
    print('task : ' + task)
    user = update.message.from_user

    if(task == ''):
        update.message.reply_text('💡 The format is /todo <space> Taskname ')
    else:
        addToDo(user, task)
        update.message.reply_text(
            '🚣‍ @{} added task : {}.\n ({} pending tasks)'.format(
                user.username,
                task,
                str(tasks.count(user_id=user.id, finished=False))
            )
        )


def reminder(bot, update, args, job_queue, chat_data):
    cmd = str(update.message.text[10:])
    print(job_queue.jobs())
    print(cmd)
    if cmd == 'on':
        update.message.reply_text('Reminder turned on\n')
        for j in job_queue.jobs():
            j.schedule_removal()
        job_queue.stop()
        job = job_queue.run_repeating(alarm, interval=86400, first=0,
                                      context=update.message.chat_id)
        job_queue.start()
        job.enabled = True
    elif cmd == 'off':
        for j in job_queue.jobs():
            j.schedule_removal()

        update.message.reply_text('Reminder turned off\n')
        job_queue.stop()
    else:
        update.message.reply_text(
            'Handle reminders with /reminder on  or /reminder off\n')


def done(bot, update):
    """Send a message when the command /help is issued."""
    if update.message.chat_id != -1001187606231:
        update.message.reply_text(
            '💡 This command is a group only command!. ' +
            'Let others know what you are working on 😎'
        )
        return
    task = update.message.text[6:]
    print('done task : ' + task)
    if(task == ''):
        update.message.reply_text('💡 The format is /done <space> _Taskname_')
    else:
        user = update.message.from_user
        addDone(user, task)
        cur_score = users.find_one(user_id=user.id)['score']
        cur_score += 10
        users.update(dict(user_id=user.id, score=cur_score), ['user_id'])
        update.message.reply_text(
            '🚀 @{} finished task : {}.\n ({} pending tasks)'.format(
                user.username, task, str(
                    tasks.count(
                        user_id=user.id, finished=False))))


def leaderboard(bot, update):
    """Send a message when the command /help is issued."""
    delta = timedelta(days=1)
    enddate = date.today()

    # disable for group chat
    if update.message.chat_id < 0:
        return
    uss = []
    my_score = 0
    for user in users:
        total_score = user['score']  # + streak_score
        statement = 'SELECT  count(dayfinished) as count FROM ' + \
            '(SELECT DISTINCT dayfinished FROM tasks WHERE user_id={});' \
            .format(
                user['user_id']
            )
        streak = db.query(statement)
        for row in streak:
            streak_score = row['count']
            break
        # streak_score = int((streak_score*(streak_score + 1))/2)
        git_score = GitActivity().get_total_commit_count(user['gitname'])
        uss.append([user['gitname'], total_score, streak_score, git_score])
        if user['user_id'] == update.message.from_user.id:
            my_score = total_score
    uss.sort(key=lambda x: (-x[1], -x[2]))
    lb = " 🏆 Leaderboard \n\n"
    i = 0
    for u in uss:
        i += 1
        lb += ('{}. {} - {} 🔥{}  👾{} \n').format(i, u[0], u[1], u[2], u[3])
    lb += "\n\n Your score : {}".format(str(my_score))
    update.message.reply_text(lb)


def tasks_(bot, update):
    reply = 'Your tasks are\n\n'
    user = update.message.from_user

    # if the command is from a group chat no need of reply
    if update.message.chat_id < 0:
        return

    tasks2 = tasks.find(user_id=user.id)
    for task in tasks2:
        reply += '• {}'.format(task['text'])
        if task['finished']:
            reply += ' - ✅ \n'
        else:
            reply += ' - ⭕ /delete_{}\n'.format(str(task['id']))
    update.message.reply_text(reply)


def echo(bot, update):
    """Echo the user message."""
    user = update.message.from_user
    # disable for group chat
    if update.message.chat_id < 0:
        return
    # print(update.message.text[:10])
    update.message.reply_text(
        '🙌 Sorry, didnt get you, /help for list of commands')


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query.lower()
    user = update.inline_query.from_user
    tasks2 = tasks.find(finished=False)
    results = []
    # print(query)
    for task in tasks2:
        if task['user_id'] == user.id and task['finished'] is False:
            results.append(InlineQueryResultArticle(
                id=str(task['id']),
                title=task['text'],
                description='⏳ Ongoing',
                # description='✅ Finished' if task['finished'] else '⏳ Ongoing'
                input_message_content=InputTextMessageContent(
                    '/completed {}'.format(task['id'])))
            )
    update.inline_query.answer(results, cache_time=0, is_personal=True)


def streak(bot, update):
    # if the command is from a group chat no need of reply
    if update.message.chat_id < 0:
        return
    user = update.message.from_user
    statement = 'SELECT  count(dayfinished) as count FROM ' + \
        '(SELECT DISTINCT dayfinished FROM tasks WHERE user_id={});'.format(
            user.id
        )
    streak = db.query(statement)
    for row in streak:
        streak_score = row['count']
        break
    update.message.reply_text(
        '🔥 Your streak : {} days'.format(streak_score),
        parse_mode='MarkDown')


def completed(bot, update):
    if update.message.chat_id != -1001187606231:
        update.message.reply_text(
            '💡 You can only mark tasks as completed from the group itself, ' +
            'update your progress with community! 💹')
        return
    user = update.message.from_user
    try:
        task_id = update.message.text.replace('/completed', '').strip()
        if(tasks.count(user_id=user.id, id=task_id, finished=False) > 0):
            tasks.update(dict(
                user_id=user.id,
                id=task_id,
                finished=True,
                dayfinished=date.today().isoformat()
            ), ['id', 'user_id'])
            cur_score = users.find_one(user_id=user.id)['score']
            cur_score += 10
            users.update(dict(user_id=user.id, score=cur_score), ['user_id'])
            reply = '🚀 @{} completed task : {}.\n ({} pending tasks)'.format(
                user.username, tasks.find_one(
                    id=task_id)['text'], str(
                    tasks.count(
                        user_id=user.id, finished=False)))
            update.message.reply_text(reply, parse_mode='MarkDown')
        else:
            update.message.reply_text(
                '💡 Unknown error occurred report @ir5had',
                parse_mode='MarkDown')
    except Exception as e:
        print(e)
        update.message.reply_text(
            '👾 Unknown error occurred report the error @ir5had',
            parse_mode='MarkDown')


def error(bot, update, error):
    """Log Errors caused by Updates."""

    logger.warning('Update "%s" caused error "%s"', update, error)


def command_handler(bot, update):
    # disable for group chat
    if update.message.chat_id < 0:
        return
    if update.message.text[:7] == '/delete':
        try:
            task_id = int(update.message.text.split('_')[1])
            tasks.delete(id=task_id)
            reply = 'Task deleted.'
            update.message.reply_text(reply)
        except BaseException:
            update.message.reply_text(
                'Deletion error occurred',
                parse_mode='MarkDown')


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.environ['TG_BOT_TOKEN'])
    j = updater.job_queue
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("gitname", gitname))
    dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("todo", todo))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(CommandHandler("completed", completed))
    dp.add_handler(CommandHandler("tasks", tasks_))
    dp.add_handler(CommandHandler("leaderboard", leaderboard))
    dp.add_handler(CommandHandler("streak", streak))
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(CommandHandler("todo", todo))
    dp.add_handler(CommandHandler("reminder", reminder,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.command, command_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
