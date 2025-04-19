import os
import random
import re
import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from dotenv import load_dotenv

# Cargar variables de entorno desde config.txt
load_dotenv('config.txt')
TOKEN = os.getenv('token')
FFMPEG_PATH = (os.getenv('ffmpeg_path', '').strip() or "ffmpeg")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variables globales
playlist = []
base_playlist = []
current_index = 0
playlist_path = ""
current_volume = 1.0
vc = None
current_audio_source = None
manual_skip = False
loop_enabled = False
added_songs = []
insert_index = None

def remove_extension(file_name):
    return os.path.splitext(file_name)[0]

def play_current_song():
    global current_audio_source, vc, current_index, playlist, current_volume, manual_skip
    if current_index < 0 or current_index >= len(playlist):
        print("Índice fuera de rango. No se puede reproducir la canción.")
        return

    song_path = playlist[current_index]
    current_audio_source = FFmpegPCMAudio(song_path, executable=FFMPEG_PATH)
    current_audio_source = discord.PCMVolumeTransformer(current_audio_source)
    current_audio_source.volume = current_volume
    vc.play(current_audio_source, after=lambda error: bot.loop.create_task(auto_next()))
    print(f"Reproduciendo: {song_path}")

async def auto_next():
    global current_index, playlist, base_playlist, vc, manual_skip, loop_enabled, added_songs, insert_index

    if manual_skip:
        manual_skip = False
        return

    if current_index < len(playlist) - 1:
        current_index += 1
    elif loop_enabled:
        playlist = base_playlist.copy()
        current_index = 0
        added_songs.clear()
        insert_index = None
    else:
        return

    await asyncio.sleep(0.5)
    play_current_song()

@bot.event
async def on_ready():
    print(f"bot not connected as {bot.user}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ connected to {channel.name}")
        else:
            await channel.connect()
            await ctx.send(f"✅ joined to: {channel.name}")
    else:
        await ctx.send("❌ must be in a voice channel.")

@bot.command()
async def quit(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 disconnecting...")
    else:
        await ctx.send("❌ ain't connected to a voice channel")

@bot.command()
async def play(ctx, playlist_name: str = None):
    global playlist, base_playlist, current_index, playlist_path, vc, insert_index, added_songs

    base_dir = os.path.join("media", "playlists")

    if playlist_name is None:
        available = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
        if not available:
            await ctx.send("❌ no playlists aviable")
            return
        playlist_name = random.choice(available)

    playlist_path = os.path.join(base_dir, playlist_name)
    if not os.path.exists(playlist_path):
        await ctx.send("❌ playlist not found.")
        return

    if not ctx.author.voice:
        await ctx.send("❌ must be in a voice channel")
        return

    voice_channel = ctx.author.voice.channel
    if not ctx.voice_client:
        vc = await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)
        vc = ctx.voice_client
    else:
        vc = ctx.voice_client

    media_formats = (".mp3", ".ogg", ".wav", ".flac", ".m4a", ".mp4", ".mkv")
    files = sorted([f for f in os.listdir(playlist_path) if f.lower().endswith(media_formats)])
    if not files:
        await ctx.send("❌ no valid files in this playlist")
        return

    playlist = [os.path.join(playlist_path, f) for f in files]
    base_playlist = playlist.copy()
    current_index = 0
    insert_index = None
    added_songs.clear()

    await ctx.send(f"🎶 playing: **{playlist_name}**")
    play_current_song()

@bot.command()
async def queue(ctx):
    global playlist, current_index

    if not playlist:
        await ctx.send("❌ no songs in queue")
        return

    queue_message = "📜 **queue:**\n"
    for pos, song in enumerate(playlist[current_index:], start=1):
        song_name = remove_extension(os.path.basename(song))
        if pos == 1:
            queue_message += f"     🎵  {song_name}\n"
        else:
            queue_message += f"     **{pos}.**  {song_name}\n"
    await ctx.send(queue_message)

