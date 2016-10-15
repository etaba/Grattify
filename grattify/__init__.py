from __future__ import unicode_literals
from bs4 import BeautifulSoup
import sys, requests, youtube_dl, os, traceback, spotipy, urllib,pprint
import spotipy.util as util

def downloadSong(title,artist,attempt,saveDir):
	options = {
		'format':'bestaudio/best',
		'extractaudio':True,
		'audioformat':'mp3',
		'outtmpl':'%(id)s.%(ext)s',		#name the file the ID of the video
		'noplaylist':True,
		'nocheckcertificate':True,
		'proxy':"",
		'addmetadata':True,
		'postprocessors': [{
        	'key': 'FFmpegExtractAudio',
        	'preferredcodec': 'mp3',
        	'preferredquality': '192',
    	}]
	}

	ydl = youtube_dl.YoutubeDL(options)
	searchString = (artist.lower()+'+'+title.lower()).replace(' ','+')
	results = getYoutubeSearchResults(searchString)
	if results == False:
		return False
	songURL = findNthBestLink(attempt,searchString,results,artist.lower(),title.lower())['link']
	savePath = makeSavepath(title,artist,saveDir)
	#print artist,"---",title
	#return
	try: #video already being downloaded
		os.stat(savePath)
		print "%s already downloaded, continuing..." % savePath
	except OSError: #download video
		try:
			result = ydl.extract_info(songURL, download=True)
			print savePath
			os.rename(result['id'] +'.mp3', savePath)
			print "Downloaded and converted %s successfully!" % savePath
		except Exception as e:
			print "Can't download audio! %s\n" % traceback.format_exc()
			return False
	return True

def makeSavepath(title,artist,saveDir):
	title = title.replace('/',' ')
	artist = artist.replace('/',' ')
	return os.path.join(saveDir,"%s -- %s.mp3" % (artist, title))

def getYoutubeSearchResults(query):
	results= []
	try:
		r = requests.post("https://www.youtube.com/results?search_query="+query)
	except Exception as e:
		print "Can't download audio! %s -- %s\n" % (artist,title)
		return False
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
								results.append({"viewCount":int(viewCount.replace(',','')),
												"link":"https://www.youtube.com"+link,
												"title":title.lower(),
												"duration":duration})
					except:
						continue
	return results

def findNthBestLink(n,searchInput,ytResults,artist,title):
	#ytResults = sorted(ytResults,key = lambda r: r['viewCount'],reverse=True)
	#TODO: account for deviation from average video duration
	badKeywords = ["video","album","live","cover","remix","instrumental","acoustic","karaoke"]
	goodKeywords = ["audio","lyric"]# + searchInput.split('+')
	
	badKeywords = filter(lambda bk: searchInput.find(bk) < 0,badKeywords)
	#for bk in badKeywords:
	#	if searchInput.find(bk) > 0:
	#		badKeywords.remove(bk)
	scoreIndex = []
	for i,ytR in enumerate(ytResults):
		matchScore = i
		for bk in badKeywords:
			if ytR['title'].find(bk) != -1:
				matchScore += 1.1
		for gk in goodKeywords:
			if ytR['title'].find(gk) != -1:
				matchScore -= 1.1
		if ytR['title'].find("".join(artist.split("the "))) != -1:
			matchScore -= 5
		if ytR['title'].find(title) != -1:
			matchScore -= 3
		#for sI in searchInput.split('+'):
		#	if len(sI) > 3 and ytR['title'].find(sI) > 0:
		#		matchScore -= 5
		scoreIndex.append((i,matchScore))
	bestToWorst = sorted(scoreIndex,key=lambda score: score[1])
	nthBest = bestToWorst[n-1][0]
	#printResults(ytResults,bestToWorst)
	print "1st: ",ytResults[bestToWorst[n-1][0]]['link']
	#print "2nd: ",ytResults[bestToWorst[n][0]]['link']
	#print "3rd: ",ytResults[bestToWorst[n+1][0]]['link']
	return ytResults[nthBest]
 		
