from telegram.ext import Updater, CommandHandler


def alarm(bot, job):
    """Send the alarm message."""
    REMINDER_TEXT = "You have {} pending tasks.\n"
    bot.send_message(job.context, text=REMINDER_TEXT)

def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:

        # Add job to queue
        job = job_queue.run_repeating(alarm, interval=60,first=0, context=chat_id)
        # job = job_queue.run_repeating(set_timer, interval=5, first=0)
        # chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')

u = Updater('514604364:AAF7Iae4c11PLjefhBChUhx5PMSlStEKHIc')
j = u.job_queue
dp = u.dispatcher

# job_minute = j.run_repeating(callback_minute, interval=5, first=0)
# timer_handler = CommandHandler('timer', callback_minute, pass_job_queue=True)
dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
# u.dispatcher.add_handler(timer_handler)

u.start_polling()
u.idle()