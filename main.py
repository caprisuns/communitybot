import discord
from discord.ext import commands
from webserver import keep_alive
import os
import asyncio
import traceback
import sys

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='bi ', intents=intents)
intents.reactions = True

#cogs.bidoofCog

initialExtensions = [
    'cogs.quoteCog', 'cogs.wordcloudCog', 'cogs.moneyCog', 'cogs.instaCog', 'cogs.tiktokCog', 'cogs.fighterCog', 'cogs.musicCog'
]


async def load_extensions():
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      # cut off the .py from the file name
      await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_member_update(before, after):
  if before.status != after.status and after.status == discord.Status.online:
    # The user has come online
    channel_id = 1154086953025814672  # Replace with your desired channel ID
    channel = bot.get_channel(channel_id)
    if channel:
      await channel.send(f'{after.mention} is now online!')


TOKEN = ''

keep_alive()


async def main():
  for extension in initialExtensions:
    try:
      await bot.load_extension(extension)
    except Exception as e:
      print(f'Failed to load extension {extension}', file=sys.stderr)
      traceback.print_exc()

  await bot.start(TOKEN)


asyncio.run(main())


TOKEN = ''