def printResults(ytResults,bestToWorst):
	print "UNSORTED::"
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(ytResults[:7])
	print "\n\n\n"
	print "BY ALGORITHM::"
	smartList = map(lambda score: (ytResults[score[0]],score[1]),bestToWorst)
	pp.pprint(smartList[:7])

def parsePandoraLikes(pandoraLikesPage):
	pFile = urllib.urlopen(pandoraLikesPage).read()
	soup = BeautifulSoup(pFile,'html.parser')
	songs = []
	for div in soup.findAll('div',id=lambda x: x and x.startswith('tracklike')):
		info = div.findAll('a')
		songs.append((info[0].text,info[1].text))
	return songs

def getSpotifyTop5(artist):
	sp = spotipy.Spotify()
	results = sp.search(q="artist:"+artist,type='artist')
	url = results['artists']['items'][0]['external_urls']['spotify']
	r = requests.get(url)
	soup = BeautifulSoup(r.content,'html.parser')
	songs =[]
	for i in range(5):
		row = soup.find('tr',{'data-index':i})
		div = row.find('div',{'data-log-click':"name"})
		songs.append(div.text.strip())
	return songs

def getTopN(artist,n):
	try:
		r = requests.get("http://www.last.fm/music/"+artist.replace(' ','+')+"/+tracks")
		soup = BeautifulSoup(r.content,'html.parser')
		tds = soup.findAll("td",{"class":"chartlist-name"})
		songs = []
		for i in range(n):
			song = tds[i].find("a").text
			songs.append(song)
		return songs
	except Exception as e:
		print "SEARCH ERROR: Couldnt find top "+str(n)+" songs by "+artist

def getAlbum(artist,album):
	try:
		r = requests.get("http://www.last.fm/music/"+artist.replace(' ','+')+"/"+album.replace(' ','+'))
		soup = BeautifulSoup(r.content,'html.parser')
		tds = soup.findAll("td",{"class":"chartlist-name"})
		return map((lambda td: td.find("a").text),tds)
		#songs = []
		#for td in tds:
		#	song = td.find("a").text
		#	songs.append(song)
	except Exception as e:
		print "SEARCH ERROR: Couldnt find album "+album+" by "+artist

def getSpotifyPlaylists(username):
	scope = "playlist-read-private user-library-read"
	token = spotipy.util.prompt_for_user_token(username, scope,SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI)
	tracks = []
	if token:
	    sp = spotipy.Spotify(auth=token)
	    user = sp.current_user()['id']
	    playlists = sp.user_playlists(user)
	    for playlist in playlists['items']:
			print playlist['name']
			print '  total tracks', playlist['tracks']['total']
			results = sp.user_playlist(user, playlist['id'],
			    fields="tracks,next")
			tracks = results['tracks']
			#sp.show_tracks(tracks)
			for item in tracks['items']:
				tracks.append((item['track']['artists'][0]['name'],item['track']['name']))
			#while tracks['next']:
			#    tracks = sp.next(tracks)
			#    show_tracks(tracks)
			#print track['name'] + ' - ' + track['artists'][0]['name']
	else:
	    print "Can't get token for", username
	return tracks

def compare(file1,file2):
	lines1 = file(file1).readlines()
	lines2 = file(file2).readlines()
	c1 = []
	for i,l in enumerate(lines1):
		if l[:4]=="1st:":
			c1.append(lines1[i-1] + ":::" + l[4:])
	c2 = []
	for i,l in enumerate(lines2):
		if l[:4]=="1st:":
			c2.append(lines2[i+3] + ":::" + l[4:])

	misMatches = filter((lambda (l1,l2): l1 != l2),zip(c1,c2))
	changeLog = file("changeLog.txt","w+")
	for mPair in misMatches:
		m = mPair[0]
		artist = m[m.find("---")+4:m.find("\n:::")]
		song = m[:m.find("---")]
		#print artist,song
		changeLog.write(artist + "," + song + '\n')
	return misMatches