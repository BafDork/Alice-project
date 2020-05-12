from additional_content import get_logger, users_bots
import threading, os, re


class Bot_Father():


	def __init__(self):
		self.thread_plain, self.thread_bot, self.bot, self.network = None, None, None, None
		self.add_flag, self.save_flag, self.auto_answer = False, False, True
		self.new_messages, self.plain = {}, {'vk': {}, 'telegram': {}}


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
		def decorator(self, file_name, tipe, *data):
			with open(file_name, tipe) as file:
				func(self, file, *data)
		return decorator


	def update_arg(self, req, res):
		self.user_message, self.user_id = req['request']['original_utterance'], req['session']['user_id']
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
		bots = file.readlines()
		for line in bots:
			if all(key in [self.user_id, self.bot['token'], self.bot.get('group_id', True)] for key in line.replace('\n', '').split(';')):
				os.system(r'nul>{}'.format(users_bots))
				bots.remove(line)
				with open(users_bots, 'w') as file_to_write:
					file_to_write.write(''.join(bots))
				self.save_flag = False
				self.logger.info('delete_bot; remove: {}'.format(self.user_id))
				return


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
		self.logger.info('add_user; add: {}'.format({'user_id': user_id}))


	@func_implementer
	def stop_bot(self):
		self.thread_bot.flag, self.thread_bot, self.new_messages = False, None, {}
		self.logger.info('Stop bot work')


	@func_implementer
	def enable_auto_answer(self):
		if self.auto_answer:
			return 'Автоответ уже активирован'
		self.auto_answer = True
		self.logger.info('Enable auto answer')

	@func_implementer
	def disable_auto_answer(self):
		if not self.auto_answer:
			return 'Автоответ уже отключен'
		self.auto_answer = False
		self.logger.info('Disable auto answer')


	@func_implementer
	def check_new_messages(self):
		if len(self.new_messages) == 0:
			info_return = 'У вас нет новых сообщений.'
		else:
			info_return = f'У вас {len(self.new_messages)} новых сообщений.'
		self.logger.info('check_new_messages; return {}'.format({'user_id': self.user_id, 'info_return': info_return}))
		return info_return


	@func_implementer
	def planned_mailing_list(self, bot):
		timer = re.search(r'\d+', r'{}'.format(self.user_message))
		self.logger.info(timer)
		if 'написать всем' in self.user_message:
			self.plain[bot]['write'] = self.user_message.split(':')[1]
			self.logger.info(timer)
			self.thread_plain = threading.Timer(int(timer[0]) * 60, self.write_all_users)
		elif 'ответить всем' in self.user_message:
			self.plain[bot]['answer'] = self.user_message.split(':')[1]
			self.thread_plain = threading.Timer(int(timer[0]) * 60, self.answer_messages)
		self.logger.info('planned_mailing_list; plain: {}'.format({'time': timer[0]}))
		self.thread_plain.start()