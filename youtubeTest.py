import requests,sys
from bs4 import BeautifulSoup

#.ol["class"] == "item-section"

def scrape():
	r = requests.post("https://www.youtube.com/results?search_query=mac+miller+nikes+on+my+feet")
	soup = BeautifulSoup(r.content,'html.parser')
	for div in soup.findAll("div"):
		if 'class' in div.attrs and "yt-lockup-content" in div['class']:
			for a in div.findAll('a'):
				if "/watch" in a['href']:
					link = a['href']
					try:
						title = a['title']
						duration  = a.parent.find('span').text.split(' ')[-1][:-1]
						for li in div:
							#if 'class' in li.parent.attrs and "yt-lockup-meta-info" in li.parent['class']:
							if "views" in li.text:
								viewCount = li.text.split(' ')[-2][3:]
								print viewCount
								print link
								print title
								print "duration: " + duration
								print "\n"
					except:
						continue
	return

def findNthBest(n,searchInput,ytResults):
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
	print scoreIndex
	bestToWorst = sorted(scoreIndex,key=lambda score: score[1])
	print bestToWorst
	nthIndex = bestToWorst[n-1][0]
	return ytResults[nthIndex]

testResults  = [{'title':"test video"},
		 {'title':"test video"},
		 {'title':"test video"},
		 {'title':"test lyrics"},
		 {'title':"test lyrics"}]
print findNthBest(1,"test ",testResults)

