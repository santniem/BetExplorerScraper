import socket
from pymongo import MongoClient,ASCENDING,DESCENDING
from flask import Flask, render_template,jsonify
from flask_table import Table, Col, LinkCol
from datetime import datetime
from time import gmtime, strftime
from flask_socketio import SocketIO
from threading import Thread,Event
import time
import json
#flask+socket
app = Flask(__name__)
socketio = SocketIO(app)
#Mongo Connection
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
client = MongoClient('mongodb+srv://user:pass@cluster0-zypbs.mongodb.net/test')
db = client.get_database('test')
bets = db.Bets

#missä kaikkialla mul on accountit
myBookies=["Betway",
"Pinnacle",
"bet365",
"William Hill",
"Betvictor",
"Betfair",
"Unibet","ComeOn"]

class ItemTable(Table):
	URL = Col('URL')
	Margin = Col('Margin')
	BetType = Col("BetType")
	bookies1 = Col("Home")
	bookies2= Col("Away")

# Get some objects
class Item(object):
	def __init__(self, URL, Margin,BetType,bookies1,bookies2):
		self.URL =URL
		self.Margin = Margin
		self.BetType = BetType
		self.bookies1=bookies1
		self.bookies2=bookies2


@app.route('/666/')
async def testi():
	jiison()


@app.route('/index')
def update():
	aika = datetime.now().strftime('%H:%M')
	lista=[]
	items= bets.find({"Active":1,"Time":{"$gt":aika}}).sort("Margin",DESCENDING)
	for each in items:
		bookies1=list(each["Bookie 1"]["Bookies"].keys())
		bookies2=list(each["Bookie 2"]["Bookies"].keys())
		lista.append(Item(each["URL"],each["Margin"],each["BetType"],bookies1,bookies2))
	table = ItemTable(lista)
	return table.__html__()

@app.route('/json')
def jiison():
	aika = datetime.now().strftime('%H:%M')
	lista=[]
	items= bets.find({"Active":1,"Time":{"$gt":aika}}).sort("Margin",DESCENDING)
	for each in items:
			del each['_id']
			lista.append(each)
	return jsonify(lista)



def updateSite():
	#this is where the magic happens
	aika = datetime.now().strftime('%H:%M')
	items= bets.find({"Active":1,"Margin":{"$gt":2},"Time":{"$gt":aika}}).sort("Margin",DESCENDING)#,"Time":{"$gt":aika}}
	for each in items:
		bookies1=list(each["Bookie 1"]["Bookies"].keys())
		bookies2=list(each["Bookie 2"]["Bookies"].keys())
		true1 = truer(bookies1)
		true2 = truer(bookies2)
		
		if(true1 == True and true2 == True):
			del each['_id']
			del each["lastModified"]
			print("asd")
			socketio.emit('newnumber', json.dumps(each), namespace='/test')
			
def truer(ee):
    for each in ee:
    	if each in myBookies:
    		return True


@socketio.on('connect', namespace='/test')
def test_connect():
	#pitää tietää threadin olemassaolosta tai muuten homma kusee
	global thread
	print('Client connected')
	if not thread.isAlive():
        
		thread = updater()
		thread.start()
		print("Starting Thread")


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')		

@app.route('/')
def index():
    #socketIO html
    return render_template('index.html')

#Threadi joka updatee listaa paskoista	
class updater(Thread):#
	def __init__(self):
		Thread.__init__(self)
	def run(self):
		while True:
				
			updateSite()
			time.sleep(30)
#dunno mitä tekee ilmeisesti ctrl+c pysäytysjuttu			
thread = Thread()
thread_stop_event = Event()

if __name__ == "__main__":
	socketio.run(app)