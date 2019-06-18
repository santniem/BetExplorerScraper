from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException,TimeoutException
import time
import threading
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from selenium.webdriver.support import expected_conditions as EC
import numpy as np

client = MongoClient('mongodb+srv://persnekru:Santtu420@cluster0-zypbs.mongodb.net/test')
myclient = MongoClient("mongodb://localhost:27017/")
db = client.get_database('test')
betsCollection = db.Bets

def getUrlsByGame():
	urls=[]
	times=[]
	driver = webdriver.Chrome(options=options)
	tmpList2=[]
	gamess = ["soccer","tennis","basketball","baseball","volleyball"]#,"basketball""baseball","volleyball","basketball",
	for game in gamess:
		wait = WebDriverWait(driver,10)
		driver.get("https://www.betexplorer.com/next/" +game+"/?year=2019&month=06&day=18")
		element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#nr-all')))
		
		testi  = driver.page_source
		soup = BeautifulSoup(testi,features="lxml")
		tr = soup.find_all("tr")
		for each in tr:
			result = each.find(class_='table-main__result')
			if (result!=None):
				each.decompose()
		linkki='https://www.betexplorer.com/'
		
		for each in tr:
			
			a = each.find("a")
			b = each.find(class_="table-main__time")
			if(a is None):
				pass
			else:
				linkki='https://www.betexplorer.com/'
				link = a["href"]
				link = link.split('/')
				
				if(len(link)>5):
					link.pop(0)
					link.pop
					for each in link:
						linkki+=each+'/'
					linkki= linkki[:-1]
					urls.append(linkki)
					tmpList=[]
					
					b=b.get_text()
					times.append(b)

					tmpList.append(b)
					tmpList.append(linkki)
					tmpList2.append(tmpList)

					
	driver.close()
	return urls,gamess,tmpList2

def right(s, amount):#miksei pyyttonissa vain ole omaa LEFT RIGHT JA MID
	return s[-amount:]
def baseball(element):#pesis on hieman vammane nii pitää hakee omalla tavalla
	check = element.text.split('\n')
	if (len(check)>1):
		url = (element.find_element_by_css_selector('a').get_attribute('href'))
		return url
	else: pass

def Decomposer(soup):
	try:
		try:
			shooters=soup.find_all(class_="list-details--shooters")
			for each in shooters:
					each.decompose()
		except:pass
		try:
			soup.find("div", {"id": "glib-stats"}).decompose()
		except:pass
		for each in soup.find_all(class_="box glib-stats-box-overall selected"):#poistaa turhat härpäkkeet jotka tulee <tr> tagin mukana
				each.decompose()
		for each in soup.find_all(class_="h-text-right"):#poistaa jonku vitun turhan asian
				each.decompose()
		for each in soup.find_all(class_="tablet-desktop-only"):#poistaa jonku vitun turhan asian
				each.decompose()	
		soup.find("div", {"id": "mutual_div"}).decompose()
		soup.find("div", {"id": "match-results-home"}).decompose()
		soup.find("div", {"id": "match-results-away"}).decompose()

	except Exception as e:
		return soup
	else: return soup

def SopanKauhoja(soppa):
	trList=[]
	for div in soppa:#poistaa ne rivit joissa kerroin on yliviitattu eli tähän matsiin ei sillä sivulla voi vetoo lyödä
		x = div.find_all("tr")
		for z in x:
			ass =z.find(class_="inactive")
			xxbet = z.find(class_="h-text-left over-s-only")
			if(ass!=None):
				z.decompose()
			if(xxbet!=None):
				if('1xBet' in xxbet.get_text()):
					z.decompose()


	for each in soppa:
		trList.append(each.find_all("tr"))#kaikki tr tagilliset listaan. Nää on ne mikkä sisältää datan mallissa: Bookie,bettype ,kotikerroin,vieraskerroin
	return trList

