import csv
import time
from datetime import datetime, timedelta, date
import asyncio
from collections import namedtuple, deque

from discord.ext import commands
from discord.ext.commands import Bot

# constants
PREFIX = "~"
TOKEN = "NTMxNTk2NDIwMzI3NjY5ODAz.Dxm3PA.mO237_LJZq9Q6Fxh_GWip3zaAOk"

bot = Bot(command_prefix=PREFIX)
players = {}
queues = {}
args = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        print(error)

@bot.command(pass_context=True)
async def hello(ctx):
    if ctx.message.author.id == "148229646415036417":
        await bot.say("Fuck off")
    else:
        await bot.say(f"Hello {ctx.message.author.mention}!")

@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await bot.join_voice_channel(channel)
    players[ctx.message.server.id] = []
    queues[ctx.message.server.id] = []

@bot.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    await voice_client.disconnect()

@bot.command(pass_context=True)
async def play(ctx, *, url):
    server = ctx.message.server
    voice_client = bot.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, ytdl_options={'quiet': True, 'default_search': 'auto'},
                                                   before_options=args,
                                                   after=lambda: check_queue(server.id))

    if not queues[server.id] and not players[server.id]:
        players[server.id] = player
        player.volume = 0.08
        player.start()
        print('no q')
    elif not queues[server.id] and players[server.id].is_done():
        players[server.id] = player
        player.volume = 0.08
        player.start()
        print('no q')
    else:
        if server.id in queues:
            queues[server.id].append(player)
            print('q1')
        else:
            queues[server.id] = [player]
            print('q2')

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.volume = 0.04
        player.start()

@bot.command(pass_context=True)
async def skip(ctx):
    if ctx.message.author.id == "148229646415036417":
        players[ctx.message.server.id].stop()
    else:
        await bot.say("You're not my supervisor!")

@bot.command(pass_context=True)
async def stat(ctx):
    """Returns a CSV file of all users on the server."""
    await bot.request_offline_members(ctx.message.server)
    before = time.time()
    nicknames = [m.display_name for m in ctx.message.server.members]
    roles = [m.roles for m in ctx.message.server.members]
    rn = [[m.name for m in line] for line in roles]
    with open('temp.csv', mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        for i in range(len(rn)):
            writer.writerow([nicknames[i], rn[i]])
    after = time.time()
    await bot.send_file(ctx.message.author, 'temp.csv', filename='stats.csv',
                        content="Here you go! Check your PM's. Generated in {:.4}ms.".format((after - before) * 1000))

@bot.command(pass_context=True)
async def activity(ctx, threshold=-1):
    if threshold != -1:
        dt = datetime.utcnow() - timedelta(days=int(threshold))
    else:
        dt = datetime(year=date.today().year, month=date.today().month, day=1)
    print(dt)
    authors = []
    timestamps = []
    val = ""
    for channel in ctx.message.server.channels:
        async for message in bot.logs_from(channel, limit=5000, after=dt, reverse=False):
            author = message.author.display_name

            if author not in authors:
                authors.append(author)
                timestamps.append(message.timestamp)
            elif timestamps[authors.index(author)] < message.timestamp:
                timestamps[authors.index(author)] = message.timestamp

    print(len(authors))
    for i in range(len(authors)):
        if len(val) + len(authors[i] + '     ' + str(timestamps[i]) + '\n') < 1990:
            val += (authors[i] + '     ' + str(timestamps[i]) + '\n')
        else:
            print("send")
            await bot.send_message(ctx.message.author,
                                   content="```" + val + "```")
            val = ""

    await bot.send_message(ctx.message.author,
                           content="```" + val + "```")

@bot.command(pass_context=True)
async def help(ctx):
    await bot.say('Ask InvaderZM.')

@bot.event
async def on_message(message):
    if message.author.bot is False and message.author.id == "148229646415036417":
        if message.content.startswith("bruh"):
            await bot.send_message(message.channel, "bruh")
        elif message.content.startswith("ayy"):
            await bot.send_message(message.channel, "lmao")
        elif message.content.startswith("noice"):
            await bot.send_message(message.channel, "smort")
        elif message.content.startswith("smort"):
            await bot.send_message(message.channel, "toit")
        elif message.content.startswith("toit"):
            await bot.send_message(message.channel, "noice")
    await bot.process_commands(message)

if __name__ == '__main__':
    bot.run(TOKEN)