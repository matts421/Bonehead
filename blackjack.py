import discord
from discord.ext import commands
import stats
from typing import Literal, Any, Tuple
import random
import settings

# deal to player, deal to dealer
# deal to player, deal to dealer (face up)
SUITS = {'clubs': "♣️", 'diamonds' : "♦️", 'hearts': "♥️", 'spades': "♠️"}
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {"2" : 2,
              "3": 3,
              "4": 4,
              "5": 5,
              "6": 6,
              "7": 7,
              "8": 8,
              "9": 9,
              "10": 10,
              "J": 10,
              "Q": 10,
              "K": 10,
              "A": [1, 11]}


STANDARD_CARDS = {suit : [rank for rank in RANKS] for suit in SUITS}
INITIAL_CARD_NUMBER = 2


def dict_to_cards(card_dict: dict) -> list:
    cards = []
    for suit in card_dict.keys():
        cards.extend([Card(suit, rank) for rank in card_dict[suit]])
    return cards


def hand_value(hand: list) -> (list):
    n = len([i for (i, card) in enumerate(hand) if card.rank == "A"])
    if n == 0 :
        totals = [0]
    else:
        totals = [0 for _ in range(2 * n)]

    for card in hand:
        rank = card.rank
        if rank == "A":
            totals[:n] = [total + 1 for total in totals[:n]]
            totals[n:] = [total + 11 for total in totals[n:]]
        else:
            totals = [total + RANK_VALUES[rank] for total in totals]

    return totals


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"

    @property
    def suit(self):
        return self._suit
    
    @suit.setter
    def suit(self, suit):
        if suit not in SUITS.keys():
            raise ValueError("Invalid suit!")
        self._suit = suit


    @property
    def rank(self):
        return self._rank
    
    @rank.setter
    def rank(self, rank):
        if rank not in RANKS:
            raise ValueError("Invalid rank!")
        self._rank = rank


def card_to_emoji(card: Card):
    if card:
        return f"`{SUITS[card.suit]}{card.rank}`"
    else:
        return f"`??`"


def hand_to_emoji(hand: list):
    out = []
    for card in hand:
        out.append(card_to_emoji(card))
    return ", ".join(out)


class Deck:
    def __init__(self, cards: list):
        self.cards = cards


    def shuffle(self):
        random.shuffle(self.cards)


    def remove_card(self) -> Card:
        return self.cards.pop()


    def add_card(self, card: Card) -> None:
        self.cards.append(card)


class BlackjackPlayer:
    def __init__(self, member: stats.Member, hand: list = [], playing: bool = False):
        self.member = member
        self.hand = hand
        self.playing = playing

    def check_playing(self) -> bool:
        values = hand_value(self.hand)
        return any(value < 21 for value in values)


class Dealer:
    def __init__(self, deck: Deck, hand: list = []):
        self.deck = deck
        self.hand = hand


    def deal(self, deck: Deck, receiver: BlackjackPlayer) -> None:
        card = deck.remove_card()
        receiver.hand.append(card)

    
    def end_game(self) -> list:
        values = hand_value(self.hand)
        while all([value < 17 for value in values]):
            self.deal(self.deck, self)
            values = hand_value(self.hand)
        return filter(lambda n: n >= 17, values)


async def handle_winner(player: BlackjackPlayer, dealer_values: list | None, wager: float, ctx) -> None:
    if dealer_values:
        values = hand_value(player.hand)
        if all(value > 21 for value in values):
            player.member.wallet.withdraw(wager)
            dollars, cents = stats.convert_to_dollars(wager)
            await ctx.send(f"**Bust!** You lost `${dollars:,}.{cents:02d}`")
        else:
            player_best = max(filter(lambda n: n <= 21, values))
            
            try:
                dealer_best = max(filter(lambda n: n <= 21, dealer_values))
            except ValueError:
                dealer_best = 0

            if player_best == dealer_best:
                await ctx.send(f"**Push!** Nobody wins.")
                return
            elif player_best == 21:
                player.member.wallet.deposit(wager * 1.5)
                dollars, cents = stats.convert_to_dollars(wager * 1.5)
                await ctx.send(f"**Blackjack!** You won `${dollars:,}.{cents:02d}`")
            elif player_best > dealer_best:
                player.member.wallet.deposit(wager)
                dollars, cents = stats.convert_to_dollars(wager)
                await ctx.send(f"**You beat the dealer!** You won `${dollars:,}.{cents:02d}`")
            else:
                player.member.wallet.withdraw(wager)
                dollars, cents = stats.convert_to_dollars(wager)
                await ctx.send(f"**Dealer beat you!** You lost `${dollars:,}.{cents:02d}`")
    else:
        player.member.wallet.withdraw(wager * 0.5)
        dollars, cents = stats.convert_to_dollars(wager * 0.5)
        ctx.send(f"**Surrendered!** You lost `${dollars:,}.{cents:02d}`")