@bot.command()
async def next(ctx, steps: int = 1):
    global current_index, playlist, vc, manual_skip, loop_enabled, base_playlist, added_songs, insert_index

    if not vc or not vc.is_connected():
        await ctx.send("❌ ain't connected to a voice channel")
        return

    steps = max(1, steps)
    if current_index + steps >= len(playlist):
        if loop_enabled:
            playlist = base_playlist.copy()
            current_index = 0
            added_songs.clear()
            insert_index = None
            manual_skip = True
            vc.stop()
            play_current_song()
            await ctx.send("🔁 loop activated")
        else:
            await ctx.send("❌ not enough songs in queue")
        return

    manual_skip = True
    current_index += steps
    vc.stop()
    play_current_song()
    await ctx.send(f"⏭ skipping {steps} song(s)...")

@bot.command()
async def skip(ctx, arg: str = None):
    global current_index, playlist, vc, current_audio_source, current_volume, manual_skip, loop_enabled, base_playlist, added_songs, insert_index

    if not vc or not vc.is_playing():
        await ctx.send("❌ nothing is playing")
        return

    if arg is None:
        if current_index < len(playlist) - 1:
            manual_skip = True
            current_index += 1
            vc.stop()
            play_current_song()
            await ctx.send("⏩ skipping...")
        elif loop_enabled:
            playlist = base_playlist.copy()
            current_index = 0
            added_songs.clear()
            insert_index = None
            manual_skip = True
            vc.stop()
            play_current_song()
            await ctx.send("🔁 loop activated")
        else:
            await ctx.send("❌ no more songs in queue")
        return

    try:
        idx = int(arg)
        if 0 <= idx < len(playlist):
            manual_skip = True
            current_index = idx
            vc.stop()
            play_current_song()
            await ctx.send(f"⏩ skipping to song {idx + 1}.")
        else:
            await ctx.send(f"❌ invalid index. must be between 0 and {len(playlist)-1}.")
        return
    except ValueError:
        pass

    total_seconds = None
    match = re.match(r"^(\d+):(\d+):(\d+)$", arg)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        total_seconds = hours * 3600 + minutes * 60 + seconds
    else:
        match = re.match(r"^(\d+):(\d+)$", arg)
        if match:
            minutes, seconds = map(int, match.groups())
            total_seconds = minutes * 60 + seconds
        else:
            try:
                total_seconds = int(arg)
            except ValueError:
                await ctx.send("❌ invalid time format")
                return

    if total_seconds is None:
        await ctx.send("❌ couldn't understand the argument")
        return

    manual_skip = True
    vc.stop()
    current_song = playlist[current_index]
    new_source = FFmpegPCMAudio(current_song, executable=FFMPEG_PATH, before_options=f"-ss {total_seconds}")
    new_source = discord.PCMVolumeTransformer(new_source)
    new_source.volume = current_volume
    current_audio_source = new_source
    vc.play(current_audio_source, after=lambda error: bot.loop.create_task(auto_next()))
    await ctx.send(f"⏩ playing from {arg} songs ago")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ stopping audio...")
    else:
        await ctx.send("❌ nothing is playing")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶ resuming song")
    else:
        await ctx.send("❌ audio isn't stopped")

@bot.command()
async def restart(ctx):
    global vc
    if not vc or not vc.is_connected():
        await ctx.send("❌ not connected to a voice channel")
        return

    vc.stop()
    play_current_song()
    await ctx.send("⏯ restarting...")

@bot.command()
async def volume(ctx, level: int = None):
    global current_volume
    if level is None:
        await ctx.send(f"🔊 volume right now: {int(current_volume * 100)}%")
        return

    if not (0 <= level <= 100):
        await ctx.send("❌ number must be between 0 and 100")
        return

    current_volume = level / 100.0
    if ctx.voice_client and ctx.voice_client.source:
        ctx.voice_client.source.volume = current_volume
        await ctx.send(f"🔊 volume set to {level}%")
    else:
        await ctx.send("❌ either nothing is playing or I'm not connected")

@bot.command()
async def songs(ctx):
    base_dir = os.path.join("media", "playlists")
    if not os.path.exists(base_dir):
        await ctx.send("❌ playlists directory not found")
        return

    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        await ctx.send("❌ no aviable playlists")
        return

    message = "📜 **aviable playlists and their songs:**\n\n"
    media_formats = (".mp3", ".ogg", ".wav", ".flac", ".m4a", ".mp4", ".mkv")
    for d in dirs:
        path = os.path.join(base_dir, d)
        files = sorted([f for f in os.listdir(path) if f.lower().endswith(media_formats)])
        song_list = "\n".join([f"   • {remove_extension(song)}" for song in files])
        message += f"**{d}**:\n{song_list}\n\n"
    await ctx.send(message)

