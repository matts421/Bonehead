import discord
from discord.ext import commands
import settings
import wavelink

PASSWORD = settings.MUSIC_BOT_PASSWORD

class Menu(discord.ui.View):
    def __init__(self, music, timeout):
        super().__init__(timeout = timeout)
        self.music = music
        self.looping = False


    async def disable_all_items(self, interaction: discord.Interaction | discord.Message):
        for item in self.children:
            item.disabled = True

        if isinstance(interaction, discord.Interaction):
            await interaction.response.edit_message(view=self)
        else:
            await interaction.edit(view=self)

    
    def check_in_channel(self, interaction: discord.Interaction):
        if interaction.user.voice:
            return interaction.user.voice.channel == self.music.vc.channel
        else:
            return False

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.blurple, custom_id="prev", row=0)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            history = self.music.vc.queue.history

            if len(history) < 2:
                prev_track = history.pop()
                self.music.vc.queue.put_at_front(prev_track)
            else:
                current_track = history.pop()
                prev_track = history.pop()
                self.music.vc.queue.put_at_front(current_track)
                self.music.vc.queue.put_at_front(prev_track)


            await self.music.skip(interaction)
            try:
                await interaction.response.edit_message(view=self)
            except discord.errors.NotFound:
                pass
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)    


    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.blurple, custom_id="pause", row = 0)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            button.disabled = True
            button2 = [x for x in self.children if x.custom_id == "resume"][0]
            button2.disabled = False

            if self.music.vc:
                await self.music.vc.pause()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple, custom_id="resume", row = 0)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            button.disabled = True
            button2 = [x for x in self.children if x.custom_id == "pause"][0]
            button2.disabled = False
            
            if self.music.vc:
                await self.music.vc.resume()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)

    
    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.blurple, custom_id="skip", row = 0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            if self.music.vc:
                await self.music.vc.stop()
            
            try:
                await interaction.response.edit_message(view=self)
            except discord.errors.NotFound:
                pass

        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)


    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.blurple, custom_id="stop", row = 1)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            if self.music.vc:
                await self.music.stop(interaction)
            await self.disable_all_items(interaction)
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)

    
    @discord.ui.button(label="🔂", style=discord.ButtonStyle.blurple, custom_id="loop", row = 1)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            if self.music.vc:
                if self.looping:
                    self.music.vc.queue.loop = False
                    self.looping = False
                    button.style = discord.ButtonStyle.blurple
                else:
                    self.music.vc.queue.loop = True
                    self.looping = True
                    button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(view = self)
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)


    @discord.ui.button(label="🔀", style=discord.ButtonStyle.blurple, custom_id="shuffle", row = 1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.check_in_channel(interaction):
            if self.music.vc:
                self.music.vc.queue.shuffle()
                await interaction.response.defer()
        else:
            await interaction.response.send_message("You must be in the voice channel!", ephemeral = True)
    

def ms_to_mins(ms):
    seconds = ms / 1000
    mins = round(seconds / 60)
    remain_seconds = round(seconds % 60)
    return f"{mins}:{remain_seconds:02d}"


class Music(commands.Cog):
    vc : wavelink.Player = None
    current_track = None
    music_channel = None
    menu : Menu = None
    message = None


    def __init__(self, bot):
        self.bot = bot

    async def setup_hook(self):
        node: wavelink.Node = wavelink.Node(
            uri="http://localhost:2333",
            password=PASSWORD
        )
        await wavelink.NodePool.connect(client = self.bot, nodes = [node])


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node} is ready")


    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackEventPayload):
        if self.vc:
            if not self.menu or not self.menu.looping:
                self.menu = Menu(music = self, timeout=None)
                thumbnail = await payload.player.current.fetch_thumbnail()
                duration = ms_to_mins(payload.player.current.duration)
                embed = discord.Embed(color=discord.Colour.blue(),
                                    description=f"{payload.player.current.title} \n `{duration}`",
                                    title = "Now playing")
                embed.add_field(name = "Artist", value = payload.player.current.author)
                embed.set_image(url = thumbnail)
                await self.music_channel.send(embed = embed)
                self.message = await self.music_channel.send(view=self.menu)


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        try:
            loop = self.menu.looping
        except AttributeError:
            return
        
        if not loop:
            try:
                await self.message.delete()
            except discord.errors.NotFound:
                pass

        try:
            next_song = payload.player.queue.get()
        except wavelink.QueueEmpty:
            await self.stop(self.message)
        else:
            await payload.player.play(next_song)


    @commands.command()
    async def play(self, ctx, *title: str):
        if not self.vc:
            try:
                channel = ctx.message.author.voice.channel
            except AttributeError:
                await ctx.send("You must be in a voice channel to use the music bot!")
                return
            else:
                self.music_channel = ctx.message.channel
                self.vc = await channel.connect(cls=wavelink.Player, self_deaf = True, self_mute = True)
                await ctx.send(f"Joined {channel.name}")

        tracks = await wavelink.YouTubeTrack.search(" ".join(title))
        chosen_track = tracks[0]
        self.vc.queue.put(chosen_track)

        thumbnail = await chosen_track.fetch_thumbnail()

        if self.vc.current:
            embed = discord.Embed(description=f"{chosen_track.title}",
                                  title = f"Queued - `{self.vc.queue.find_position(chosen_track) + 1}`",
                                  color=discord.Colour.orange())
            embed.set_thumbnail(url = thumbnail)
            embed.add_field(name = "Queue", value = "\n", inline = False)
            
            for i in range(len(self.vc.queue)):
                if i == 5:
                    break
                else:
                    embed.add_field(name = "", value = f"`{i + 1}`: {self.vc.queue[i]}", inline = False)
            await ctx.send(embed = embed)
        else:
            self.current_track = self.vc.queue.get()
            await self.vc.play(self.current_track)
            
            
    @commands.command(hidden = True)
    async def stop(self, ctx):
        if self.vc:
            await self.vc.stop()
            self.vc.queue.clear()
            await self.vc.disconnect()
            self.vc = None


    @commands.command(hidden = True)
    async def skip(self, ctx):
        if self.vc:
            await self.vc.stop()
            

    @commands.command()
    async def queue(self, ctx):
        if self.vc:
            await ctx.send(str(self.vc.queue))


    @commands.command(hidden = True)
    async def resume(self, ctx):
        if self.vc:
            await self.vc.resume()


    @commands.command(hidden = True)
    async def pause(self, ctx):
        if self.vc:
            await self.vc.pause()


async def setup(bot):
    music_bot = Music(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup_hook()
