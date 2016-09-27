from __future__ import unicode_literals
from bs4 import BeautifulSoup
import sys, requests, youtube_dl, os, traceback


inFile = file("songList.txt");
local_filename = "songOutput.mp3"

saveDir = "songFolder"
if not os.path.exists(saveDir):
	os.makedirs(saveDir)

def makeSavepath(title,artist,saveDir=saveDir):
	return os.path.join(saveDir,"%s--%s.mp3" % (title, artist))

def getYoutubeSearchResults(query):
	results = []
	r = requests.post("https://www.youtube.com/results?search_query="+query)
	soup = BeautifulSoup(r.content,'html.parser')
	for div in soup.findAll("div"):
		if 'class' in div.attrs and "yt-lockup-content" in div['class']:
			for a in div.findAll('a'):
				if "watch" in a['href']:
					try:
						link = a['href']
						title = a['title']
						duration  = a.parent.find('span').text.split(' ')[-1][:-1]
						for li in div:
							#if 'class' in li.parent.attrs and "yt-lockup-meta-info" in li.parent['class']:
							if "views" in li.text:
								viewCount = li.text.split(' ')[-2][3:]
								results.append({"viewCount":viewCount,
												"link":"https://www.youtube.com"+link,
												"title":title,
												"duration":duration})
					except:
						print "skipping 'a' tag"
						continue
	return results

options = {
		'format':'bestaudio/best',
		'extractaudio':True,
		'audioformat':'mp3',
		'outtmpl':'%(id)s.%(ext)s',		#name the file the ID of the video
		'noplaylist':True,
		'nocheckcertificate':True,
		'postprocessors': [{
        	'key': 'FFmpegExtractAudio',
        	'preferredcodec': 'mp3',
        	'preferredquality': '192',
    	}]
	}

ydl = youtube_dl.YoutubeDL(options)
songs = inFile.readlines()
points = {}

for song in songs:
	songParts = song.split(",")
	title = songParts[0]
	artist = songParts[1]
	if (len(songParts) > 2): #additional details
		option = songParts[2]

	#TODO: replace spaces with +
	searchString = artist + "+" + title

	results = getYoutubeSearchResults(searchString)
	print results
	sys.exit()
	savePath = makeSavepath(title,artist)
	print savePath
	try: #video already being downloaded
		os.stat(savePath)
		print "%s already downloaded, continuing..." % savePath
		continue
	except OSError: #download video
		try:
			result = ydl.extract_info(songURL, download=True)
			print result['id']
			os.rename(result['id']+'.mp3', savePath)
			print "Downloaded and converted %s successfully!" % savePath
		except Exception as e:
			print "Can't download audio! %s\n" % traceback.format_exc()
	#in response: div .search_form -> 1st div #row -> div #span2 -> a href
	#r = requests.post('http://convert2mp3.net/en/index.php?p=convert', data = {"url":songURL,'format':'mp3','quality':"1",'3rfoos':"49554"})
	#r = requests.post('http://convert2mp3.net/en/index.php?p=complete&id='+songID, data = {"url":songURL,'format':'mp3','quality':"1",'3rfoos':"49554"})
	##attached to url: &key=CYxCxnlOg7k5
	#r = requests.post('http://convert2mp3.net/download.php?id='+songID+'&d=y')
	##print r.content
	#print r.content
	#with open(local_filename, 'wb') as f:
	#	for chunk in r.iter_content(chunk_size=1024): 
	#		if chunk: # filter out keep-alive new chunks
	#			f.write(chunk)
	#			#f.flush() commented by recommendation from J.F.Sebastian


	