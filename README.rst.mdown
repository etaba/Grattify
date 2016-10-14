Requirements:

HomeBrew: ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
	ffmpeg

Pip: comes with homebrewed python, use 'homebrew install pip' if using default python
	youtube-dl
	BeautifulSoup4
	spotipy
	NOTE:  if sudo needed to pip install packages its because default os x python being used. To avoid this, brew install python alongside it, and add /usr/local/bin to the beginning of paths file (/etc/paths)