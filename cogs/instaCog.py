import discord
from discord.ext import commands

class Insta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message was sent in the specific channel you mentioned
        if message.channel.id == 1154087567466172567:  # Replace with the actual channel ID
            # Check if the message has an attachment (image)
            if message.attachments:
                # Add a thumbs-up (👍) reaction to the message
                await message.add_reaction('👍')
                
                # Send a message with a comment reaction (💬) to indicate comments
                await message.add_reaction('💬')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Check if the reaction is added by a bot to avoid loops
        if user.bot:
            return

        # Check if the reaction is the comment reaction (💬)
        if str(reaction.emoji) == '💬':
            # Ensure the reaction is on a message in the specific channel
            if reaction.message.channel.id == 1154087567466172567:  # Replace with the actual channel ID
                # Create a thread for the image and send a message in the thread
                image_message = reaction.message
                image_url = image_message.attachments[0].url if image_message.attachments else None

                if image_url:
                    # Create a new thread for the image
                    thread_channel = await image_message.create_thread(
                        name=f"{image_message.author.display_name}'s food'"
                    )
                    await thread_channel.send('')

async def setup(bot):
    await bot.add_cog(Insta(bot))
    print('Insta has loaded')