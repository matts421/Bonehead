import discord
from discord.ext import commands
import typing
import requests
import random
import settings
import stats
from typing import Tuple, Literal
from blackjack import BlackjackGame, BlackjackPlayer, Dealer, Deck, dict_to_cards, STANDARD_CARDS
import hangman as hm

MW_DICTIONARY = settings.MW_DICTIONARY
MINIMUM_WAGER = 50


class Games(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(brief = "Play hangman!",
                      description = "Play hangman with a randomly generated word")
    async def hangman(self, ctx):
        author = ctx.author
        position = stats.find_member(settings.MEMBERS_JSON_PATH, author.id)

        if position == -1:
            await ctx.send("You haven't registered yet! Use !stats to register.")
            return

        member_dict = stats.get_member(settings.MEMBERS_JSON_PATH, position)
        member = stats.dict_to_member(member_dict)
        player = hm.HangmanPlayer(member, lives = 6, guesses = [], progress = [])
        game = hm.HangmanGame(player, ctx, position, self.bot)

        await game.play_game()


    @commands.command()
    async def riddle(self, ctx):
        url = "https://riddles-api.vercel.app/random"
        data = requests.get(url).json()
        riddle = data['riddle']
        answer = data['answer']
        await ctx.send(f"{riddle}\n||{answer}||")
        

    @commands.command(aliases = ['r'])
    async def roulette(self, ctx, wager: float, guess: Literal['red', 'black']):
        if guess not in ['red', 'black']:
            await ctx.send("Invalid choice! Please enter red or black.")
            return
        
        author = ctx.author
        position = stats.find_member(settings.MEMBERS_JSON_PATH, author.id)

        if position == -1:
            await ctx.send("You haven't registered yet! Use !stats to register.")
            return
        
        member_dict = stats.get_member(settings.MEMBERS_JSON_PATH, position)
        member = stats.dict_to_member(member_dict)
        if wager > member.wallet.money:
            await ctx.send("You don't have enough money for that wager!")
            return
        
        if wager < MINIMUM_WAGER:
            await ctx.send("This wager is too low! The minimum wager is `$50.00`")
            return
        
        number = random.randint(1, 38)
        if 1 <= number <= 18:
            win_color = 'red'
        elif 18 < number < 36:
            win_color = 'black'
        else:
            win_color = 'green'

        if win_color == guess:
            outcome = "win"
            member.wallet.deposit(wager)
        else:
            outcome = "lose"
            member.wallet.withdraw(wager)

        await ctx.send(f"The ball falls on `{win_color}`. You {outcome}!")
        stats.update_member(settings.MEMBERS_JSON_PATH, member.to_dictionary(), position)

    
    @commands.command(description = "Play blackjack against Bonehead!")
    async def blackjack(self, ctx,
                        wager: float = commands.parameter(default = 50.00, description = "Betting amount")):
        position = stats.find_member(settings.MEMBERS_JSON_PATH, ctx.author.id)
        member_dict = stats.get_member(settings.MEMBERS_JSON_PATH, position)
        member = stats.dict_to_member(member_dict)

        player = BlackjackPlayer(member, hand = [])
        dealer = Dealer(Deck(dict_to_cards(STANDARD_CARDS)), hand = [])

        if wager < MINIMUM_WAGER:
            await ctx.send("The minimum wager is `$50.00`!")
            return
        elif wager > member.wallet.money:
            await ctx.send("Insufficient funds!")
            return

        game = BlackjackGame(dealer, player, ctx, wager)
        
        await game.play_game()

        member_dict = member.to_dictionary()
        stats.update_member(settings.MEMBERS_JSON_PATH, member_dict, position)

        
        
async def setup(bot):
    await bot.add_cog(Games(bot))
