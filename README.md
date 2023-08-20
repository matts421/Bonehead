# Bonehead Bot

![Bonehead Avatar](avatar.png)

_Avatar image created using [Craiyon](https://www.craiyon.com/)_

##

Bonehead Bot is a Discord bot built using the asynchronous [Discord.py](https://discordpy.readthedocs.io/en/stable/) library. Structured around the Cogs framework, Bonehead supports commands related to simple text-based games, music, information wikis, and a fully-fledged economy system.

## Functionality

All available commands are visible via typing `!help` in any channel that Bonehead has visibility to.

### _Games_

- **Hangman**
  - Stylized embed depiciting current game-state.
  - Console-logged "good-guess" suggestions with highest probability of being correct.
  - Currency is awarded or lost depending on the end-state of the game.
  - A dictionary definition of the word is provided via [Marriam-Webster](https://dictionaryapi.com/) at the end of the game.
- **Blackjack**
  - Stylized embed with custom buttons to progress game-state.
  - Blackjack pays 3 to 2.
- **Roulette**
  - Simple roulette game that allows betting with earned currency on black or red.
- **Riddle**
  - Pulls a riddle from a [riddle API]("https://riddles-api.vercel.app/random") and hides the answer behind a Discord spoiler.

### _Wikis_

- **Terraria**
  - Provides a stylized embed containing various Terraria wiki related links.
- **Calamity**
  - Provides a styled embed containing various Terraria Calamity Mod wiki related links.

### _Music_

- **Music Bot**
  - Powered by [lavalink](https://github.com/lavalink-devs/Lavalink), a fully funcitonal voice-channel music bot with button GUI.

### _Statistics & Economy_

- **Player Card**
  - Displays a player-card embed that depicts the amount of currency and win-loss ratio on Hangman.

- **Leaderboard**
  - Lists the top 5 players on the server by amount of currency.

## Dependencies

In order to run Bonehead Bot locally, you will need to complete the following steps:

1. Create a Discord account and create a new application on the [developer portal](https://discord.com/developers/applications). Bonehead requires administrator permissions. Bonehead also needs message content and members intents.
2. Configure Python and install all required dependencies in `requirements.txt`.
3. The music bot is built with [Wavelink](https://github.com/PythonistaGuild/Wavelink) (go give them a star on their repo), so follow the lavalink instructions laid out on their repo! The folder storing Lavalink contents should be titled `lavalink`.
4. Populate a `.env` file that contains the necessary API keys to run Bonehead. `settings.py` contains all of the correct variable names.
