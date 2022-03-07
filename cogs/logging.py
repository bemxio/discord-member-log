from discord.ext import commands
from io import StringIO
import gspread, strings

from asyncio import TimeoutError
from discord import NotFound, File

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.account = gspread.service_account(filename="service_account.json")
        self.sheet = self.account.open_by_key(self.bot.config["SPREADSHEET_KEY"])
        self.worksheet = self.sheet.get_worksheet(0)
        
        self.offset = 2 # TODO: make it configurable in "config.toml"
    
    async def get_member_info(self, member):
        return [
            str(member.id), # user ID
            member.name + "#" + member.discriminator, # user tag
            member.display_name, # user nickname (guild nick if available)

            str(member.created_at), # user creation date
            str(member.joined_at), # user guild join date

            ", ".join(role.name for role in member.roles), # user roles
            "On server" # state on guild (left, banned etc.), on-server by default
        ]
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        cell = self.worksheet.find(str(member.id))

        if cell is None:
            return self.worksheet.append_row(await self.get_member_info(member))
        
        notation = f"A{cell.row}:G{cell.row}"
        self.worksheet.format(notation, {
            "backgroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0,
            }
        })
        self.worksheet.update_cell(cell.row, 7, "On server")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        cell = self.worksheet.find(str(member.id))
        notation = f"A{cell.row}:G{cell.row}"

        # checking state of member on guild
        try:
            await member.guild.fetch_ban(member)
        except NotFound:
            color = {"red": 0.6, "green": 0.6, "blue": 0.6}
            state = "Left"
        else:
            color = {"red": 0.7, "green": 0.0, "blue": 0.0}
            state = "Banned"
        
        self.worksheet.format(notation, {"backgroundColor": color})
        self.worksheet.update_cell(cell.row, 7, state)

    @commands.command()
    async def update(self, ctx):
        """
        Updates the worksheet with the member list of the guild.

        This command will overwrite all existing data on the spreadsheet.
        Any information about users who've left and/or got banned will be **deleted**.
        """
        
        if not any(role.id in self.bot.config["ALLOWED_ROLES"] for role in ctx.author.roles):
            return
        
        message = await ctx.send(strings.en.UPDATE_WARNING)
        await message.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅"

        try:
            await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except TimeoutError:
            return await message.edit(content=strings.en.UPDATE_REACTION_TIMEOUT)

        await message.edit(content=strings.en.UPDATE_WAITING)
        
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        data = [await self.get_member_info(member) for member in members]

        self.worksheet.update(f"A{self.offset}:G{len(data) + 1}", data)
        await message.edit(content=strings.en.UPDATE_DONE.format(ctx.author.mention, len(data)))

    @commands.command()
    async def download(self, ctx):
        """
        Generates a CSV (seperated by tabs) file with the member list of the guild.
        This will **not** fetch the data from the spreadsheet,
        so it will not contain data about users who've left and/or got banned.

        To export the member list from the spreadsheet, see the article below:
        https://www.solveyourtech.com/save-csv-google-sheets/
        """

        if not any(role.id in self.bot.config["ALLOWED_ROLES"] for role in ctx.author.roles):
            return
        
        await ctx.send(strings.en.DOWNLOAD_WAITING)
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)

        stream = StringIO("ID,Tag,Nickname,Creation Date,Join Date,Roles,State\n")

        for member in members:
            info = await self.get_member_info(member)
            stream.write("\t".join(info) + "\n")

        stream.seek(0)
        await ctx.send(
            strings.en.DOWNLOAD_DONE.format(len(members)), 
            file=File(fp=stream, filename="members.csv")
        )

def setup(bot):
    bot.add_cog(Logger(bot))