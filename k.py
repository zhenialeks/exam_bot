#!python3

import requests
import bs4
import hashlib
from secret import secret_tok

secret_token=secret_tok
DEVELOER_INFO="""
разработчик — https://vk.com/id64946461 
версия 1.0
"""
RE_FORM_MATCH = r"(?P<Lastname>[А-ЯЁ][а-яё]{0,50}) (?P<Name>[А-ЯЁ][а-яё]{0,50}) (?P<idnomer>\d{4}-\d{4}-\d{4})"

WELCOME_TEXT="""
Здравствуйте! Я бот—уведомитель о результатах ЕГЭ.
"""

COMMAND_TEXT="""
команды для бота:

1 — подключить уведомления о результатах ЕГЭ с сайти НИМРО (только для Новосибирска)
2 — отключить уведомления
3 — информация о разработчике
команды — вывод всех команд
"""

NOTIFICATIONS_TURNED_OFF="""
оповещения отключены.
"""

REGISTER_TEXT="""
Для того, чтобы получать уведомления введите свои данные в следующем формате:

<Фамилия> <Имя> <Код>

Например, 
"Иванов Иван 1234-5678-9012" (без ковычек)

"""
ALREADY_REGISTRED="""
Вы уже ввели данные. Мы вышлем вам уведомление как только появится что-то новое!
"""
WRONG_WRITTEN="""
Введёные вами данные несоответствуют необходимому формату. Попробуйте ещё раз или введите "2"
"""
WRONG_INFO="""
В системе нет такого пользователя. Проверьте введёные данные и попробуйте ещё раз или введите "2"
"""
OK_NOW_IS="""
На данный момент в системе есть следующие данные:
%s

Как только появятся изменения, мы вам сообщим
"""

def get_exam_results(id_data):
	url = "http://nscm.ru/egeresult/tablresult.php"
	
	hh = {"Host":"nscm.ru",
	"Connection":"keep-alive",
	"Content-Length":"146",
	"Origin":"http://nscm.ru",
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
	"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
	"Accept":"text/html, */*; q=0.01",
	"X-Requested-With":"XMLHttpRequest",
	"Referer":"http://nscm.ru/egeresult/",
	"Accept-Encoding":"gzip, deflate",
	"Accept-Language":"ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"}
	
	exams = []
	
	kk = requests.post(url, data = id_data, headers = hh)
	
	doc =  bs4.BeautifulSoup(kk.content.decode(), "html.parser")
	if not doc.h2:
		return False
	exams.append(doc.h2.text)
	
	for i in doc.find_all('tr')[1:]:
		exams.append([i.find_all("td")[j].text for j in range(3)])
	
	exam_text = ""
	for i in exams[1:]:
		for j in i:
			exam_text += j 
			exam_text += " | "
		exam_text += "\n"
	
	hash_now = hashlib.md5(str(exam_text).encode("utf-8")).hexdigest()

	return (exam_text, hash_now)