def OddsGetter(driver):#bröther mäy i have söme lÖÖps
	try:
		matchDictionary={}
		SiteElements=[]			
		siteElements=[]#iha vitun hyviä listan nimiä
		tempList=[]
		bookie={}
		mylist = []
		#wait
		wait=WebDriverWait(driver,3)
		element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#odds-content')))
		time.sleep(0.5)
		#wait
		if(True):#tsekkaa iha vittuillaksee et onko peli jo pelattu vai ei vaikka urleis ei pitäs semmosia ollakkaa
			urli=right(driver.current_url,3)#tsekkaa urlin 3 viimestä merkkiä jotka on muodossa #xx ja nää on niit pelityyppei
			if(urli=="#dc" ): #double chance 3 kerrointa ni menee vituiks
				return matchDictionary
			if(urli=="#ha" ): #täski on 3 kerrointa ni ei toimi eli palauttaa vaa tyhjän dictionaryn
				return matchDictionary
			if(urli=="1x2"):
				return matchDictionary
			
			#soppaa
			soppa = BeautifulSoup( driver.page_source,features="lxml") #sorsasoppaa
			soppa = Decomposer(soppa)#napataan turhat elementit vittuun sekaamasta soppaa
			kokoSoppa = soppa.find_all("tbody")
			trList = SopanKauhoja(kokoSoppa)
			#soppaa
			lastempty=''		
			for k in trList:#korvaa puuttuvat kertoimet ykkösellä ja pois \xa0 merkit
				for i in k:
					splits = i.text.split('\n')
					for empty in splits:
							if(empty!=''):
									if(empty=='\xa0' and lastempty != 'null'): empty='1'
									siteElements.append(empty)
									lastempty = empty
							else:pass
			

			for i in range(len(siteElements)):
					if(len(siteElements[i])<17):#tarkistus
						tempList.append(siteElements[i])
			chunkSize=4
			if(urli=='bts'): chunkSize = 3
			SiteElements = list(divideList(tempList, chunkSize))

			for element in SiteElements:
					mylist.append(element[1])
			mylist = list(dict.fromkeys(mylist))#haetaan uniikit avaimet(betTypes) dictionarylle 
			if(urli!='bts'):
				for z in mylist:
					bookie={}
					for i in SiteElements:
						if(z==i[1]):
							try:
								float(i[2])
								float(i[3])
							except Exception as e:
								print(e,'löl',driver.current_url)
							else:
								bookie[i[0]]=(i[1],float(i[2]),float(i[3]))
								matchDictionary[z] = bookie					#Dictionaryllinen dictionaryja 
						else:pass

			else:
				for z in mylist:
					bookie={}
					for i in SiteElements: #i pitäs olla oddsit mutta joskus kusooo
						try:
							float(i[1])
							float(i[2])
						except Exception as e:
							print(e,'läl',driver.current_url)
						else:
							bookie[i[0]]=('bts',float(i[1]),float(i[2]))
							matchDictionary['bts'] = bookie					#Dictionaryllinen dictionaryja 
			return matchDictionary
		else:return matchDictionary
	except Exception as e: 
		print(e,driver.current_url,SiteElements)
		print("exception at getter")
		#matchDictionary={}
		return matchDictionary



def urlit(urls,driver):#ottaa listan ekan urlin ja poppaa sen helvettiin käyttämisen jälkeen
	try:
		url = urls[0]#listan eka url
		driver.get(url)#mene sinne url
		bt=betTypes(url,driver)#hae sen urlin bettypet
		urls.pop(0)#poista se url
		return url, bt#palauta se url että sen voi lokittaa
	except:
		return 'stop',0#hukkaragee.mp4

def betTypes(url,driver): #haetaan eri bettityypit over/under,handicap,1x2 jnejne
	try:
		betTypeList=[]
		for i in range(1,10):
			if("basketball" in url):#koripallosivuilla on jotenki astetta vammasempi layout
					bt = driver.find_elements_by_class_name("list-tabs__item")
					bt.pop()
					for each in bt:
						
						btype = each.text
						if(len(btype)<15 and btype!=''):
							betTypeList.append(btype)
					if(i==1):return betTypeList
			else:
				bt = driver.find_element_by_css_selector('#odds-all > div.box-overflow > div > ul > li:nth-child('+str(i)+')').text
			betTypeList.append(bt)
	except: return betTypeList