def blackjack_embed(dealer_hand: list, player_hand: list) -> discord.Embed:
    embed = discord.Embed(title= "Blackjack",
                                    color = discord.Colour.from_rgb(255,255,255))
    embed.set_thumbnail(url = "https://www.nicepng.com/png/detail/154-1547506_blackjack-comments-black-jack-icon.png")
    embed.add_field(name = "Dealer", value = hand_to_emoji(dealer_hand))
    embed.add_field(name = "Your hand", value = hand_to_emoji(player_hand), inline = False)
    return embed


def handle_button_info(button_info: str, player: BlackjackPlayer, dealer: Dealer, wager: float) -> (bool | str):
    if button_info == "hit":
        dealer.deal(dealer.deck, player)
        return not player.check_playing()
    elif button_info == "stand":
        return True
    elif button_info == "double":
        dealer.deal(dealer.deck, player)
        return True
    else:
        return False


class BlackjackGame:
    def __init__(self, dealer: Dealer, player: BlackjackPlayer, ctx: commands.Context, wager: float = 50):
        self.dealer = dealer
        self.player = player
        self.ctx = ctx
        self.wager = wager

    
    def start_game(self):
        self.dealer.deck.shuffle() 
        self.player.playing = True
        for _ in range(INITIAL_CARD_NUMBER):
            self.dealer.deal(self.dealer.deck, self.player)
            self.dealer.deal(self.dealer.deck, self.dealer)

    async def play_game(self):
        author = self.ctx.author
        self.start_game()
        await self.ctx.send("Now playing: **blackjack**!")
        start_embed = blackjack_embed([None, self.dealer.hand[1]], self.player.hand)
        game_message = await self.ctx.send(embed = start_embed)

        while self.player.playing:
            double = len(self.player.hand) == 2 and self.player.member.wallet.money >= self.wager * 2
            menu = BlackjackButtons(double, author, timeout = 300)
            menu_message = await self.ctx.send(view = menu)
            await menu.wait()

            if menu.button_info == "surrender":
                await handle_winner(self.player, None, self.wager, self.ctx)
                self.player.playing = False

            else:
                end = handle_button_info(menu.button_info,
                                         self.player, self.dealer, self.wager)
                deal_hand = [None, self.dealer.hand[1]]

                if menu.button_info == "double":
                    self.wager *= 2

                if end:
                    dealer_values = self.dealer.end_game()

                    await handle_winner(self.player, dealer_values, self.wager, self.ctx)
                    self.player.playing = False
                    deal_hand = self.dealer.hand

                embed = blackjack_embed(deal_hand, self.player.hand)
                await game_message.edit(embed = embed)
    
            await menu_message.delete()


class BlackjackButtons(discord.ui.View):
    def __init__(self, double: bool, author, timeout: float = None):
        super().__init__(timeout = timeout)
        self.author = author
        self.can_double = double

    button_info : str = None

    def on_timeout(self):
        self.button_info = "timeout"

    async def check_presser(self, interaction: discord.Interaction):
        if interaction.user == self.author:
            return True
        else:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return False



    @discord.ui.button(label = "Hit", style = discord.ButtonStyle.blurple, custom_id = "hit", emoji = "✅")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        allow = await self.check_presser(interaction)
        if allow:
            self.button_info = "hit"
            await interaction.response.defer()
            self.stop()


    @discord.ui.button(label="Stand", style = discord.ButtonStyle.gray, custom_id = "stand", emoji = "🛑")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        allow = await self.check_presser(interaction)
        if allow:
            self.button_info = "stand"
            await interaction.response.defer()
            self.stop()


    @discord.ui.button(label="Double", style = discord.ButtonStyle.green, custom_id = "double", emoji="💰")
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        allow = await self.check_presser(interaction)
        if allow:
            if self.can_double:
                self.button_info = "double"
                await interaction.response.defer()
                self.stop()
            else:
                button.disabled = True
                await interaction.response.send_message("Can't double down: insufficient funds or too many cards!",
                                                    ephemeral=True)


    @discord.ui.button(label="Surrender", style = discord.ButtonStyle.red, custom_id = "surrender", emoji= "🏳️")
    async def surrender(self, interaction: discord.Interaction, button: discord.ui.Button):
        allow = await self.check_presser(interaction)
        if allow:
            self.button_info = "surrender"
            await interaction.response.defer()
            self.stop()


    # def insurance(self):
    #     #can bet up to half original wager as insurance if dealer's upcard is ace
    #     ...

    # def split(self):
    #     #if both cards same value, can start 2 games
    #     #can split up to 3 times, making 4 games
    #     #must match original bet for each extra game
    #     #if split aces, can only get 1 additional card (unless that card is an ace, then can split again)
    #     ...

if __name__ == "__main__":
    card1 = Card("clubs", 'Q')
    card2 = Card("hearts", 'K')
    hand = [card1, card2]
    deck = Deck(dict_to_cards(STANDARD_CARDS))
    dealer = Dealer(deck, [card1, card2])
    print(hand_value(hand))