import settings
import discord
from discord.ext import commands
from cogs.greetings import Greetings
from discord import app_commands
import requests
import typing


def is_owner():
    async def predicate(ctx):
        if ctx.author.id != ctx.guild.owner_id:
            raise NotOwner("Hey you are not the owner")
        return True
    return commands.check(predicate)


class NotOwner(commands.CheckFailure):
    ...


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)


    @bot.event
    async def on_ready():
        print(f"User: {bot.user} (ID: {bot.user.id})")

        # for cmd_file in settings.CMDS_DIR.glob("*.py"):
        #     if cmd_file.name != "__init__.py":
        #         await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")

        for cog_file in settings.COGS_DIR.glob("*.py"):
            if cog_file.name != "__init__.py":
                await bot.load_extension(f"cogs.{cog_file.name[:-3]}")

        bot.tree.copy_global_to(guild=settings.GUILDS_ID)
        await bot.tree.sync(guild=settings.GUILDS_ID)


    # @bot.event
    # async def on_command_error(ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #          await ctx.send("Missing command argument!")
    
    
    @bot.command(hidden = True)
    @is_owner()
    async def reload(ctx, cog : str):
        try:
            await bot.reload_extension(f"cogs.{cog.lower()}")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send("Invalid extension name.")
        else:
            await ctx.send(f"{cog.title()} has been succesfully reloaded!")


    @bot.command(hidden = True)
    @is_owner()
    async def load(ctx, cog : str):
        try:
            await bot.load_extension(f"cogs.{cog.lower()}")
        except commands.errors.ExtensionNotFound:
            await ctx.send("Invalid extension name.")
        else:
            await ctx.send(f"{cog.title()} has been succesfully loaded!")


    @bot.command(hidden = True)
    @is_owner()
    async def unload(ctx, cog : str):
        try:
            await bot.unload_extension(f"cogs.{cog.lower()}")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send("Invalid extension name.")
        else:
            await ctx.send(f"{cog.title()} has been succesfully unloaded!")


    bot.run(settings.TOKEN)


if __name__ == "__main__":
    run()