def click(i,url,driver): #klikkaaa ittensä eri bettityyppien sivulle koska koko sivun lataaminen url/#ou tyylillä vitun raskasta
	try:
		wait=WebDriverWait(driver,5)
		element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#odds-all > div.box-overflow > div > ul > li:nth-child(1) > a')))
		time.sleep(0.3)
		if("basketball" in url):#koris o vammane
			asd = driver.find_elements_by_class_name('list-tabs__item')
			asd.pop()
			asd[i].click()
		else:
				try:
					driver.find_element_by_css_selector('#odds-all > div.box-overflow > div > ul > li:nth-child('+str(i)+')').click()
				except: pass
	except TimeoutException:
		pass

def matchUpdater(listOfDicts,driver):
	i=1
	for each in listOfDicts:
			# bookies1=list(each["Bookie 1"]["Bookies"].keys())
			# bookies2=list(each["Bookie 2"]["Bookies"].keys()) lets see jos näit vaikka tarvii joskus johonki
			driver.get(each["URL"])
			
			homeList=[]
			awayList=[]
			bookieList=[]
			matchDictionary=OddsGetter(driver)
			#vammane loop koska avaimia ei muuten saa
			print("Updating: ",i," out of :",listOfDicts.count())
			i+=1
			for keyElement in matchDictionary:
					if(each["BetType"] == keyElement):
							KeyElementDict=matchDictionary[keyElement]
							for eachElement in KeyElementDict:
									bookieList.append(eachElement)
									homeList.append(KeyElementDict[eachElement][1])
									awayList.append(KeyElementDict[eachElement][2])
							bestBet=getArbitage(homeList,awayList,bookieList)
							newMargin=bestBet[0]
							if (newMargin>=100):
									betsCollection.update_one({"URL":each["URL"],"BetType":keyElement},{"$set":{"Active":0}})
							else:
									HomeBookies,AwayBookies=FindMatchingBookies(bookieList,homeList,awayList)
									jsonifier(bestBet,driver,keyElement,HomeBookies,AwayBookies)
																		




def getMax(lista): #hakee listasta kerroinlistasta maksimin ja palauttaa myös sen indeksin että saa bookien mukaan
	maximum=max(lista)
	maxIndex=lista.index(max(lista))
	return maximum,maxIndex
def updater(driver):
	active=1
	test = driver.find_element_by_id("js-score").text
	if(test != '-:-'):
		active=0
	
def jsonifier(bestBet,driver,key,HomeBookies,AwayBookies):
	try:
		
		day = driver.find_element_by_id('match-date').text
		daytime = day.split(" - ")
		day=daytime[0]
		Time=daytime[1]
		currentURL=driver.current_url
		urli=right(currentURL,3)
		try:
			try:
				type1=driver.find_element_by_css_selector("#sortable-1 > thead > tr > th:nth-child(6) > a").text
				type2=driver.find_element_by_css_selector('#sortable-1 > thead > tr > th:nth-child(7) > a').text
			except NoSuchElementException:
				type1=driver.find_element_by_css_selector("#sortable-1 > thead > tr > th:nth-child(5) > a").text
				type2=driver.find_element_by_css_selector('#sortable-1 > thead > tr > th:nth-child(6) > a').text
		except NoSuchElementException:
				type1=driver.find_element_by_css_selector("#sortable-1 > thead > tr > th:nth-child(4) > a").text
				type2=driver.find_element_by_css_selector('#sortable-1 > thead > tr > th:nth-child(5) > a').text
		active = 1
		if(bestBet[0]>100):
			active=0
		test = driver.find_element_by_id("js-score").text
		if(test != '-:-'):
			active=0

		betJson ={
				"URL": currentURL,
				"Margin":round(100-bestBet[0],3),
				"BetType": key,
				"Day":day,
				"Time":Time,
				"Active":active,
				"Bookie 1" :
					{	"Type":type1,
						"Bookies":HomeBookies,
						"HomeOdds":bestBet[3]
					},
				"Bookie 2" :
				{	"type2": type2,
					"Bookies":AwayBookies,
					"Awayodds": bestBet[4]
				},

				"Betti 1":
				{
					"Bet A":bestBet[5],
					"Bet B":bestBet[6],
					"Yht":bestBet[7],
					"Profit if Home Wins":bestBet[8],
					"Profit if Away Wins":bestBet[13],
					"newMargin": bestBet[15]
				},
				"Betti2":
				{
					"Bet2 A":bestBet[9],
					"bet2 B": bestBet[10],
					"Yht":bestBet[11],
					"Profit if Home Wins":bestBet[14],
					"Profit if Away Wins":bestBet[12],
					"newMargin": bestBet[16]
				},
		
		}
		return betJson,bestBet[0]
	except Exception as e:
		print("exception at jsonifier")
		print(driver.current_url,e)

