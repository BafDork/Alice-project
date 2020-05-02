import logging, sys, os


FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
abilities = ['В месте {} выберите один вариант из предложенного списка.'
			 'Добавление бота: "Добавь бота {вк или телеграмм}"',
			 'Изменить добавленные данные бота: "Измени бота {вк или телеграмм}"',
			 'Сохранение данных о боте: "Запомни бота {вк или телеграмм}"',
			 'Удаление данных о боте: "Забудь бота {вк или телеграмм}"',
			 'Активация добавленного бота: "Запусти бота {вк или телеграмм}"',
			 'Деактивация добавленного бота: "Останови бота {вк или телеграмм}"',
			 'Отменить добавление бота: "Отменить добавление"',
			 'Проверка новых сообщений с момента запуска навыка: "Проверь новые сообщения в {вк или телеграмм}"',
			 'Ответить на все новые сообщения: "Ответь всем в {вк или телеграмм}: {текст сообщения}"',
			 'Написать всем пользователям приложения: "Напиши всем в {вк или телеграмм}: {текст сообщения}"']


def get_suggests(message):
	message_suggest = {'что ты умеешь': ['Добавь бота вк', 'Добавь бота вк'],
					   'отменить добавление': ['Добавь бота вк', 'Добавь бота вк', 'Что ты умеешь'], 
					   'измени бота вк': ['Отменить добавление'],
					   'добавь бота вк': ['Отменить добавление'],
					   'запомни бота вк': ['Запусти бота вк', 'Забудь бота вк', 'Измени бота вк'], 
					   'запусти бота вк': ['Проверь новые сообщения в вк', 'Останови бота вк'], 
					   'забудь бота вк': ['Запомни бота вк'], 
					   'останови бота вк': ['Запусти бота вк', 'Измени бота вк'],
					   'измени бота телеграмм': ['Отменить добавление'],
					   'добавь бота телеграмм': ['Отменить добавление'],
					   'запомни бота телеграмм': ['Запусти бота телеграмм', 'Забудь бота телеграмм', 'Измени бота телеграмм'], 
					   'запусти бота телеграмм': ['Проверь новые сообщения в телеграмм', 'Останови бота телеграмм'], 
					   'забудь бота телеграмм': ['Запомни бота телеграмм'], 
					   'останови бота телеграмм': ['Запусти бота телеграмм', 'Измени бота телеграмм']}
	if message_suggest.get(message):
		suggests = [{'title': suggest, 'hide': True}
					for suggest in message_suggest[message]]
		return suggests


def get_console_handler():
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(FORMATTER)
	return console_handler


def get_file_handler(log_file):
	os.system(r'nul>{}'.format(log_file))
	file_handler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight')
	file_handler.setFormatter(FORMATTER)
	return file_handler


def get_logger(logger_name, log_file):
	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.DEBUG)
	#logger.addHandler(get_console_handler())
	logger.addHandler(get_file_handler(log_file))
	logger.propagate = False
	return logger