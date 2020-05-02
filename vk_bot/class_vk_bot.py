from class_bot_father import Bot_Father
from additional_content import get_logger
import threading, vk_api, random, os
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType



class Vk_Bot(Bot_Father):


	def __init__(self, logger, req, res):
		self.logger = logger
		super().__init__()
		super().update_arg(req, res)


	@Bot_Father.open_file
	def check_saved_bot(self, file):
		for line in file.readlines():
			if self.user_id in line:
				if len(line.split(';')) == 3:
					self.bot = {'token': line.split(';')[1], 'group_id': line[:-1].split(';')[2]}
					self.res['response']['text'] = 'У вас уже доваблен бот.\n Чтобы активировать своего бота напишите: Запусти бота {"вк" или "телеграмм"}'
					self.save_flag = True
					self.logger.info('check_saved_bot; successful_add: {}'.format(self.user_id))


	def start_bot_work(self, TOKEN, group_id):
		try:
			self.logger.info('Starting bot work')
			vk_session = vk_api.VkApi(token=TOKEN)
			longpoll = VkBotLongPoll(vk_session, group_id)
			self.logger.info('Successfully connecting to group. Waiting for messages')
			for event in longpoll.listen():
				if not getattr(threading.currentThread(), 'flag', True):
					threading.currentThread().join()
				elif event.type == VkBotEventType.MESSAGE_NEW:
					self.logger.info(f'Get; message: {event}')
					self.network = vk_session.get_api()
					super().add_user_info([os.path.join('top_secret', 'vk_users.txt'), 'w'], event.obj.message['from_id'], event.obj.message['text'])
					self.network.messages.send(user_id=event.obj.message['from_id'],
										  message=f'{self.network.users.get(user_id=event.obj.message["from_id"])[0]["first_name"]}, мы вам скоро ответим.',
										  random_id=random.randint(0, 2 ** 64))
					self.logger.info('start_vk_bot; message: {}'.format({'user_id': event.obj.message["from_id"],
										'text': {f'{self.network.users.get(user_id=event.obj.message["from_id"])[0]["first_name"]}, мы вам скоро ответим.'}}))
		except Exception as error:
			self.logger.error(f'Error; start_bot_work: {error}')


	@Bot_Father.func_implementer
	def answer_messages(self):
		for user_id in self.new_messages:
			self.network.messages.send(user_id=user_id,
							 message=self.user_message.split(':')[1],
							 random_id=random.randint(0, 2 ** 64))
			self.logger.info('answer_messages; message: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))


	@Bot_Father.open_file
	@Bot_Father.func_implementer
	def write_all_users(self, file):
		users = file.readlines()
		for line in users:
			if self.user_id in line:
				for user_id in line[:-1].split(':')[1].split(','):
					self.network.messages.send(user_id=user_id,
											   message=self.user_message.split(':')[1],
											   random_id=random.randint(0, 2 ** 64))
					self.logger.info('write_all_users; message: {}'.format({'user_id': user_id, 'text': self.user_message.split(':')[1]}))