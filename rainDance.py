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
						continue
	return results

def findNthBest(n,searchInput,ytResults):
	#TODO: account for deviation from average video duration
	badKeywords = ["video","live","cover","remix","instrumental","acoustic","karaoke"]
	goodKeywords = ["audio","lyrics"]
	for bk in badKeywords:
		if searchInput.find(bk) > 0:
			badKeywords.remove(bk)
	scoreIndex = []
	for i in range(len(ytResults)):
		matchScore = i
		for bk in badKeywords:
			if ytResults[i]['title'].find(bk) > 0:
				matchScore += 1.1
		for gk in goodKeywords:
			if ytResults[i]['title'].find(gk) > 0:
				matchScore -= 1.1
		scoreIndex.append((i,matchScore))
	bestToWorst = sorted(scoreIndex,key=lambda score: score[1])
	nthIndex = bestToWorst[n-1][0]
	return ytResults[nthIndex]
 		

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
try:
	attempt = int(songs[0].strip())
except:
	attempt = 1
for song in songs:
	searchString = song.replace(' ','+') + "+audio"

	results = getYoutubeSearchResults(searchString)
	for r in results:
		print r['link']
	songURL = findNthBest(attempt,searchString,results)['link']
	print songURL
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



	