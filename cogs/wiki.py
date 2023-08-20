import discord
from discord.ext import commands
import requests
import typing


class Wiki(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(brief = "Terraria wiki",
                      description = "Generates a summary of terraria-related wikis")
    async def terraria(self, ctx):
        embed = discord.Embed(
             colour = discord.Colour.green(),
             title = "Terraria"
             )
       
        embed.set_thumbnail(url = "https://terraria.wiki.gg/images/thumb/a/ac/Tree.png/25px-Tree.png")
        embed.set_image(url = "https://cdn.shopify.com/s/files/1/0500/1894/3142/t/40/assets/newpromologo.png?v=98044556741494641381686755815")

        embed.add_field(name="General", value="https://terraria.wiki.gg/wiki/Terraria_Wiki")
        embed.add_field(name="Weapons", value="https://terraria.wiki.gg/wiki/Weapons", inline=False)

        await ctx.send(embed=embed)

    @commands.command(brief = "Calamity wiki",
                      description = "Generates a summary of calamity-related wikis")
    async def calamity(self, ctx):
        embed = discord.Embed(
            colour = discord.Colour.red(),
            title = "Calamity"
        )

        embed.set_thumbnail(url = "https://static.wikia.nocookie.net/calamitymod_gamepedia_en/images/6/63/Calamity_Logo.png/revision/latest?cb=20220816075814&format=original")
        embed.set_image(url = "https://calamitymod.wiki.gg/images/e/e6/Site-logo.png")

        embed.add_field(name = "General", value = "https://calamitymod.wiki.gg/wiki/Calamity_Mod_Wiki")
        embed.add_field(name = "Weapons", value = "https://calamitymod.wiki.gg/wiki/Weapons", inline=False)
        embed.add_field(name = "Class guide", value = "https://calamitymod.wiki.gg/wiki/Guide:Class_setups", inline=False)

        await ctx.send(embed=embed)

        


async def setup(bot):
    await bot.add_cog(Wiki(bot))
