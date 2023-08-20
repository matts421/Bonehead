import discord
from discord.ext import commands
import stats
import settings
import json


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def stats(self, ctx):
        user = ctx.author
        position = stats.find_member(settings.MEMBERS_JSON_PATH, user.id)

        if position == -1:
            self.register(user)
            position = stats.find_member(settings.MEMBERS_JSON_PATH, user.id)
            await ctx.send("Successfully registered!")

        member_dict = stats.get_member(settings.MEMBERS_JSON_PATH, position)
        member = stats.dict_to_member(member_dict)
        await ctx.send(embed = member.embed())


    def register(self, user: discord.Member):
        new_member = stats.Member(user.nick,
                        user.id,
                        0,
                        0,
                        user.display_avatar.url,
                        discord.Colour.random().to_rgb(),
                        stats.Wallet())
        new_member = new_member.to_dictionary()
        stats.add_member(settings.MEMBERS_JSON_PATH, new_member)


    @commands.command(hidden = True)
    async def force_update(self, ctx, user_id: int):
        for user in ctx.guild.members:
            if user.id == user_id:
                position = stats.find_member(settings.MEMBERS_JSON_PATH, user_id)
                if position != -1:
                    member_dict = stats.get_member(settings.MEMBERS_JSON_PATH, position)
                    member = stats.Member(user.nick,
                                    user.id,
                                    member_dict['wins'],
                                    member_dict['losses'],
                                    user.display_avatar.url,
                                    discord.Colour.random().to_rgb(),
                                    stats.Wallet(member_dict['wallet']['money'])
                                    )
                    member = member.to_dictionary()
                    stats.update_member(settings.MEMBERS_JSON_PATH, member, position)
                    await ctx.send("Succesfully updated member!")
                    return
                else:
                    await ctx.send("This player has not yet been registered!")
                    return
        await ctx.send("A member with this id cannot be found!")

    
    @commands.command(aliases = ['lb'])
    async def leaderboard(self, ctx):
        with open(settings.MEMBERS_JSON_PATH, "r") as file:
            data = json.load(file)
            data.sort(key = lambda m: m['wallet']['money'], reverse=True)
            leaderboard = [{'nick': member['nick'], 'money': member['wallet']['money']} for member in data]
        embed = discord.Embed(title = "Leaderboard",
                              description="Top balances across the server",
                              color = discord.Colour.green())
        members = ""
        balances = ""
        for i in range(5):
            try:
                user = leaderboard[i]
            except IndexError:
                pass
            else:
                wallet = stats.Wallet(user['money'])
                members += f"{user['nick'].capitalize()}\n"
                balances += f"`{wallet}`\n"

        embed.add_field(name="Member", value = members)
        embed.add_field(name="Balance", value= balances)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))