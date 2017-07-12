import sqlite3
from k  import get_exam_results, secret_token
import vk_api
import hashlib
import logging

logging.basicConfig(filename="/var/log/myproject/checker.log", format="%(asctime)s %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
logging.info(r"____________checking____________")

conn = sqlite3.connect(r"/root/temp.db")
curs = conn.cursor()

pub = vk_api.VkApi(token = secret_token)
api = pub.get_api()

for user in curs.execute("select user_id, Lastname, Name, idnomer, hash from userdata where enabled=4").fetchall():
	logging.debug("-user"+str(user))
	res = get_exam_results(
		{"Lastname":user[1],
		"Name":user[2],
		"idnomer":user[3]})
	if res[1] == user[4]:
		pass #nothing has been changed
		logging.info("<nothing new>")
	else:
		curs.execute(" update userdata set hash ='"+hashlib.md5(str(res[0]).encode("utf-8")).hexdigest()+"' where user_id='"+user[0]+"'")
		conn.commit()
		api.messages.send(user_id=user[0], message = "Смотри, что-то изменилось: \n" + res[0])
		logging.info("here're some changes" + res[0])
logging.info(r"____________ending____________")
conn.close()