def jsonWriter(bestBet,kkey,driver,jsonName,HomeBookies,AwayBookies):	
	try:
		SortedjsonList=[]
		global lck
		lck.acquire()
		betJson,margin = jsonifier(bestBet,driver,kkey,HomeBookies,AwayBookies)
		if(betJson not in jsonList):#Katotaan ettei tuu duplicateja
			jsonList.append(betJson)
			# if(bestBet[0]>100):
			# 	betsCollection.update_one({"URL":betJson["URL"],"BetType":kkey},{"$set":{"Active":0}})
			# 	print("did something")
			# else:		
			betsCollection.update_one({"URL":betJson["URL"],"BetType":kkey},{"$set":betJson,"$currentDate": {"lastModified": True}},upsert=True)
			print("Updated or inserted something")
		else:pass
		lck.release()
	except Exception as e:
		print(e)

def FindMatchingBookies(bookie,home,away):
	homeBookies={}
	awayBookies={}
	homemax=max(home)
	awaymax=max(away)
	home = np.array(home)
	away= np.array(away)
	homeII = np.where(home == homemax)[0]
	awayII = np.where(away == awaymax)[0]
	for i in homeII:
		try:
			homeBookies[bookie[i]]=jsonURLS[bookie[i]]
		except KeyError:homeBookies[bookie[i]]="no url"
	for i in awayII:
			try:
				awayBookies[bookie[i]]=jsonURLS[bookie[i]]
			except KeyError:
				awayBookies[bookie[i]]="no url"	
	return homeBookies,awayBookies


with open("C:\\Users\\santeri\\Documents\\koodia\\ArbitageBetting\\urls.json","r") as filu:
	jsonURLS = json.load(filu)   			
def countMargins(home,away):#laskee arbitaasimarginaalin
	return round(((1/home)+(1/away))*100,4)		

def getArbitage(homeList,awayList,bookies):#haetaan maksimit ja palautetaan listana paras marginaali tyyliin

	defaultBet=100
	bestBet=[]
	homeMax, homemaxIndex = getMax(homeList)
	awayMax, awayMaxIndex = getMax(awayList)
	margin = countMargins(homeMax, awayMax)
	bestBet.append(margin)
	bestBet.append(bookies[homemaxIndex])
	bestBet.append(bookies[awayMaxIndex])
	bestBet.append(homeList[homemaxIndex])
	bestBet.append(awayList[awayMaxIndex])
	BetA= defaultBet
	#jos kodilla pienemmät oddsit
	BetB= 5*round((BetA*(homeMax/awayMax))/5)
	BetSum = round(BetA+BetB,2)
	bestBet.append(BetA)
	bestBet.append(BetB)
	bestBet.append((BetSum))
	wins=BetA*homeMax
	profit = round(wins-BetSum,2)
	bestBet.append(profit)
	newMargin=round((BetB/awayMax)/(BetA*homeMax),4)
	profitIFaway=round((BetB*awayMax -BetSum),2)

	#jos vieraalla pienenmmät
	BetB = defaultBet
	BetA= 5*round((BetB*(awayMax/homeMax))/5)
	bestBet.append(BetA)
	bestBet.append(BetB)
	BetSum = round(BetA+BetB,2)
	bestBet.append(BetSum)
	profit=round((BetB*awayMax)-(BetA+BetB),2)
	bestBet.append(round(profit))
	newMargin2 = round((BetA*homeMax)/(BetB*awayMax),4)

	profitIFhome =round((BetA*homeMax)-BetSum,2)
	bestBet.append(profitIFaway)
	bestBet.append(profitIFhome)
	bestBet.append(newMargin)
	bestBet.append(newMargin2)


	return bestBet

