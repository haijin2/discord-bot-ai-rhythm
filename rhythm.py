import discord
from discord.ext import commands
import sqlite3
import yt_dlp
from dotenv import load_dotenv
from discord import Embed
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# get token
load_dotenv()
TOKEN = os.getenv("TOKEN")

@bot.event
async def on_ready():
    print(f'🎶 Logged in as {bot.user.name}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = ctx.voice_client  
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)

        else:
            await channel.connect()
        await ctx.send(f"🔊 Joined {channel}")
        await ctx.send(f"{ctx.author.mention} hindi ka na mag i-isa")
    else:
        await ctx.send("TANGINA WALA KA NAMAN SA VOICE CHANNEL E")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("BYE TANGINA MO")
    else:
        await ctx.send("⚠️ I'm not connected to any voice channel.")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command('join'))

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        title = info.get('title', 'Unknown')
    
    ctx.voice_client.stop()
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(url2, executable="ffmpeg"),
        after=lambda e: print(f"Finished playing: {e}")
    )
    await ctx.send(f"🎶 Now playing: **{title}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Music paused.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Music resumed.")

@bot.command()
async def stop(ctx):
    ctx.voice_client.stop()
    await ctx.send("⏹️ Music stopped.")

# radio stations
# fetch from the db
def fetch_station_url(station_name):
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM stations WHERE name = ?", (station_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

@bot.command()
async def radio(ctx, station: str = "vibe"):
    gif = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWtxcjl2NHY3NDJkY2ppb3hva2xkMXFxaWppcG1rYmJoYXcwbTBlayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jEl8zlvatJBVS/giphy.gif"
    station = station.lower()

    # fetch the station url from the db
    url = fetch_station_url(station)
    
    if not url:
        conn = sqlite3.connect('stations.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM stations")
        available = [row[0] for row in cursor.fetchall()]
        conn.close()

        await ctx.send(f"unknown station. Available: {', '.join(available)}")
        return

    if not ctx.author.voice:
        await ctx.send("wala ka naman sa voice channel")
        return

    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect()
    elif vc.channel != ctx.author.voice.channel:
        await vc.move_to(ctx.author.voice.channel)

    vc.stop()

    # Use yt_dlp for YouTube
    if "youtube.com" in url:
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
    else:
        audio_url = url

    ffmpeg_audio = discord.FFmpegPCMAudio(
        audio_url,
        executable="ffmpeg",
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    try:
        vc.play(ffmpeg_audio, after=lambda e: print(f"Finished playing: {e}"))
        embed = Embed(title=f"📻 Now playing: {station} radio", color=0x1DB954)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error playing radio: {e}")

def fetch_all_station_names():
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM stations")
    results = cursor.fetchall()
    conn.close()
    return [row[0] for row in results]

#@bot.command()
#async def stations(ctx):
#    stations = fetch_all_station_names()
#    station_list = '\n'.join(f"• **{name}**" for name in stations)
#    await ctx.send(f"mga stations na pwede kong katahin hehehe: \n{station_list}")

bot.run(TOKEN)  
