from additional_content import get_logger
import threading, logging, vk_api, random, os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


logger = get_logger('vk_bot_logger', 'vk_bot/logfile.log')


class Vk_Bot():


	def __init__(self):
		self.vk = None
		self.bot = 	None
		self.new_messages = {}
		self.thread_vk_bot = None


	def func_implementer(func):
		def decorator(self, *data):
			try:
				if self.bot:
					info_return = func(self, *data)
					if info_return:
						self.res['response']['text'] = info_return
					else:
						self.res['response']['text'] = 'Выполнено.'
				else:
					self.res['response']['text'] = 'У вас нет добавленного вк бота.'
			except Exception as error:
				self.res['response']['text'] = 'Что-то пошло не так'
				logger.error(f'Error; {func.__name__}: {error}')
		return decorator


	def open_file(func):
		def decorator(self, arg, *data):
			with open(arg[0], arg[1]) as file:
				func(self, file, *data)
		return decorator


	def update_arg(self, req, res):
		self.user_message = req['request']['original_utterance'].lower()
		self.user_id = req['session']['user_id']
		self.req, self.res = req, res


	@open_file
	def check_saved_bot(self, file):
		for line in file.readlines():
			if self.user_id in line and len(line.split(';')) == 3:
				self.bot = {'token': line.split(';')[1], 'group_id': line[:-1].split(';')[2]}
				self.res['response']['text'] = 'У вас доваблен бот вк.\n Чтобы активировать своего бота напишите: Запусти бота {"вк" или "телеграмм"}'
				return ('У вас доваблен бот вк.\n Чтобы активировать своего бота напишите: Запусти бота {"вк" или "телеграмм"}')


	def add_bot(self):
		try:
			self.bot = {'token': self.user_message.replace(' ', '').split(';')[0].split('=')[1],
						'group_id': self.user_message.replace(' ', '').split(';')[1].split('=')[1]}
			self.res['response']['text'] = 'Вк бот успешно добавлен.\n Вы можете сохранить данные бота написав: "Запомни бота {вк или телеграмм}"'
		except Exception:
			self.res['response']['text'] = 'Вы неверно ввели данные.'


	@open_file
	@func_implementer
	def save_bot(self, file):
		file.write(';'.join([self.user_id, self.bot['token'], self.bot['group_id']]) + '\n')


	@open_file
	@func_implementer
	def delete_bot(self, file):
		users_bots = file.readlines()
		for line in users_bots:
			if all(key in [self.user_id, self.bot['token'], self.bot['group_id']] for key in line.replace('\n', '').split(';')):
				os.system(r'nul>{}'.format(os.path.join('top_secret', 'users_bots.txt')))
				users_bots.remove(line)
				with open(os.path.join('top_secret', 'users_bots.txt'), 'w') as file_to_write:
					file_to_write.write(''.join(users_bots))
				return
		return 'У вас нет сохраненного бота.'


	@func_implementer
	def start_bot(self):
		if not self.thread_vk_bot:
			self.thread_vk_bot = threading.Thread(target=self.start_vk_bot,
												  args=(self.bot['token'], int(self.bot['group_id'])))
			self.thread_vk_bot.start()
		else:
			return 'Бот уже был активирован.'


	@func_implementer
	def start_vk_bot(self, TOKEN, group_id):
		logger.info('Starting bot work')
		vk_session = vk_api.VkApi(token=TOKEN)
		longpoll = VkBotLongPoll(vk_session, group_id)
		logger.info('Successfully connecting to group. Waiting for messages')
		for event in longpoll.listen():
			if not getattr(threading.currentThread(), 'flag', True):
				threading.currentThread().join()
			elif event.type == VkBotEventType.MESSAGE_NEW:
				logger.info(f'Get; message: {event}')
				self.vk = vk_session.get_api()
				self.add_user_info([os.path.join('top_secret', 'users.txt'), 'a+'], event.obj.message['from_id'], event.obj.message['text'])
				self.vk.messages.send(user_id=event.obj.message['from_id'],
									  message=f'{self.vk.users.get(user_id=event.obj.message["from_id"])[0]["first_name"]}, мы вам скоро ответим.',
									  random_id=random.randint(0, 2 ** 64))
				logger.info('Post; message: {}'.format({'user_id': event.obj.message["from_id"],
														 'text': {f'{self.vk.users.get(user_id=event.obj.message["from_id"])[0]["first_name"]}, мы вам скоро ответим.'}}))


	@open_file
	@func_implementer
	def add_user_info(self, file, user_id, text):
		with open(os.path.join('top_secret', 'users.txt'), 'r') as file_to_read:
			users = file_to_read.readline()
		if len(users) == 0:
			file.write(str(user_id))
		elif str(user_id) not in users.split(';'):
			file.write(f';{user_id}')
		if self.new_messages.get(user_id):
			self.new_messages[user_id].append(text)
		else:
			self.new_messages.update({user_id: [text]})
		logger.info('add_user: {}'.format({'user_id': user_id, 'new_user': user_id in users.split(';')}))


	@func_implementer
	def stop_bot(self):
		self.thread_vk_bot.flag = False
		self.new_messages = {}


	@func_implementer
	def check_new_messages(self):
		if len(self.new_messages) == 0:
			info_return = 'У вас нет новых сообщений.'
		else:
			info_return = f'У вас {len(self.new_messages)} новых сообщений.'
		logger.info('check_new_messages_vk: {}'.format({'info_return': info_return}))
		return info_return


	@func_implementer
	def answer_messages(self):
		for user_id in self.new_messages:
			self.vk.messages.send(user_id=user_id,
							 message=self.user_message.split(':')[1],
							 random_id=random.randint(0, 2 ** 64))
			logger.info('Post; answer_messages_vk: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))


	@open_file
	@func_implementer
	def write_all_users(self, file):
		users = file.readline().split(';')
		for user_id in users:
			self.vk.messages.send(user_id=user_id,
							 message=self.user_message.split(':')[1],
							 random_id=random.randint(0, 2 ** 64))
			logger.info('Post; write_all_users_vk: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))


if __name__ == '__main__':
	app.run()