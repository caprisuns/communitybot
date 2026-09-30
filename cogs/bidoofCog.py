import discord
from discord.ext import commands
import openai
import os

# Make sure the OpenAI-KEY environment variable is set correctly
my_secret = os.environ['OpenAI-KEY']
openai.api_key = my_secret 

class Bidoof(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.content.lower().startswith("bidoof"):
            try:
              response = openai.ChatCompletion.create(
                  model="gpt-3.5-turbo",
                  messages=[
                      {"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": message.content},
                  ],
              )
              await message.channel.send(response.choices[0].message["content"])
            except Exception as e:
                await message.channel.send(f"An error occurred: {str(e)}")


async def setup(bot):
    await bot.add_cog(Bidoof(bot))
    print('Bidoof has loaded')