@bot.command()
async def playlists(ctx):
    base_dir = os.path.join("media", "playlists")
    if not os.path.exists(base_dir):
        await ctx.send("❌ playlists directory not found")
        return

    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not dirs:
        await ctx.send("❌ no aviable playlists")
        return

    message = "**📜 aviable playlists:**\n" + "\n".join([f"   • {d}" for d in dirs])
    await ctx.send(message)

@bot.command()
async def commands(ctx):
    command_list = """
    **commands:**

	add "[song]"
	commands
	help
	join
	loop
	play [playlist]
	playlists
	previous [number]
	quit
	queue
	restart
	resume
	shuffle
	skip [hh:mm:ss]
	songs
	stop
	volume [number]
	whatisthis
	    
    """
    await ctx.send(command_list)

@bot.command()
async def previous(ctx, steps: int = 1):
    global current_index, playlist, vc, manual_skip, loop_enabled

    if not vc or not vc.is_connected():
        await ctx.send("❌ ain't connected to a voice channel")
        return

    steps = max(1, steps)

    if current_index - steps < 0:
        if loop_enabled:
            # Ir al final si hay loop
            current_index = len(playlist) - 1
        else:
            await ctx.send("❌ no previous songs")
            return
    else:
        current_index -= steps

    manual_skip = True
    vc.stop()
    play_current_song()
    await ctx.send(f"⏮ going back {steps} song(s)...")

@bot.command()
async def whatisthis(ctx):
    global current_index, playlist

    if not playlist:
        await ctx.send("❌ no songs in queue")
        return

    if current_index < 0 or current_index >= len(playlist):
        await ctx.send("❌ nothing is playing right now")
        return

    current_song = remove_extension(os.path.basename(playlist[current_index]))
    await ctx.send(f"🎶 this is: **{current_song}**")

@bot.command()
async def add(ctx, song_name: str):
    global playlist, playlist_path, added_songs, current_index, insert_index

    base_dir = os.path.join("media", "playlists")
    media_formats = (".mp3", ".ogg", ".wav", ".flac", ".m4a", ".mp4", ".mkv")
    song_path = None

    for playlist_dir in os.listdir(base_dir):
        playlist_dir_path = os.path.join(base_dir, playlist_dir)
        if os.path.isdir(playlist_dir_path):
            files = [f for f in os.listdir(playlist_dir_path) if f.lower().endswith(media_formats)]
            for file in files:
                if remove_extension(file).lower() == song_name.lower():
                    song_path = os.path.join(playlist_dir_path, file)
                    break
        if song_path:
            break

    if song_path:
        if insert_index is None or insert_index < current_index:
            insert_index = current_index + 1

        insert_index = min(insert_index, len(playlist))
        playlist.insert(insert_index, song_path)
        added_songs.append(song_path)
        await ctx.send(f"✅ song **{song_name}** added in position {insert_index + 1}.")
        insert_index += 1
    else:
        await ctx.send(f"❌ didn't found **{song_name}**")

@bot.command()
async def loop(ctx, state: str = None):
    global loop_enabled

    if state is None:
        await ctx.send(f"🔁 loop is {'true' if loop_enabled else 'false'}")
        return

    state = state.lower()
    if state == "true":
        loop_enabled = True
        await ctx.send("🔁 loop enabled")
    elif state == "false":
        loop_enabled = False
        await ctx.send("⏹ loop disabled")
    else:
        await ctx.send("❌ invalid value, use ture or false")

@bot.command()
async def shuffle(ctx):
    global playlist, current_index

    if not playlist or current_index >= len(playlist):
        await ctx.send("❌ no songs in queue")
        return

    current_song = playlist[current_index]
    remaining = playlist[current_index + 1:]
    random.shuffle(remaining)
    playlist = playlist[:current_index + 1] + remaining
    await ctx.send("🔀 shuffling...")

bot.run(TOKEN)
