from telegram.ext import Updater, MessageHandler, Filters
from additional_content import get_logger
from class_bot_father import Bot_Father
import threading, os


class Telegram_Bot(Bot_Father):


	def __init__(self, logger, req, res):
		self.logger = logger
		super().__init__()
		super().update_arg(req, res)


	@Bot_Father.open_file
	def check_saved_bot(self, file):
		for line in file.readlines():
			if self.user_id in line:
				if len(line.split(';')) == 2:
					self.bot = {'token': line[:-1].split(';')[1]}
					self.res['response']['text'] = 'У вас уже доваблен бот.\n Чтобы активировать своего бота напишите: Запусти бота {"вк" или "телеграмм"}'
					self.save_flag = True
					self.logger.info('check_saved_bot; successful_add: {}'.format(self.user_id))


	def start_bot_work(self, TOKEN):
		try:
			self.logger.info('Starting bot work')
			updater = Updater(TOKEN, use_context=True)
			dp = updater.dispatcher
			dp.add_handler(MessageHandler(Filters.text, self.text_message))
			self.logger.info('Successfully connecting to chat. Waiting for messages')
			updater.start_polling()
			while getattr(threading.currentThread(), 'flag', True):
				pass
			updater.stop()
			threading.currentThread().join()
		except Exception as error:
			self.logger.error(f'Error; start_bot_work: {error}')


	def text_message(self, update, context):
		self.network = context
		self.logger.info(f'Get: message: {update.message.from_user}')
		super().add_user_info([os.path.join('top_secret', 'telegram_users.txt'), 'w'], update.message.from_user.id, update.message.text)
		update.message.reply_text(f'{update.message.from_user.first_name}, мы вам скоро ответим.')
		self.logger.info('text_message; message: {}'.format({'user_id': update.message.from_user.id,
														'text': f'{update.message.from_user.first_name}, мы вам скоро ответим.'}))


	@Bot_Father.func_implementer
	def answer_messages(self):
		for user_id in self.new_messages:
			self.network.bot.send_message(chat_id=user_id, text=self.user_message.split(':')[1])
			self.logger.info('answer_messages; message: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))


	@Bot_Father.open_file
	@Bot_Father.func_implementer
	def write_all_users(self, file):
		users = file.readlines()
		for line in users:
			if self.user_id in line:
				for user_id in line[:-1].split(':')[1].split(','):
					self.network.bot.send_message(chat_id=user_id, text=self.user_message.split(':')[1])
					self.logger.info('write_all_users; message: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))