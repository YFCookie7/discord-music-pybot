import discord
from discord.ext import commands
import yt_dlp
import os
import json

audio_dir = "C:/Users/mikel/Documents/Github/discord-music-bot/audio/" 
audio_naming = f"%(title)s.%(ext)s"
json_file = "audio.json"
FFMPEG_PATH = "C:/ffmpeg/ffmpeg.exe"

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
    'outtmpl': "/audio/"+audio_naming,   # ~/audio/abc.mp3
    "quiet": True,
}

def removelist(yt_url):
    return yt_url.split("&", 1)[0]

def get_audio(yt_url):
    # Check if the audio file already exists
    if os.path.exists(json_file) and os.stat(json_file).st_size > 0:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        for data in json_data:
            if data.get('yt_url') == yt_url:
                return data.get('audio_filename')
    return "not found"

def download_audio(yt_url):
    # Download the audio file if it does not exist
    print("Downloading: " + yt_url)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=True)
        title = info['title']
        ext = "mp3"
        audio_file = ydl.prepare_filename(info)
        audio_filename = (f"{title}.{ext}")
        print("Downloaded: " + audio_filename)

    # Save the audio data to json
    data = {
        'audio_filename': audio_filename,
        'yt_url': yt_url
    }
    if os.path.exists(json_file) and os.stat(json_file).st_size > 0:
        with open(json_file, 'r+', encoding='utf-8') as f:
            json_data = json.load(f)
            json_data.append(data)
            f.seek(0)  # Move the file pointer to the beginning of the file
            json.dump(json_data, f, ensure_ascii=False, indent=4)
            f.truncate()  # Truncate the file to remove any remaining content
    else:
        # Create a new JSON file with the data
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([data], f, ensure_ascii=False, indent=4)
    return audio_filename


class Play(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Tutorial for interacting with music bot")
    async def help(self ,ctx):
        await ctx.defer()
        await ctx.respond("no help")

    @discord.slash_command(description="Add the bot to voice channel")
    async def join(self ,ctx):
        await ctx.defer()
        if(ctx.author.voice):
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.respond("Bot is now in voice channel")
        else:
            await ctx.respond("You have to join the voice channel first")

    @discord.slash_command(description="Remove the bot from voice channel")
    async def quit(self ,ctx):
        if ctx.voice_client is not None:
            await ctx.defer()
            await ctx.voice_client.disconnect()
        await ctx.respond("Bot has left the voice channel")

    @discord.slash_command(description="Play music")
    async def play(self, ctx, yt_url: discord.Option(str, description="Input youtube URL", required = True)):
        # Stop the current audio if it is playing
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        yt_url=removelist(yt_url)
        audio_filename = get_audio(yt_url)
        if audio_filename == "not found":
            audio_filename = download_audio(yt_url)

        channel = ctx.author.voice.channel
        voice = ctx.voice_client or await channel.connect()
        print("Now playing: " + audio_filename)
        voice.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=audio_dir + audio_filename))

    @discord.slash_command(description="Stop music")
    async def stop(self ,ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.ctx = None
        else:
            await ctx.send("No audio is currently playing.")

    @discord.slash_command(description="Pause music")
    async def pause(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("No audio is currently playing.")

    @discord.slash_command(description="Resume music")
    async def resume(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Audio is not currently paused.")

def setup(bot):
    bot.add_cog(Play(bot))