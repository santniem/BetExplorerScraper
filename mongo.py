from pymongo import MongoClient
from arbing import getUrlsByGame,creativeMethodName
import arbing
import datetime
from selenium import webdriver
import time
import threading


client = MongoClient('mongodb+srv://user:pass@cluster0-zypbs.mongodb.net/test')
db = client.get_database('test')
bets = db.Bets

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--log-level=3")
tmp,tmp2,Urls=getUrlsByGame()


def getter():
	tmpUrls=[]
	for each in Urls:
		checkTime=time.strptime(each[0],"%H:%M")
		asd = datetime.datetime.now()
		if(checkTime[3]>asd.hour and checkTime[3]<asd.hour + 3) :
			tmpUrls.append(each[1])
	
	return tmpUrls

def xHourArbs():
	driver = webdriver.Chrome(options=options)
	tmpurls=getter()
	creativeMethodName(driver,tmpurls,'pepe')
	print("byebye x")
		

def updater():
	driver = webdriver.Chrome(options=options)
	urlsToBeUpdated=[]
	asd = bets.find({"Active":1})
	for each in asd:
		urlsToBeUpdated.append(each["URL"])
	creativeMethodName(driver,urlsToBeUpdated,'updater')
	print("byebye updater")
	
def updaterUpdater():
	driver = webdriver.Chrome(options=options)
	urlsToBeUpdated=[]
	listOfDicts = bets.find({"Active":1})
	arbing.matchUpdater(listOfDicts,driver)
	


class GetAll(threading.Thread):#
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while True:
			arbing.main(Urls)
			time.sleep(1000)
		
class GetGamesNearNow(threading.Thread):#
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while True:
			xHourArbs()
			time.sleep(300)

class updaterThread(threading.Thread):#
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while True:
			time.sleep(300)
			updater()

class updaterUpdaterThread(threading.Thread):#
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		while True:
			updaterUpdater()
			time.sleep(180)	

thread1= GetAll()
thread2= GetGamesNearNow()
thread3=updaterThread()
thread4=updaterUpdaterThread()
thread2.start()
thread3.start()
thread4.start()

tmp,tmp2,Urls=getUrlsByGame()
thread1.start()