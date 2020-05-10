from additional_content import abilities, get_suggests, get_logger, users_bots
from telegram_bot.class_telegram_bot import Telegram_Bot
from vk_bot.class_vk_bot import Vk_Bot
from flask_ngrok import run_with_ngrok
from flask import Flask, request
import json, re


app = Flask(__name__)
run_with_ngrok(app)
sessionStorage, logger = {}, get_logger('alice_logger', 'logfile.log')


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
	user_message, user_id =  req['request']['original_utterance'].lower(), req['session']['user_id']
	if req['session']['new']:
		sessionStorage[user_id] = {'vk_bot': {'bot': Vk_Bot(get_logger('vk_bot_logger', 'vk_bot/logfile.log'), req, res)},
								   'telegram_bot': {'bot': Telegram_Bot(get_logger('telegram_bot_logger', 'telegram_bot/logfile.log'), req, res)}}
		sessionStorage[user_id]['vk_bot']['bot'].check_saved_bot(users_bots, 'r')
		sessionStorage[user_id]['telegram_bot']['bot'].check_saved_bot(users_bots, 'r')
		if not sessionStorage[user_id]['vk_bot']['bot'].bot and not sessionStorage[user_id]['telegram_bot']['bot'].bot:
			res['response']['text'] = ('Привет, с моей помощью вы сможешь управлять своими ботами.\n'
									   'Чтобы узнать мои возможности напишите: "Что ты умеешь"')
			res['response']['buttons'] = get_suggests('new_user')
		return
	vk_bot, telegram_bot = sessionStorage[user_id]['vk_bot']['bot'], sessionStorage[user_id]['telegram_bot']['bot']
	vk_bot.update_arg(req, res)
	telegram_bot.update_arg(req, res)
	if user_message == 'что ты умеешь':
		res['response']['text'] = '\n'.join(abilities)

	elif user_message == 'отменить добавление':
		if vk_bot.add_flag or telegram_bot.add_flag:
			vk_bot.add_flag, telegram_bot.add_flag = False, False
			res['response']['text'] = 'Выполнено.'
		else:
			res['response']['text'] = 'Вы не добавляете бота.'

	elif re.search(r'добавь бота (вк|телеграмм)', user_message):
		if 'вк' in user_message and not vk_bot.bot:
			vk_bot.add_flag = True
			res['response']['text'] = 'Введите token бота и id группы: "token={}; group_id={}"'
		elif 'телеграмм' in user_message and not telegram_bot.bot:
			telegram_bot.add_flag = True
			res['response']['text'] = 'Введите token бота: "token={}"'
		else:
			res['response']['text'] = 'У вас уже добавлен бот.'

	elif vk_bot.add_flag or telegram_bot.add_flag:
		if vk_bot.add_flag:
			vk_bot.add_bot()
			res['response']['buttons'] = get_suggests('завершение добавления бота вк')
		elif telegram_bot.add_flag:
			telegram_bot.add_bot()
			res['response']['buttons'] = get_suggests('завершение добавления бота телеграмм')

	elif re.search(r'измени бота (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.delete_bot(users_bots, 'r')
			vk_bot.bot, vk_bot.add_flag = None, True
			if res['response']['text'] == 'Выполнено.':
				res['response']['text'] = 'Ваше сохранение было удалено.'
			res['response']['text'] += ' Введите token бота и id группы: "token={}; group_id={}"'
		elif 'телеграмм' in user_message:
			telegram_bot.delete_bot(users_bots, 'r')
			telegram_bot.bot, telegram_bot.add_flag = None, True
			if res['response']['text'] == 'Выполнено.':
				res['response']['text'] = 'Ваше сохранение было удалено.'
			res['response']['text'] += ' Введите token бота: "token={}"'

	elif re.search(r'запомни бота (вк|телеграмм)', user_message):
		if 'вк' in user_message and not vk_bot.save_flag:
			vk_bot.save_bot(users_bots, 'a+')
		elif 'телеграмм' in user_message and not telegram_bot.save_flag:
			telegram_bot.save_bot(users_bots, 'a+')
		else:
			res['response']['text'] = 'Ваш бот уже был сохранен.'

	elif re.search(r'забудь бота (вк|телеграмм)', user_message):
		if 'вк' in user_message and vk_bot.save_flag:
			vk_bot.delete_bot(users_bots, 'r')
		elif 'телеграмм' in user_message and telegram_bot.save_flag:
			telegram_bot.delete_bot(users_bots, 'r')
		else:
			res['response']['text'] = 'Ваш бот не был сохранен.'

	elif re.search(r'запусти бота (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.start_bot()
		elif 'телеграмм' in user_message:
			telegram_bot.start_bot()

	elif re.search(r'останови бота (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.stop_bot()
		elif 'телеграмм' in user_message:
			telegram_bot.stop_bot()

	elif re.search(r'активируй автоответ бота (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.enable_auto_answer()
		elif 'телеграмм' in user_message:
			telegram_bot.enable_auto_answer()

	elif re.search(r'отключи автоответ бота (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.disable_auto_answer()
		elif 'телеграмм' in user_message:
			telegram_bot.disable_auto_answer()

	elif re.search(r'проверь новые сообщения в (вк|телеграмм)', user_message):
		if 'вк' in user_message:
			vk_bot.check_new_messages()
		elif 'телеграмм' in user_message:
			telegram_bot.check_new_messages()

	elif re.search(r'ответь всем в (вк|телеграмм):', user_message):
		if 'вк' in user_message:
			vk_bot.answer_messages()
		elif 'телеграмм' in user_message:
			telegram_bot.answer_messages()

	elif re.search(r'напиши всем в (вк|телеграмм):', user_message):
		if 'вк' in user_message:
			vk_bot.write_all_users()
		elif 'телеграмм' in user_message:
			telegram_bot.write_all_users()

	elif re.search(r'запланируй через \d+ мин (написать)|(ответить) всем в (вк|телеграмм):', user_message):
		if 'вк' in user_message:
			vk_bot.planned_mailing_list('vk')
		elif 'телеграмм' in user_message:
			telegram_bot.planned_mailing_list('telegram')

	else:
		res['response']['text'] = 'Извините я такого не умею.'

	res['response']['buttons'] = get_suggests(user_message)


if __name__ == '__main__':
	app.run()