marginLimit=100
jsonList=[]
def creativeMethodName(driver,urlss,threadName):#Tää tekee oikeesti kaiken iha vitu vammasesti pitäskö korjata lol
	#path="C:\\Users\\SanteriNiemi\\Documents\\koodia\\pelei\\"
	path = "C:\\Users\\santeri\\Documents\\koodia\\ArbitageBetting\\"
	jsonName =path+"json"+".json" 
	aikalista=[]	
	while(True):#looppaa niin kauan et urlit loppuu ja sit cräshää
		start = time.time()
		#menee sinne urliin
		url, bt = urlit(urlss,driver)
		currentURL=driver.current_url
		splits=currentURL.split('/')
		itera=1
		if(bt==0):#tää ei muuten toimi lol
			driver.close()
			break
		else:
			for i in range(1,len(bt)):
				if(i==1 and splits[3]=='soccer'):#sport=="soccer" and 
					itera+=1#jos jalkapallo niin ei 1x2 koska 1x2 on 3 eri kerrointa ja me halutaan vaan 2 eri kerroin
				click(itera, url,driver)
				itera+=1
				matchDictionary = OddsGetter(driver) #scrapee sivun
				for key, value in matchDictionary.items():#key = sport ja value on sit bookie,team1 ja team2
					homeList = []
					awayList = []
					bookies = []
					for bookie, odds in value.items():
						if(odds[0]==key):#survotaan kertoimet ja bookie listoihin bettityypin perusteella esim yli 0.5maalia , alle 4.5maalia jnejne
							bookies.append(bookie)
							homeList.append(odds[1])
							awayList.append(odds[2])
						else:pass
					if not homeList:
						pass
					else:
						bestBet=getArbitage(homeList,awayList,bookies)
					if(len(bestBet) == 0):
						pass
					else:
						if(90<bestBet[0] < marginLimit):#jos marginaali 98-100 ni iha vitun turhaa jollai 2% profiiteilla leikkiä. Alle 92% on varmaa virhe joten ei sitä
							HomeBookies,AwayBookies=FindMatchingBookies(bookies,homeList,awayList)
							jsonWriter(bestBet,key,driver,jsonName,HomeBookies,AwayBookies)
						else: pass
			end = time.time()
			aikalista.append(end-start)#sekuntteja
			avgTime=0
			for each in aikalista:
				avgTime+=each
			avgTime= avgTime/(len(aikalista))
			print("Estimated time till completion for thread",threadName," is: ", round((avgTime*len(urlss))/60,1), "Mins  - Average time:",round(avgTime,1)," seconds"+" - "+str(+len(urlss))+' urls left')

class myThread(threading.Thread):#tehään threadit lajin perusteella että ei kestä kolmee vuotta hakee kaikkia päivän pelejä
	def __init__(self,ThreadName,urls):
		threading.Thread.__init__(self)
		self.ThreadName = ThreadName
		self.urls = urls
	def run(self):
		
		driver = webdriver.Chrome(options=options) #jokaselle oma chrome tottakai executable_path='C:\\Users\\SanteriNiemi\\Documents\\koodia\\chromedriver.exe'

		creativeMethodName(driver,self.urls,self.ThreadName)

		print("Byebye",self.ThreadName)
		

def divideList(l, n): 
	# Atm KAIKKI on vaa yhes listas ja tää jakaa ne 4 palasen listoiksi [bookie,type,oddhome,oddaway]
	for i in range(0, len(l), n):  
		yield l[i:i + n] #jotai magiaa vissii

#Globals		
lck = threading.Lock()
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--log-level=3")
#Globals
def main(urlsANDtimes):
	urls=[]
	for each in urlsANDtimes:
			urls.append(each[1])
	NUMOFTHREADS=10
	x = divideList(urls, int(len(urls)/NUMOFTHREADS)) #Jaetaan urlit n osaan ja startataan threadeja listojen määrän perusteella
	threadlist=[]
	iter=0
	threads={}#dunno paska nimi
	for each in x:
		threads[iter]=each
		iter+=1

	for each in threads:
		each = myThread(each,threads[each])
		threadlist.append(each)
	for x in threadlist:
		time.sleep(0.2)
		x.start()


