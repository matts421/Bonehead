import discord
from discord.ext import commands
import typing
import random
import requests
import stats
import settings
import hangman_solver

WORDLIST_URL = "https://www.mit.edu/~ecprice/wordlist.10000"
HANGMAN_IMAGE_FOLDER = "C:\\Users\\Matt\\Desktop\\Bonehead\\hangman_images"
MW_DICTIONARY_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
MW_DICTIONARY_KEY = settings.MW_DICTIONARY


def check_guess(guess: str, word: str) -> typing.Tuple[bool, bool]:
    if guess == word:
        return False, True
    elif guess in word:
        return True, True
    else:
        return True, False
    

def amt_fcn(lives: int, progress: list, guesses: list):
    valid_progress = len(list(filter(lambda c: c != "\_", progress)))
    if lives == 0:
        return 100 * ((len(progress) - valid_progress) / len(progress)) + 5*len(guesses)
    else:
        return 100 + 10*lives - 10*(len(guesses) - valid_progress)


def handle_embed(playing: bool, win: bool, guesses: list, lives: int, word : str, progress : list):
    
    file = discord.File(f"{HANGMAN_IMAGE_FOLDER}\\{lives}.png", filename = f"{lives}.png")
    
    if guesses == []:
        embed = discord.Embed(
            colour = discord.Colour.blue(),
            description = "❤️" * lives + "🤍" * (6-lives)
        )
        embed.set_image(url = f"attachment://{lives}.png")
        embed.add_field(name = "Progress", value = (" ").join(progress).upper())

    elif not playing and win:
        embed = discord.Embed(
            colour = discord.Colour.dark_green(),
            description = "❤️" * lives + "🤍" * (6-lives),
            title = "Victory!"
        )
        embed.set_image(url = f"attachment://{lives}.png")
        embed.add_field(name = "Progress", value = (" ").join(word.upper()))
        embed.add_field(name = "Word", value = (" ").join(word.upper()))
    elif not playing and not win:
        embed = discord.Embed(
            colour = discord.Colour.dark_red(),
            description = "❤️" * lives + "🤍" * (6-lives),
            title = "Defeat!"
        )
        embed.set_image(url = f"attachment://{lives}.png")
        embed.add_field(name = "Progress", value = (" ").join(progress).upper())
        embed.add_field(name = "Word", value = (" ").join(word.upper()))
    elif win:
        embed = discord.Embed(
            colour = discord.Colour.green(),
            description = "❤️" * lives + "🤍" * (6-lives)
        )
        embed.set_image(url = f"attachment://{lives}.png")
        embed.add_field(name = "Progress", value = (" ").join(progress).upper())
    else:
        embed = discord.Embed(
            colour = discord.Colour.red(),
            description = "❤️" * lives + "🤍" * (6-lives)
        )
        embed.set_image(url = f"attachment://{lives}.png")
        embed.add_field(name = "Progress", value = (" ").join(progress).upper())

    embed.add_field(name="Guesses", value= ", ".join(guesses).upper(), inline=False)
    return file, embed


class HangmanPlayer:
    def __init__(self, member: discord.Member,
                 lives: int = 6, progress: list = [], guesses: list = [],
                 playing: bool = False):
        self.member = member
        self.lives = lives
        self.progress = progress
        self.guesses = guesses
        self.playing = playing


    def lose_life(self):
        self.lives -= 1


    @property
    def lives(self):
        return self._lives
    
    @lives.setter
    def lives(self, lives):
        if lives < 0:
            raise ValueError("Lives cannot be negative!")
        self._lives = lives


class HangmanGame:
    def __init__(self, player: HangmanPlayer, ctx: commands.Context, position: int, bot: commands.Bot):
        self.player = player
        self.ctx = ctx
        self.position = position
        self.bot = bot


    def start_game(self):
        raw_words = requests.get(WORDLIST_URL).content.splitlines()
        word = str(random.choice(raw_words))[2:-1]
        self.player.progress = ["\_"] * len(word)
        self.player.playing = True
        return word, raw_words
    

    async def play_game(self):
        player = self.player
        word, raw_words = self.start_game()
        await self.ctx.send("Now playing: **hangman**! Start with your first guess.")
        file, embed = handle_embed(player.playing, False, player.guesses, player.lives, word, player.progress)
        await self.ctx.send(file=file, embed=embed)

        words = map(lambda w: str(w)[2:-1], raw_words)
        words = filter(lambda w: len(w) == len(word), words)

        # good_guess, words = hangman_solver.hangman_guesser(self.player.guesses, self.player.progress, words)
        # print("good guess: ", good_guess)

        def check(m: discord.Message):
            return m.author == self.ctx.author and m.channel == self.ctx.channel
        
        while player.playing:
            good_guess, words = hangman_solver.hangman_guesser(self.player.guesses, self.player.progress, words)
            print("good guess: ", good_guess)

            guess_message = await self.bot.wait_for("message", check=check)
            guess = guess_message.content.strip().lower()
            if not guess.isalpha():
                await self.ctx.send("Guesses must only contain alphabetic characters!")
            elif guess in player.guesses:
                await self.ctx.send("You've already guessed that!")
            else: 
                player.guesses.append(guess)
                player.playing, win = check_guess(guess, word)

                if win:
                    if player.playing:
                        for i, c in enumerate(word):
                                    if guess == c:
                                        player.progress[i] = c
                        if "\_" not in player.progress:
                            player.playing = False
                            money_message = hangman_win(player, amt_fcn, self.position)
                    else:
                        player.progress = list(word.upper())
                        money_message = hangman_win(player, amt_fcn, self.position)
                else:
                    player.lose_life()


                if player.lives == 0:
                    player.playing = False
                    money_message = hangman_loss(player, amt_fcn, self.position)

                file, embed = handle_embed(player.playing, win, player.guesses, player.lives, word, player.progress)
                await self.ctx.send(file=file, embed=embed)

        definition = handle_definition(word)

        if definition:
            await self.ctx.send(definition)
        
        if money_message:
            await self.ctx.send(money_message)

        await self.ctx.send(embed = player.member.embed())


def hangman_win(player: HangmanPlayer, amount, position: int) -> str:
    money = amount(player.lives, player.progress, player.guesses)
    player.member.win()
    player.member.wallet.deposit(money)
    dollars, cents = stats.convert_to_dollars(money)
    stats.update_member(settings.MEMBERS_JSON_PATH, player.member.to_dictionary(), position)
    return f"You won $`{dollars}.{cents:02d}`"


def hangman_loss(player: HangmanPlayer, amount, position: int) -> str:
    money = amount(player.lives, player.progress, player.guesses)
    player.member.lose()
    try:
        player.member.wallet.withdraw(money)
    except ValueError:
        player.member.wallet.money = 0
    dollars, cents = stats.convert_to_dollars(money)
    stats.update_member(settings.MEMBERS_JSON_PATH, player.member.to_dictionary(), position)
    return f"You lost $`{dollars}.{cents:02d}`"
        

def handle_definition(word):
    url = f"{MW_DICTIONARY_URL}/{word}?key={MW_DICTIONARY_KEY}"
    data = requests.get(url).json()
    try:
        return f"**Definition**: {data[0]['shortdef'][0]}"
    except TypeError:
        return None
    except IndexError:
        return None



        