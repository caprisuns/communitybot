import discord
from discord.ext import commands
import csv
import os
import random
from discord.errors import DiscordException



class Money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_balances = {}
        self.user_message_count = {}  # Track the number of messages sent by each user
        self.CSV_FILE = 'user_balances.csv'

        # Check if the CSV file exists, and if not, create it
        if not os.path.exists(self.CSV_FILE):
            with open(self.CSV_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['UserID', 'Balance'])

        # Load user balances from the CSV file into the dictionary
        with open(self.CSV_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.user_balances[int(row['UserID'])] = int(row['Balance'])

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after_seconds = round(error.retry_after)
            em = discord.Embed(title="cooldown", description=f"Wait {retry_after_seconds} seconds.",
                               color=0xFF0000)  # Replace with your desired color code
            await ctx.send(embed=em)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required arguments. Please provide the target user.")
        # Add more error handling as needed
        else:
            # Handle other errors or log them
            print(f"An error occurred: {error}")

    # Command to check the user's balance or another user's balance
    @commands.command(name='balance', help='Check your balance or someone else\'s balance.')
    async def check_balance(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        user_id = user.id
        balance = self.user_balances.get(user_id, 0)

        embed = discord.Embed(title=f'Balance for {user.display_name}', color=discord.Color.blue())
        embed.add_field(name='Balance', value=f'{balance} coins')
        await ctx.send(embed=embed)

    # Event handler to update user balances when they send a message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore messages from other bots

        user_id = message.author.id
        self.user_message_count[user_id] = self.user_message_count.get(user_id, 0) + 1

        # Check if the user has sent 3 messages
        if self.user_message_count.get(user_id, 0) % 3 == 0:
            # Award 1 coin for every 3 messages
            self.update_user_balance(user_id, 1)

    @commands.command(name='give', help='Give money to another user with a 20% tax.')
    async def give_money(self, ctx, recipient: discord.User, amount: int):
        sender_id = ctx.author.id
        recipient_id = recipient.id

        # Check if the sender has enough money to give
        if sender_id not in self.user_balances or self.user_balances[sender_id] < amount:
            await ctx.send("You don't have enough money to give.")
            return

        # Calculate the tax amount
        tax_amount = int(amount * 0.2)
        net_amount = amount - tax_amount

        # Transfer money (net amount) from sender to recipient
        self.user_balances[sender_id] -= amount
        self.user_balances[recipient_id] = self.user_balances.get(recipient_id, 0) + net_amount

        # Update the CSV file
        with open(self.CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['UserID', 'Balance'])
            for user, balance in self.user_balances.items():
                writer.writerow([user, balance])

        await ctx.send(
            f"You gave {net_amount} coins to {recipient.display_name} after a 20% tax of {tax_amount} coins.")

    @commands.command(name='steal', help='Attempt to steal money from another user.')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 use per 60 seconds per user
    async def steal_money(self, ctx, target: discord.User):
        thief_id = ctx.author.id
        target_id = target.id

        try:
            # Check if the thief has enough money to attempt the theft
            if thief_id not in self.user_balances or self.user_balances[thief_id] < 500:
                await ctx.send("You need at least 500 coins to attempt a theft.")
                return

            # Check if the target has any money to steal
            if target_id not in self.user_balances or self.user_balances[target_id] <= 0:
                await ctx.send(f"{target.display_name} doesn't have any money to steal.")
                return

            # Determine whether the theft is successful
            success_chance = random.randint(1, 100)
            if success_chance <= 37:  # 50% chance of success (you can adjust this)
                stolen_amount = random.randint(1, self.user_balances[target_id])
                await ctx.send(
                    f"{ctx.author.display_name} successfully stole {stolen_amount} coins from {target.display_name}!")
                self.user_balances[thief_id] = self.user_balances.get(thief_id, 0) + stolen_amount
                self.user_balances[target_id] -= stolen_amount

                # Update the CSV file
                self.update_csv_file()

            else:
                # If the theft fails, the thief must pay back 500 coins
                await ctx.send(f"Your attempt to steal from {target.display_name} failed. "
                               f"You must pay back 500 coins as compensation.")
                self.user_balances[thief_id] -= 500
                self.user_balances[target_id] += 500

                # Update the CSV file
                self.update_csv_file()



        except commands.CommandOnCooldown as e:
            # Inform the user about the remaining cooldown time
            print(f"This command is on cooldown. Try again in {int(e.retry_after)} seconds.")

    def update_user_balance(self, user_id, amount):
        """Update a user's balance by a specified amount."""
        if user_id in self.user_balances:
            self.user_balances[user_id] += amount
        else:
            self.user_balances[user_id] = amount

        # Update the CSV file
        with open(self.CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['UserID', 'Balance'])
            for user, balance in self.user_balances.items():
                writer.writerow([user, balance])


async def setup(bot):
    await bot.add_cog(Money(bot))
    print('Money has loaded')
