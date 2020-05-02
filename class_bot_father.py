from additional_content import get_logger
import threading, logging, os


class Bot_Father():


	def __init__(self):
		self.bot = 	None
		self.network = None
		self.thread_bot = None
		self.add_flag = False
		self.save_flag= False
		self.new_messages = {}


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
					self.res['response']['text'] = 'У вас нет добавленного бота.'
			except Exception as error:
				self.res['response']['text'] = 'Что-то пошло не так'
				self.logger.error(f'Error; {func.__name__}: {error}')
		return decorator


	def open_file(func):
		def decorator(self, arg, *data):
			with open(arg[0], arg[1]) as file:
				func(self, file, *data)
		return decorator


	def update_arg(self, req, res):
		self.user_message = req['request']['original_utterance']
		self.user_id = req['session']['user_id']
		self.req, self.res = req, res


	def add_bot(self):
		try:
			self.bot = {'token': self.user_message.replace(' ', '').split(';')[0].split('=')[1]}
			if len(self.user_message.split(';')) == 2:
				self.bot.update({'group_id': self.user_message.replace(' ', '').split(';')[1].split('=')[1]})
			self.add_flag = False
			self.res['response']['text'] = 'Бот успешно добавлен.\n Вы можете сохранить данные бота написав: "Запомни бота {вк или телеграмм}"'
			self.logger.info('add_bot; add: {}'.format(self.user_id))
		except Exception:
			self.res['response']['text'] = 'Вы неверно ввели данные.'


	@open_file
	@func_implementer
	def save_bot(self, file):
		group_id = self.bot.get('group_id')
		file.write('{};{}{}\n'.format(self.user_id, self.bot['token'], ';' + group_id if group_id else ''))
		self.save_flag = True
		self.logger.info('save_bot; save: {}'.format(self.user_id))


	@open_file
	@func_implementer
	def delete_bot(self, file):
		users_bots = file.readlines()
		for line in users_bots:
			if all(key in [self.user_id, self.bot['token'], self.bot.get('group_id', True)] for key in line.replace('\n', '').split(';')):
				os.system(r'nul>{}'.format(os.path.join('top_secret', 'users_bots.txt')))
				users_bots.remove(line)
				with open(os.path.join('top_secret', 'users_bots.txt'), 'w') as file_to_write:
					file_to_write.write(''.join(users_bots))
				self.save_flag = False
				self.logger.info('delete_bot; remove: {}'.format(self.user_id))
				return
		return 'У вас нет сохраненного бота.'


	@func_implementer
	def start_bot(self):
		if self.thread_bot:
			return 'Бот уже был активирован.'
		self.thread_bot = threading.Thread(target=self.start_bot_work, args=(list(self.bot.values())))
		self.logger.info('Starting work bot thread')
		self.thread_bot.start()
		if not self.thread_bot.is_alive():
			return 'Что-то пошло не так'


	@open_file
	@func_implementer
	def add_user_info(self, file, user_id, text):
		with open(file.name, 'r') as file_to_read:
			users = file_to_read.readlines()
		if any(self.user_id in line for line in users):
			for line in users:
				if self.user_id in line:
					line = line[:-1] + f',{user_id}\n'
		else:
			users.append('{}:{}\n'.format(self.user_id, user_id))
		file.write(''.join(users))
		if self.new_messages.get(user_id):
			self.new_messages[user_id].append(text)
		else:
			self.new_messages.update({user_id: [text]})
		self.logger.info('add_user; add: {}'.format({'user_id': user_id, 'new_user': user_id in users.split(';')}))


	@func_implementer
	def stop_bot(self):
		self.thread_bot.flag = False
		self.thread_bot = None
		self.new_messages = {}
		self.logger.info('Stop bot work')


	@func_implementer
	def check_new_messages(self):
		if len(self.new_messages) == 0:
			info_return = 'У вас нет новых сообщений.'
		else:
			info_return = f'У вас {len(self.new_messages)} новых сообщений.'
		self.logger.info('check_new_messages; return {}'.format({'user_id': self.user_id, 'info_return': info_return}))
		return info_return