# Discord Bot - RISK
this project is a discord bot to play Risk - The Boardgame

# setup
You can run `main.py` to initiate the program. When it runs for the first time it will ask for your discord-bot token, then it saves it into a `.env` file. The next time you run the program will automatically get the token from here.

At this moment, when the `models.py` file gets updates (e.g. with a new column), you will have to delete your own database (`database.db`) and re-run `main.py` to generate the new version.

your bot will need the following permissions:

- `Manage Roles`
- `Manage Channels`
- `Manage Threads`
- `Send Messages`
- `Send Messages in Threads`
- `Create Private Threads`
- `Embed Links`
- `Attach Files`

The permissions integer is `361045739536`


