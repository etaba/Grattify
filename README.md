#<center> Grattify </center>
##Requirements:

* HomeBrew (OS X Package Manager):
	* ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

* FFMPEG (audio converter, to convert between different audio formats):
	* brew install ffmpeg

* Pip (comes with homebrewed python, use 'homebrew install pip' if using default python)
	* NOTE:  if sudo needed to pip install packages its because default os x python being used. To avoid this, brew install python alongside it, and add /usr/local/bin to the beginning of paths file (/etc/paths)

* And Grattify!:
	* pip install grattify


##Basic Commands:

* grattify 
	* Shows you list of possible commands

* grattify -spotify mySpotifyUsername 
	* Brings you to the spotify login page, then downloads your spotify playlists
	* If you only want to download certain playlists, specify them after your username: 'grattify -spotify myUsername "my playlist 1" "my playlist 2" ... '

* grattify -song "the beatles" "come together"
	* Download a single song by providing the artist and song name

* grattify -album "the beatles" "abbey road" 
	* Download a whole album by providing the artist and album name

* grattify -top 18 "the beatles"'
	* Download the top N songs by an artist by providing the number N and the artist

* grattify -file "songList.txt"'
	* Download songs listed on a text file. The file can contain 3 types of lines:
		* artist - song (must be hyphen separated, shouldnt need quotes around * artist or song)
		* album: album - artist
		* top 16: artist