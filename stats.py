from typing import Tuple
import json
import os
import discord


MEMBER_INDENT = 2


def convert_to_dollars(money: float) -> Tuple[int, float]:
        dollars: int = int(money // 1)
        cents: int = round((money - dollars) * 100)
        return dollars, cents


class Wallet:
    def __init__(self, money: float = 0):
        self.money = money


    def __str__(self) -> str:
        dollars, cents = convert_to_dollars(self.money)
        return f"${dollars:,}.{cents:02d}"


    def deposit(self, money: float = 0) -> None:
        self.money += money


    def withdraw(self, money: float = 0) -> None:
        self.money -= money


    def to_dictionary(self) -> dict:
        out = {
            'money': self.money
        }
        return out


    @property
    def money(self):
        return self._money
    
    @money.setter
    def money(self, money):
        if not isinstance(money, float) and not isinstance(money, int):
            raise TypeError("Money must be a positive number!")
        elif money < 0:
            raise ValueError("Money must be a positive number!")
        self._money = money


class Member:
    def __init__(self, nick: str, unique_id: int, wins, losses, avatar_url: str, colour: Tuple[int, int, int], wallet: Wallet):
        self.nick = nick
        self.unique_id = unique_id
        self.wins = wins
        self.losses = losses
        self.avatar_url = avatar_url
        self.colour = colour
        self.wallet = wallet


    def __str__(self) -> str:
        return f"{self.nick}: {self.wins} / {self.losses} | {self.wallet}"
    

    def win(self):
        self.wins += 1


    def lose(self):
        self.losses += 1


    def to_dictionary(self) -> dict:
        out = {
            'nick': self.nick,
            'unique_id': self.unique_id,
            'wins':  self.wins,
            'losses': self.losses,
            'avatar_url': self.avatar_url,
            'colour': self.colour,
            'wallet': self.wallet.to_dictionary()
        }
        return out
    

    def embed(self) -> discord.Embed:
        embed = discord.Embed(title = "Statistics",
                              description= f"Player card for `{self.nick.capitalize()}`",
                              color = discord.Colour.from_rgb(*self.colour)
                              )
        try:
            win_percent = round(self.wins * 100 / (self.wins + self.losses))
        except ZeroDivisionError:
            win_percent = 0
        embed.add_field(name = f"Hangman - `{win_percent}%`", value = f"W: `{self.wins}`\nL: `{self.losses}`")
        embed.add_field(name = "Wallet", value = f"`{self.wallet.__str__()}`", inline=False)
        embed.set_thumbnail(url = self.avatar_url)
        return embed
    

def add_member(json_name: str, new_member: dict) -> None:
    if os.path.exists(json_name):
        with open(json_name, "r+") as file:
            data = json.load(file)
            data.append(new_member)

            data.sort(key = lambda m: m['unique_id'])
            file.seek(0)
            json.dump(data, file, indent = MEMBER_INDENT)
            file.truncate()
    else:
        with open(json_name, 'w') as file:
            json.dump([new_member], file, indent = 2)
            file.truncate()


def update_member(json_name: str, member: dict, position: int = None) -> None:
    if not position:
        position = find_member(json_name, member['unique_id'])

    with open(json_name, "r+") as file:
        data = json.load(file)
        data[position] = member
        data.sort(key = lambda m: m['unique_id'])
        file.seek(0)
        json.dump(data, file, indent = MEMBER_INDENT)
        file.truncate()


def get_member(json_name: str, position: int) -> dict:
    with open(json_name, "r+") as file:
        data = json.load(file)

    return data[position]


def find_member(json_name: str, member_id: int) -> int:
    with open(json_name, "r") as file:
        member_list = json.load(file)
    
    max = len(member_list) - 1
    min = 0
    while min <= max:
        index = (max + min) // 2
        
        if member_list[index]['unique_id'] == member_id:
            return index
        elif member_list[index]['unique_id'] > member_id:
            max = index - 1
        else:
            min = index + 1

    return -1


def dict_to_member(member_dict: dict) -> Member:
    wallet = Wallet(**member_dict['wallet'])
    member_dict.pop('wallet')
    return Member(**member_dict, wallet = wallet)
