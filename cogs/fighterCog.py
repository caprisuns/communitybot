import math

import discord
from discord.ext import commands
import random
import csv
import asyncio


class FighterGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_balances = {}
        self.CSV_FILE = 'user_balances.csv'
        self.load_user_balances()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after_seconds = round(error.retry_after)
            em = discord.Embed(title="error: cooldown", description=f"Wait {retry_after_seconds} seconds.",
                               color=0xFF0000)  # Replace with your desired color code
            await ctx.send(embed=em)
        elif isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(title="error: missing requirements", description=f"check the command",
                               color=0xFF0000)  # Replace with your desired color code
            await ctx.send(embed=em)
        # Add more error handling as needed
        else:
            # Handle other errors or log them
            print(f"An error occurred: {error}")

    def load_user_balances(self):
        with open(self.CSV_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            self.user_balances = {int(row[0]): int(row[1]) for row in reader}

    def update_user_balance(self, user_id, amount):
        if user_id in self.user_balances:
            self.user_balances[user_id] += amount
        else:
            self.user_balances[user_id] = amount

        with open(self.CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['UserID', 'Balance'])
            for user, balance in self.user_balances.items():
                writer.writerow([user, balance])

    @commands.command(name='attack')
    @commands.cooldown(3, 30, commands.BucketType.user)  # 1 use per 60 seconds per user
    async def attack(self, ctx, opponent: discord.Member, wager: int):
        if self.user_balances[ctx.author.id] < wager or self.user_balances[opponent.id] < wager:
            await ctx.send("One of the players does not have enough money for this wager.")
            return

        # Move this instantiation inside the 'yes' block if needed.
        game = FighterGameInstance(ctx, opponent, wager, self.update_user_balance, self.bot)
        await game.start()

class FighterGameInstance:
    def __init__(self, ctx, opponent, wager, update_balance_callback, bot):
        self.ctx = ctx
        self.players = [ctx.author, opponent]
        self.wager = wager
        self.update_balance = update_balance_callback
        self.turn = 0
        self.hp = {player: 200 for player in self.players}
        self.actions = ['kick', 'punch', 'heal', 'block']
        self.bot = bot

    def check_message(self, message):
        return message.author == self.players[
            self.turn] and message.channel == self.ctx.channel and message.content.lower() in self.actions

    async def start(self):
        await self.ctx.send(f"{self.ctx.author.mention} has challenged {self.players[1].mention} to a duel for {self.wager}!")

        while all(hp > 0 for hp in self.hp.values()):
            await self.ctx.send(
                f"It's {self.players[self.turn].mention}'s turn. Choose an action: {', '.join(self.actions)}")
            try:
                action_message = await self.bot.wait_for('message', check=self.check_message, timeout=120)
            except asyncio.TimeoutError:
                await self.ctx.send(
                    f"{self.players[self.turn].mention} took too long. {self.players[1 - self.turn].mention} wins!")
                self.update_balance(self.players[1 - self.turn].id, self.wager)
                return

        action = action_message.content.lower()
        if action == 'heal':
            heal_amount = random.randint(30, 40)
            self.hp[self.players[self.turn]] = min(200, self.hp[self.players[self.turn]] + heal_amount)
            current_hp = math.ceil(self.hp[self.players[self.turn]])
            await self.ctx.send(
                f"{self.players[self.turn].mention} healed for {heal_amount} HP. Current HP: {current_hp}")
        elif action in ['kick', 'punch']:
            damage = random.randint(63, 85) if action == 'kick' else random.randint(50, 55)
            block_chance = 0.7 if action == 'kick' else 0.3
            if random.random() < block_chance:
                damage = round(damage * 0.3)
                await self.ctx.send(f"{self.players[1 - self.turn].mention} blocked the attack!")
            elif random.random() < 0.2:
                damage * 2
                await self.ctx.send(f"{self.players[self.turn].mention} landed a **critical hit**!")
            self.hp[self.players[1 - self.turn]] -= damage
            current_hp = math.ceil(self.hp[self.players[1 - self.turn]])
            await self.ctx.send(
                f"{self.players[self.turn].mention} dealt {damage} damage. {self.players[1 - self.turn].mention}'s Current HP: {current_hp}")
        self.turn = 1 - self.turn

        winner = self.players[0] if self.hp[self.players[0]] > 0 else self.players[1]
        await self.ctx.send(f"{winner.mention} wins the duel and receives {self.wager}!")
        self.update_balance(winner.id, self.wager)


def check_message(self, message):
    return message.author == self.players[
        self.turn] and message.channel == self.ctx.channel and message.content.lower() in self.actions


async def setup(bot):
    await bot.add_cog(FighterGame(bot))
    print('FighterGame has loaded')
