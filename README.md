# adolfo
## setup:

>first, [*download* the zip file of this repository](https://github.com/iarwin/adolfo/archive/refs/heads/main.zip)

>this project is meant to be executed in windows, but it will also work on linux or mac as long as you have correctly installed the following dependencies:

>[FFmpeg](https://ffmpeg.org/download.html) (usually already installed in windows). if you want to use the FFmpeg that you downloaded simply paste the path to the executable file in the config.txt file.
>
>you will also need [*python*](https://www.python.org/downloads/), which you can install from the microsoft store. on linux or mac it should be already installed by default (version 3.6+ is required)
>
>there are also 2 dependences you need to install from terminal ([discord.py](https://pypi.org/project/discord.py/) and [python-dotenv](https://pypi.org/project/python-dotenv/)), which you can install by running the following command:
>
>```pip install discord.py python-dotenv```
>
>but on linux this could cause some errors, depending on how the environment is set up, so you may need to [virtualize python](https://docs.python.org/3/library/venv.html)

>now you will need to [add a bot to your discrod server](https://realpython.com/how-to-make-a-discord-bot-python/) and paste its token in the config.txt file

>finally, you will need to download the songs you want to play and distribute them in different directories (playlists) as in the [given example](https://github.com/iarwin/adolfo/tree/main/media/playlists/songs)


## usage:
> !add       -->   is used to add songs to the queue (works the same as spotify's)  --> !add "song"

> !commands  -->   the help I made  --> !commands

> !help      -->   the default help by discord  -->  !help

> !join      -->   joins the bot to your same voice channel  -->  !join

> !loop      -->   without arguments tells you the state of the variable, you can also give a boolean argument (true/false)  -->  !loop  //  !loop [true/false] 
