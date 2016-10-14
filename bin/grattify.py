#!/usr/bin/env python
from grattify import *

SPOTIPY_CLIENT_ID = "6ddf2f4253a847c5bac62b17cd735e66"
SPOTIPY_CLIENT_SECRET = "5b54de875ad349f3bb1bbecd5832f276"
SPOTIPY_REDIRECT_URI = "tabatest://callback"

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

def downloadSong(title,artist,attempt,saveDir):
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




#MAIN EXECUTION

failedDownloads = []
if len(sys.argv) > 2: #using command line arguments
	if sys.argv[1] == "-album" or sys.argv[1] == "-a":
		album = sys.argv[2]
		artist = sys.argv[3]
		saveDir = album
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		tracks = getAlbum(artist,album)
		for i,track in enumerate(tracks):
			print "\nDOWNLOADING SONG %d / %d\n" % (i+1,len(tracks))
			if not downloadSong(track,artist,1,saveDir):
				failedDownloads.append((track,artist))

	if sys.argv[1] == "-song" or sys.argv[1] == "-s":
		saveDir = "songFolder"
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		artist = sys.argv[2]
		song = sys.argv[3]
		if not downloadSong(song,artist,1,saveDir):
			failedDownloads.append((song,artist))

	if sys.argv[1] == "-top" or sys.argv[1] == "-t":
		n = int(sys.argv[2])
		artist = sys.argv[3]
		saveDir = artist + "_Top_"+sys.argv[2]
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		tracks = getTopN(artist,n)
		for i,track in enumerate(tracks):
			print "\nDOWNLOADING SONG %d / %d\n" % (i+1,len(tracks))
			if not downloadSong(track,artist,1,saveDir):
				failedDownloads.append((track,artist))

	if sys.argv[1] == "-file" or sys.argv[1] == "-f":
		inFile = file(sys.argv[2])
		saveDir = sys.argv[2][:sys.argv[2].find('.')]
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		lines = inFile.readlines()
		try:
			attempt = int(lines[0].strip())
		except:
			attempt = 1
		for line in lines:
			print "\nDOWNLOADING LINE %d / %d\n" % (i+1,len(lines))
			songParts = line.split(",")
			if line[:6].lower()=="album:": #Album:the wall,pink floyd
				artist = songParts[-1]
				album = ",".join(songParts[:-1])
				album=album[6:]
				tracks = getAlbum(artist,album)
				for track in tracks:
					if not downloadSong(track,artist,attempt,saveDir):
						failedDownloads.append((track,artist))
			if line[:3].lower()=="top": #top 5:pink floyd
				colonIndex=line.find(':')
				artist = line[colonIndex+1:]
				n = int(line[3:colonIndex].strip())
				if n:
					tracks = getTopN(artist,n)
				else:
					print "SYNTAX ERROR: "+line
					print "SKIPPING"
				for track in tracks:
					if not downloadSong(track,artist,attempt,saveDir):
						failedDownloads.append((track,artist))
			else: #hey you,pink floyd
				artist = songParts[0]
				track = ",".join(songParts[1:])
				if not downloadSong(track,artist,attempt,saveDir):
					failedDownloads.append((track,artist))

	if sys.argv[1] == "-spotify" or sys.argv[1] == "-sp":
		saveDir = "SpotifySongs"
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		username = sys.argv[2]
		tracks = getSpotifyPlaylists(username)
		for i,track in enumerate(tracks):
			print "\nDOWNLOADING SONG %d / %d\n" % (i+1,len(tracks))
			if not downloadSong(track[1],track[0],1):
				failedDownloads.append((track[1],track[0]))

	if sys.argv[1] == "-pandora" or sys.argv[1] == "-p":
		saveDir = "Pandora_Liked_Songs"
		if not os.path.exists(saveDir):
			os.makedirs(saveDir)
		pandoraFile = sys.argv[2]
		tracks = parsePandoraLikes(pandoraFile)
		for i,track in enumerate(tracks):
			print "\nDOWNLOADING SONG %d / %d\n" % (i+1,len(tracks))
			if not downloadSong(track[0],track[1],1,saveDir):
				failedDownloads.append((track[0],track[1]))

	if sys.argv[1] == "-debug":
		ms = compare(sys.argv[2],sys.argv[3])
		print "%d Changes" % len(ms)
		for m in ms:
			print m

	print "Failed: ",failedDownloads if len(failedDownloads) > 0 else "All songs downloaded!"
else:
	print "USAGE:"
	print '-spotify "user@email.com"'
	print '-song "The Beatles" "Come Together"'
	print '-album "Abbey Road" "The Beatles"'
	print '-top 5 "The Beatles"'
	print '-file "songList.txt"'




	
#TODO:
#format saved files to recognize name and artist
#package libraries
#multithreading?
#replace all non alphanumeric characters? or at least apostrophes
#chrome extension to download song currently being listened to

	




	