from additional_content import abilities, get_suggests, get_logger
from vk_bot.class_vk_bot import Vk_Bot
from flask_ngrok import run_with_ngrok
import threading, logging, json, os
from flask import Flask, request


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
		sessionStorage[user_id] = {'vk_bot': {'bot': Vk_Bot(), 'add_flag': False, 'save_flag': False},
								   'telegram_bot': {'add_flag': False, 'save_flag': False}}
		sessionStorage[user_id]['vk_bot']['bot'].update_arg(req, res)
		sessionStorage[user_id]['vk_bot']['bot'].check_saved_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		if not sessionStorage[user_id]['vk_bot']['bot'].bot: ####################################################################################### and telegram_bot.bot:
			res['response']['text'] = ('Привет, с моей помощью вы сможешь управлять своими ботами.\n' +
									   'Чтобы узнать мои возможности напишите: "Что ты умеешь"')
		return
	sessionStorage[user_id]['vk_bot']['bot'].update_arg(req, res)
	if user_message == 'что ты умеешь':
		res['response']['text'] = '\n'.join(abilities)

	elif user_message == 'отменить добавление':
		if sessionStorage[user_id]['vk_bot']['add_flag'] or sessionStorage[user_id]['telegram_bot']['add_flag']:
			sessionStorage[user_id]['vk_bot']['add_flag'], sessionStorage[user_id]['telegram_bot']['add_flag'] = False, False
			res['response']['text'] = 'Выполнено.'
		else:
			res['response']['text'] = 'Вы не добавляете бота.'

	elif user_message == 'добавь бота вк':
		if not sessionStorage[user_id]['vk_bot']['bot'].bot:
			sessionStorage[user_id]['vk_bot']['add_flag'] = True
			res['response']['text'] = 'Введите token бота и id группы: "token={}; group_id={}"'
		else:
			res['response']['text'] = 'У вас уже добавлен вк бот.'

	elif sessionStorage[user_id]['vk_bot']['add_flag']:
		sessionStorage[user_id]['vk_bot']['bot'].add_bot()
		sessionStorage[user_id]['vk_bot']['add_flag'] = False

	elif user_message == 'измени бота вк':
		sessionStorage[user_id]['vk_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])
		if res['response']['text'] == 'Выполнено.':
			res['response']['text'] = 'Ваше сохранение было удалено.'
		sessionStorage[user_id]['vk_bot']['bot'].bot, sessionStorage[user_id]['vk_bot']['add_flag'] = None, True
		res['response']['text'] += ' Введите token бота и id группы: "token={}; group_id={}"'

	elif user_message == 'запомни бота вк':
		sessionStorage[user_id]['vk_bot']['bot'].save_bot([os.path.join('top_secret', 'users_bots.txt'), 'a+'])

	elif user_message == 'забудь бота вк':
		sessionStorage[user_id]['vk_bot']['bot'].delete_bot([os.path.join('top_secret', 'users_bots.txt'), 'r'])

	elif user_message == 'запусти бота вк':
		sessionStorage[user_id]['vk_bot']['bot'].start_bot()

	elif user_message == 'останови бота вк':
		sessionStorage[user_id]['vk_bot']['bot'].stop_bot()

	elif user_message == 'проверь новые сообщения в вк':
		sessionStorage[user_id]['vk_bot']['bot'].check_new_messages()

	elif 'ответь всем в вк' == user_message.split(':')[0]:
		sessionStorage[user_id]['vk_bot']['bot'].answer_messages()

	elif 'напиши всем в вк' == user_message.split(':')[0]:
		sessionStorage[user_id]['vk_bot']['bot'].write_all_users(['top_secret/users.txt', 'r'])

	else:
		res['response']['text'] = 'Извините я такого не умею.'
	res['response']['buttons'] = get_suggests(user_message)


if __name__ == '__main__':
	app.run()