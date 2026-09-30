import discord
from discord.ext import commands
import csv
import json
import asyncio
import random

CHANNEL_ID = 1148630648425291869  # channel you type in // test id: 1076337166998839326 // actual; 1114897266478678062
QUOTE_CHANNEL_ID = 1154090821386240122  # quote channel // test id: 1119388035147112628 // actual; 1119067715806707822

class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == "⭐":
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            author_name = message.author.name
            author_discriminator = message.author.discriminator

            embed = discord.Embed(title='', description=message.clean_content,
                                  color=discord.Color.from_rgb(255, 255, 255))
            embed.set_author(name=author_name, icon_url=message.author.avatar.url)
            embed.add_field(name="", value=f"[context]({message.jump_url})", inline=True)

            # Handle attachments
            for attachment in message.attachments:
                if attachment.width:  # Check if it's an image attachment
                    # Remove unnecessary parameters from the image URL
                    image_url = attachment.url.split("?")[0]
                    embed.set_image(url=image_url)
                else:
                    embed.description += f"\n[Attachment]({attachment.url})"

            target_channel = self.bot.get_channel(QUOTE_CHANNEL_ID)
            await target_channel.send(embed=embed)

    @commands.command()
    async def backup(self, ctx, channel_name: str):
        try:
            target_channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)

            if target_channel is None:
                await ctx.send("Channel not found.")
                return

            file_name = "message_backup.csv"
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(["Author", "Created At", "Content", "Embeds"])

                async for message in target_channel.history(limit=None):
                    author = message.author.display_name
                    created_at = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    content = json.dumps(message.content)
                    embeds = [json.dumps(embed.to_dict()) for embed in message.embeds]

                    csv_writer.writerow([author, created_at, content, "\n".join(embeds)])

            await ctx.send(f"Backup completed successfully. Data saved in {file_name}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @commands.command()
    async def restore(self, ctx):
        try:
            channel = await ctx.guild.create_text_channel('quotes')

            file_name = "message_backup.csv"
            with open(file_name, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)

                for row in csv_reader:
                    author = row["Author"]
                    created_at = row["Created At"]
                    content = json.loads(row["Content"])
                    embeds = row["Embeds"].split("\n")

                    embed = discord.Embed(description=content)

                    for embed_str in embeds:
                        if embed_str:
                            embed_dict = json.loads(embed_str)
                            embed_dict["type"] = "rich"
                            embed = discord.Embed.from_dict(embed_dict)

                    await asyncio.sleep(random.randint(30, 60))
                    await channel.send(embed=embed)

            await ctx.send("Messages restored successfully.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Quote(bot))
    print('Quote has loaded')
