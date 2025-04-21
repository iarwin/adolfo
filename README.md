# adolfo
## setup:

>first, [*download* the zip file of this repository](https://github.com/iarwin/adolfo/archive/refs/heads/main.zip)

>this project is meant to be executed in windows, but it will also work on linux or mac as long as you have correctly installed the following dependencies:

>[FFmpeg](https://ffmpeg.org/download.html) (usually already installed in windows). if you want to use the FFmpeg that you downloaded simply paste the path to the executable file in the config.txt file.
>
>you will also need [*python*](https://www.python.org/downloads/), which you can install from the microsoft store. on linux or mac it should be already installed by default (version 3.6+ is required)
>
>there are also 2 dependencies you need to install from terminal ([discord.py](https://pypi.org/project/discord.py/) and [python-dotenv](https://pypi.org/project/python-dotenv/)), which you can install by running the following command:
>
>```pip install discord.py python-dotenv```
>
>but on linux this could cause some errors, depending on how the environment is set up, so you may need to [virtualize python](https://docs.python.org/3/library/venv.html)

>now you will need to [add a bot to your discord server](https://realpython.com/how-to-make-a-discord-bot-python/) and paste its token in the config.txt file

>finally, you will need to download the songs you want to play and distribute them in different directories (playlists) as in the [given example](https://github.com/iarwin/adolfo/tree/main/media/playlists/songs)


## usage:
> !add       -->   is used to add songs to the queue (works the same as spotify's)  --> !add "song"

> !commands  -->   the help I made  --> !commands

> !help      -->   the default help by discord  -->  !help

> !join      -->   joins the bot to your same voice channel  -->  !join

> !loop      -->   without arguments tells you the state of the variable, you can also give a boolean argument (true/false)  -->  !loop  //  !loop [true/false]

> !next      -->   skips as many songs as you want (no argument = 1 song)  -->  !next [number]

> !play      -->   play the playlist you want (no argument = random playlist) --> !play [playlist]

> !playlists  -->  see all available playlists --> !playlist

> !previous   -->  go back as many songs as you want (no argument = 1 song)  -->  !previous [number]

> !quit      -->  leave voice channel  --> !quit

> !queue    -->   see actual queue  --> !queue

> !restart  -->   start a song from the beginning --> !restart

> !resume  -->    resume a stopped song  -->  !resume

> !shuffle  -->   shuffles the queue (including added songs) --> !shuffle

> !skip    -->    with only a numerical value it acts as !next, but when the argument is in time format it skips to the minute specified (no argument = skips 1 song) --> !skip [number]  //  !skip [hh:mm:ss] (if hh = 0 there is no need to put it)

> !songs   -->    tells you all the available songs, and the playlist they belong  -->  !songs

> !stop    -->    stops the song that is playing  -->  !stop

> !volume  -->    set the volume (no argument = tells you the volume level)  --> !volume  //  !volume [number] (number between 0 and 100)

> !whatisthis  -->  tells you the song that is playing right now  -->  !whatisthis
