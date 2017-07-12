from flask import Flask
from flask import request
import logging
from logging.handlers import RotatingFileHandler
import vk_api
import sqlite3
import re
import subprocess
from k  import get_exam_results, DEVELOER_INFO, WELCOME_TEXT, \
COMMAND_TEXT, WRONG_INFO, WRONG_WRITTEN, REGISTER_TEXT, ALREADY_REGISTRED, \
OK_NOW_IS, secret_token, RE_FORM_MATCH, NOTIFICATIONS_TURNED_OFF


#Setting up DB-connection, logging and VK-API-connection
def log_db():
	return curs.execute("select * from userdata").fetchall()

conn = sqlite3.connect(r"/root/temp.db")
curs = conn.cursor()

handler = RotatingFileHandler('/var/log/myproject/server.log')
formatter = logging.Formatter("%(asctime)s %(message)s", '%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)

pub = vk_api.VkApi(token = secret_token)
pub_api = pub.get_api()

app = Flask(__name__)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

#reacting on incoming message
def process_message(msg):
	POSTFIX = " where user_id="+str(msg["user_id"])
	user_step = curs.execute("select enabled from userdata "+ POSTFIX).fetchall()[0][0]
	app.logger.info('USER_STEP(ENABLED) IS'+ str(user_step))
	if msg["body"]=="команды":
		pub_api.messages.send(user_id=msg["user_id"], message=COMMAND_TEXT)
	elif msg["body"]=="1" or user_step==1:
		if user_step==4:
			pub_api.messages.send(user_id=msg["user_id"], message=ALREADY_REGISTRED)
		elif user_step==0:
			pub_api.messages.send(user_id=msg["user_id"], message=REGISTER_TEXT)
			curs.execute("update userdata set enabled=1 "+ POSTFIX)
			conn.commit()

		elif user_step==1:
			app.logger.debug(log_db())
			#check_1
			if re.match(RE_FORM_MATCH, msg['body']):
				#check_2
				o = re.match(RE_FORM_MATCH, msg['body']).groupdict()
				m = get_exam_results(o)
				if m != False:
					pub_api.messages.send(user_id=msg["user_id"], message=OK_NOW_IS % m[0])
					curs.execute("update userdata set enabled=4 "+ POSTFIX)
					for k in o.keys():
						curs.execute("update userdata set "+k+" = '"+o[k]+"' "+ POSTFIX)
					curs.execute("update userdata set hash='"+m[1]+"' "+ POSTFIX)
					conn.commit()
				else:
					pub_api.messages.send(user_id=msg["user_id"], message=WRONG_INFO)
			else:
				pub_api.messages.send(user_id=msg["user_id"], message=WRONG_WRITTEN)

		else:
			pub_api.messages.send(user_id=msg["user_id"], message=REGISTER_TEXT)
			curs.execute("update userdata set enabled=2 "+POSTFIX)
			conn.commit()
		app.logger.debug(log_db())
	elif msg["body"]=="2":
		if user_step==1 or user_step==4 :
			curs.execute("update userdata set Lastname='', Name='', idnomer = '', enabled=0, hash='' "+POSTFIX)
			conn.commit()
		pub_api.messages.send(user_id=msg["user_id"], message=NOTIFICATIONS_TURNED_OFF+COMMAND_TEXT)
	elif msg["body"]=="3":
		pub_api.messages.send(user_id=msg["user_id"], message=DEVELOER_INFO + COMMAND_TEXT)
	elif msg["body"] in ['checker log','checker logging','чекер лог','checker logs','лог чекер','log checker'] and msg["user_id"]==64946461:
		proc = subprocess.Popen(['tail','-n','50','/var/log/myproject/checker.log'], stdout=subprocess.PIPE)
		pub_api.messages.send(user_id=msg["user_id"], message=proc.stdout.read())
		del proc
	elif msg["body"] in ['server log','server logging','сервер лог','server logs','лог сервер','log server'] and msg["user_id"]==64946461:
		proc = subprocess.Popen(['tail','-n','50','/var/log/myproject/server.log'], stdout=subprocess.PIPE)
		pub_api.messages.send(user_id=msg["user_id"], message=proc.stdout.read())
		del proc


#first meeting
def hello(msg):
	try:
		curs.execute("insert into userdata values ("+str(msg["user_id"])+",1,'','','',0,'')")
		conn.commit()
	except sqlite3.IntegrityError as e:
		pass
	app.logger.debug(log_db())
	pub_api.messages.send(user_id=msg["user_id"], message=WELCOME_TEXT+COMMAND_TEXT)

#reacting for disabling messages
def remove(id):
	curs.execute("delete from userdata where user_id="+str(id))
	conn.commit()

#main cycle
@app.route('/', methods=['POST', 'GET'])
def hello_world():
	if request.method == 'POST':
		data = request.get_json()
		app.logger.info("REQUEST:"+data["type"])
		app.logger.info("DATA:"+str(data))
		app.logger.debug("database is"+str(curs.execute("select * from userdata").fetchall()))
		
		if data["type"]=="message_new":
			process_message(data['object'])
		elif data["type"]=="message_allow":
			hello(data['object'])
		elif data["type"]=="message_deny":
			remove(data['object']["user_id"])
		return "ok"
	else:
		return "Well, it's not so good"
