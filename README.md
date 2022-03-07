# discord-member-log
A simple Discord bot, that logs member join/leave events into a spreadsheet.
It also can export a CSV file with all current members on the server.

This was originally created for r/okbuddyhololive, but I've decided to publish it.

**NOTE: The bot is meant to run on a single server.**
Unless you want all of the members across servers to be logged into a single worksheet, 
it does not have multi-server support.

## Running
Make sure you have Python 3.8+ & Git installed.
You will also need an application on the [Discord Developer Portal](https://discord.com/developers/applications),
and a GCS Service Account (instructions on how to create it can be found [here](https://docs.gspread.org/en/v5.2.0/oauth2.html#for-bots-using-service-account)).

1. Clone this repository into your PC/VPS (using `git clone https://github.com/bemxio/discord-member-log`)
2. Install all requirements with `pip` (`pip install -r requirements.txt`)
3. Rename `example.toml` to `config.toml` and fill in all required fields
4. Copy the JSON file from GCS into the bot's directory, renaming it to `service_account.json`
5. Run the bot with `python bot.py` or `python3 bot.py`