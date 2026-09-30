import discord
from discord.ext import commands, tasks
import random
import pickle
import asyncio
from wordcloud import WordCloud
from collections import defaultdict

# Constants
COMMON_WORDS = {"i", "you", "u", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
                "my", "your", "his", "its", "our", "their", "this", "that", "these", "those", "a", "an", "the",
                "and", "but", "or", "for", "nor", "so", "yet", "am", "is", "are", "was", "were", "be", "been",
                "being", "have", "has", "had", "do", "does", "did", "will", "shall", "should", "would", "can",
                "could", "may", "might", "must", "of", "in", "on", "at", "by", "with", "about", "above", "below",
                "under", "to", "from", "into", "through", "during", "before", "after", "between", "because",
                "it's", "that's", "there's", "here's", "what's", "who's", "where's", "when's", "why's", "im",
                "ur", "no", "what", "not", "like"}

CHANNEL_ID = 1154086953025814672  # Replace with your channel ID

class worldCloudCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.server_word_frequency = defaultdict(int)
        self.personal_word_frequency = defaultdict(int)

        # Load existing word cloud data or initialize empty
        try:
            with open('word_cloud_data.pkl', 'rb') as file:
                self.word_cloud_data = pickle.load(file)
        except FileNotFoundError:
            self.word_cloud_data = {}

        # Task to fetch and process old messages
        self.fetch_and_process_old_messages.start()

    def save_word_cloud_data(self):
        with open('word_cloud_data.pkl', 'wb') as file:
            pickle.dump(self.word_cloud_data, file)

    def generate_wordcloud(self, data, filename):
        wordcloud = WordCloud().generate_from_frequencies(data)
        wordcloud.to_file(filename, width=800, height=400)

    @tasks.loop(minutes=30)
    async def fetch_and_process_old_messages(self):
        channel = discord.utils.get(self.bot.get_all_channels(), id=CHANNEL_ID)
        async for message in channel.history(limit=None):
            if message.author != self.bot.user:
                words = message.content.split()
                for word in words:
                    word = word.strip('.,!?":;()[]{}').lower()
                    if word and word not in COMMON_WORDS:
                        self.server_word_frequency[word] += 1
        # Save the updated word cloud data
        self.save_word_cloud_data()

    @fetch_and_process_old_messages.before_loop
    async def before_fetch_and_process_old_messages(self):
        await self.bot.wait_until_ready()

    async def save_and_generate_wordcloud(self):
        while True:
            try:
                print("Task is running")
                self.generate_wordcloud(self.server_word_frequency, "server_wordcloud.png")
            except Exception as e:
                print(f"An error occurred during word cloud generation: {e}")
            await asyncio.sleep(3600)

    @commands.command()
    async def cloud(self, ctx):
        # Check if the command was issued in the correct channel
        print(f"Command received in channel ID: {ctx.channel.id}")

        if ctx.channel.id == CHANNEL_ID:
            # Add a reaction to indicate that the bot is processing the request
            await ctx.message.add_reaction("⏳")  # You can use any emoji you prefer

            # Generate the word cloud
            print("Generating word cloud...")
            try:
                self.generate_wordcloud(self.server_word_frequency, "server_wordcloud.png")

                # Send the generated word cloud image to the channel
                with open("server_wordcloud.png", "rb") as file:
                    wordcloud_image = discord.File(file)
                    await ctx.send(file=wordcloud_image)

                # Remove the processing reaction and add a confirmation reaction
                await ctx.message.clear_reactions()
                await ctx.message.add_reaction("✅")  # You can use any emoji you prefer to indicate success

                print("Word cloud sent.")
            except Exception as e:
                print(f"An error occurred during word cloud generation: {e}")
                await ctx.send("An error occurred during word cloud generation.")
        else:
            await ctx.send("This command can only be used in the designated channel.")

    @commands.command()
    async def ping(self, ctx):
        print("Command Sent")
        print(self.bot.latency)

        await ctx.send('Pong! **{0}**ms'.format(round(self.bot.latency * 1000, 1)))

async def setup(bot):
    await bot.add_cog(worldCloudCog(bot))
    print('Word Cloud has loaded')
