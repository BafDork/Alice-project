from additional_content import abilities, get_suggests, get_logger
from telegram_bot.class_telegram_bot import Telegram_Bot
from vk_bot.class_vk_bot import Vk_Bot
from flask_ngrok import run_with_ngrok
from flask import Flask, request
import json, os


app = Flask(__name__)
run_with_ngrok(app)
sessionStorage = {}
logger = get_logger('alice_logger', 'logfile.log')


@app.route('/post', methods=['POST'])
def main():
	logger.info(f'Request: {request.json!r}')
	response = {'session': request.json['session'],
				'version': request.json['version'],
				'response': {'end_session': False}}
	handle_dialog(request.json, response)
	logger.info(f'Response:  {response!r}')
	return json.dumps(response)


def handle_dialog(req, res):
	user_message =  req['request']['original_utterance'].lower()
	user_id = req['session']['user_id']
	if req['session']['new']:
		sessionStorage[user_id] = {'vk_bot': {'bot': Vk_Bot(get_logger('vk_bot_logger', 'vk_bot/logfile.log'), req, res)},
								   'telegram_bot': {'bot': Telegram_Bot(get_logger('telegram_bot_logger', 'telegram_bot/logfile.log'), req, res)}}
		sessionStorage[user_id]['vk_bot']['bot'].check_saved_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		sessionStorage[user_id]['telegram_bot']['bot'].check_saved_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		if not sessionStorage[user_id]['vk_bot']['bot'].bot and not sessionStorage[user_id]['telegram_bot']['bot'].bot:
			res['response']['text'] = ('Привет, с моей помощью вы сможешь управлять своими ботами.\n' +
									   'Чтобы узнать мои возможности напишите: "Что ты умеешь"')
		return
	sessionStorage[user_id]['vk_bot']['bot'].update_arg(req, res)
	sessionStorage[user_id]['telegram_bot']['bot'].update_arg(req, res)
	if user_message == 'что ты умеешь':
		res['response']['text'] = '\n'.join(abilities)

	elif user_message == 'отменить добавление':
		if sessionStorage[user_id]['vk_bot']['bot'].add_flag or sessionStorage[user_id]['telegram_bot']['bot'].add_flag:
			sessionStorage[user_id]['vk_bot']['bot'].add_flag, sessionStorage[user_id]['telegram_bot']['bot'].add_flag = False, False
			res['response']['text'] = 'Выполнено.'
		else:
			res['response']['text'] = 'Вы не добавляете бота.'

	elif any(f'добавь бота {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message and not sessionStorage[user_id]['vk_bot']['bot'].bot:
			sessionStorage[user_id]['vk_bot']['bot'].add_flag = True
			res['response']['text'] = 'Введите token бота и id группы: "token={}; group_id={}"'
		elif 'телеграмм' in user_message and not sessionStorage[user_id]['telegram_bot']['bot'].bot:
			sessionStorage[user_id]['telegram_bot']['bot'].add_flag = True
			res['response']['text'] = 'Введите token бота: "token={}"'
		else:
			res['response']['text'] = 'У вас уже добавлен бот.'

	elif sessionStorage[user_id]['vk_bot']['bot'].add_flag or sessionStorage[user_id]['telegram_bot']['bot'].add_flag:
		if sessionStorage[user_id]['vk_bot']['bot'].add_flag:
			sessionStorage[user_id]['vk_bot']['bot'].add_bot()
		elif sessionStorage[user_id]['telegram_bot']['bot'].add_flag:
			sessionStorage[user_id]['telegram_bot']['bot'].add_bot()

	elif any(f'измени бота {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
			sessionStorage[user_id]['vk_bot']['bot'].bot, sessionStorage[user_id]['vk_bot']['bot'].add_flag = None, True
			if res['response']['text'] == 'Выполнено.':
				res['response']['text'] = 'Ваше сохранение было удалено.'
			res['response']['text'] += ' Введите token бота и id группы: "token={}; group_id={}"'
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
			sessionStorage[user_id]['telegram_bot']['bot'].bot, sessionStorage[user_id]['telegram_bot']['bot'].add_flag = None, True
			if res['response']['text'] == 'Выполнено.':
				res['response']['text'] = 'Ваше сохранение было удалено.'
			res['response']['text'] += ' Введите token бота: "token={}"'

	elif any(f'запомни бота {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message and not sessionStorage[user_id]['vk_bot']['bot'].save_flag:
			sessionStorage[user_id]['vk_bot']['bot'].save_bot([os.path.join('top_secret', 'users_bots.txt'), 'a+'])
		elif 'телеграмм' in user_message and not sessionStorage[user_id]['telegram_bot']['bot'].save_flag:
			sessionStorage[user_id]['telegram_bot']['bot'].save_bot([os.path.join('top_secret', 'users_bots.txt'), 'a+'])
		else:
			res['response']['text'] = 'Ваш бот уже был сохранен.'

	elif any(f'забудь бота {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message and sessionStorage[user_id]['vk_bot']['bot'].save_flag:
			sessionStorage[user_id]['vk_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		elif 'телеграмм' in user_message and sessionStorage[user_id]['telegram_bot']['bot'].save_flag:
			sessionStorage[user_id]['telegram_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		else:
			res['response']['text'] = 'Ваш бот не был сохранен.'

	elif any(f'запусти бота {key}' == user_message for key in ['вк', 'телеграмм']):	
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].start_bot()
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].start_bot()

	elif any(f'останови бота {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].stop_bot()
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].stop_bot()

	elif any(f'проверь новые сообщения в {key}' == user_message for key in ['вк', 'телеграмм']):
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].check_new_messages()
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].check_new_messages()

	elif any(f'ответь всем в {key}' == user_message.split(':')[0] for key in ['вк', 'телеграмм']):
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].answer_messages()
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].answer_messages()
	elif any(f'напиши всем в {key}' == user_message.split(':')[0] for key in ['вк', 'телеграмм']):
		if 'вк' in user_message:
			sessionStorage[user_id]['vk_bot']['bot'].write_all_users([os.path.join('top_secret', 'vk_users.txt'), 'r'])
		elif 'телеграмм' in user_message:
			sessionStorage[user_id]['telegram_bot']['bot'].write_all_users([os.path.join('top_secret', 'telegram_users.txt'), 'r'])

	else:
		res['response']['text'] = 'Извините я такого не умею.'
	res['response']['buttons'] = get_suggests(user_message)


if __name__ == '__main__':
	app.run()