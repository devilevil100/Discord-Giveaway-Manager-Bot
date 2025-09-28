from discord.ext import commands
import asyncio
import discord
import pytz
import discord
from dateutil import parser
import json
import random
import datetime
from datetime import timedelta
import ast
from discord.utils import get
import pickle
from collections import defaultdict
import sqlite3
from discord import Option
f = open('config.json',)
colorforembed = discord.Colour.from_rgb(57, 54, 54)
# returns JSON object as
# a dictionary
config = json.load(f)
print(config['serverids'])
custom_invites = {}
with open('invites.json', 'r') as o:
	invite_uses = json.load(o)

conn = sqlite3.connect('giveaways.db')

c = conn.cursor()
def find_invite_by_code(invite_list, code):
	for inv in invite_list:
		if inv.code == code:
			return inv


c.execute("""CREATE TABLE IF NOT EXISTS giveaways(
                guildid BIGINT,
                multipliers TEXT,
                requirements TEXT,
                winners INTEGER,
                title TEXT,
                times BIGINT,
                createdat TEXT,
                description TEXT,
                image TEXT,
                winmsg TEXT,
                msgid BIGINT,
                id BIGINT)
                """)
conn.close()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

def time_format(seconds: int):
    if seconds is not None:
        seconds = int(seconds)
        d = seconds // (3600 * 24)
        h = seconds // 3600 % 24
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        if d > 0:
            return '{:02d}D {:02d}H {:02d}m {:02d}s'.format(d, h, m, s)
        elif h > 0:
            return '{:02d}H {:02d}m {:02d}s'.format(h, m, s)
        elif m > 0:
            return '{:02d}m {:02d}s'.format(m, s)
        elif s > 0:
            return '{:02d}s'.format(s)
@bot.event
async def on_ready():
    for guild in bot.guilds:
        try:
            custom_invites[str(guild.id)] = await guild.invites()
            if str(guild.id) not in invite_uses:
	               invite_uses[str(guild.id)] = []
	               with open('invites.json', 'w') as fp:
		                     json.dump(invite_uses, fp)
        except Exception:
            pass
    print("loggedin")



class Statusdropdown(discord.ui.Select):
    def __init__(self, master, multi=None):
        self.master = master
        self.multi = multi
        options = [
            discord.SelectOption(
                label="Online",  emoji="<:online:891236434747490305>"
            ),
            discord.SelectOption(
                label="Idle", emoji="<:idle:891236454607486998>"
            ),
            discord.SelectOption(
                label="DND", emoji="<:dnd:891236444205625414>"
            ),
            discord.SelectOption(
                label="Streaming", emoji="<:stream:891236480540880938>"
            ),
            discord.SelectOption(
                label="Offline", emoji="<:offline:891236469807657000>"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Select a requirement value",
            min_values=1,
            max_values=4,
            options=options,
        )


    async def callback(self, interaction: discord.Interaction):

        added = 0
        def checkint(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric()
            return inner_check
        if self.multi == None:
            for item in self.master.req:
                 if list(item.keys())[0] == "status":
                     item[list(item.keys())[0]] = self.values
                     added = 1
            if added != 1:
                self.master.req.append({"status": self.values})
                added = 0

        if self.multi == "yes":
            self.disabled = True
            embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val2:
                listtt = {str(tuple(self.values)):val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "status":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"status": [listtt]})
                    added = 0
                print(self.master.multi)
                self.master.remove_item(self)
        self.master.status = "done"
        self.master.remove_item(self)

class ActivityDropdown(discord.ui.Select):
    def __init__(self, master, multi=None):
        self.multi = multi
        self.master = master
        options = [
            discord.SelectOption(
                label="Lurker",  description="Anyone who has sent at least one message "
            ),
            discord.SelectOption(
                label="Inactive", description="In top 75% of messages sent"
            ),
            discord.SelectOption(
                label="Average", description="Average message sent"
            ),
            discord.SelectOption(
                label="Active", description="In top 25% of messages sent"
            ),
            discord.SelectOption(
                label="Hyperactive", description="Most messages in the server"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Select a requirement value",
            min_values=1,
            max_values=1,
            options=options,
        )


    async def callback(self, interaction: discord.Interaction):
        added = 0
        def checkint(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric()
            return inner_check
        if self.multi == None:
            for item in self.master.req:
                 if list(item.keys())[0] == "activity":
                     item[list(item.keys())[0]] = self.values[0]
                     added = 1
            if added != 1:
                self.master.req.append({"activity": self.values[0]})
                added = 0
            self.master.status = "done"
        else:
            self.disabled = True
            embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val2:
                listtt = {self.values[0]:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "activity":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"activity": [listtt]})
                    added = 0
                print(self.master.multi)
                self.master.remove_item(self)

        self.master.status = "done"
        self.master.remove_item(self)

#MULIPLIER DROPDOWN
class MultiDropdown(discord.ui.Select):
    def __init__(self, master):

        self.master = master
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Account Older", description="Must be a certain amount of days old"
            ),
            discord.SelectOption(
                label="Member Older", description="Must be a member for a certain amount of days"
            ),
            discord.SelectOption(
                label="Role", description="Must have the specified role"
            ),
            discord.SelectOption(
                label="Not Role", description="Must **not** have the specified role"
            ),
            discord.SelectOption(
                label="Messages", description="Must have sent the specified number of messages"
            ),
            discord.SelectOption(
                label="Tag", description="Must have the specified discriminator"
            ),
            discord.SelectOption(
                label="Voice Duration", description="Have been in VC for a certain amount of minutes"
            ),
            discord.SelectOption(
                label="Status", description="Must have the specified status(es)"
            ),
            discord.SelectOption(
                label="Bio", description="Must have this in their custom status"
            ),
            discord.SelectOption(
                label="Name", description="Must have this in their name"
            ),
            discord.SelectOption(
                label="Activity", description="Member must meet a specified activity threshold"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Select a requirement type",
            min_values=1,
            max_values=1,
            options=options,
        )


    async def callback(self, interaction: discord.Interaction):
        self.disabled = True

        def checkint(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric()
            return inner_check
        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check
        def checkinteract(author):
            def inner_check(message):
                return message.user == author
            return inner_check

        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        def checktag(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric() and len(message.content) == 4
            return inner_check
        if self.values[0] == "Account Older":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum account age for each entrant in days.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "acc":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"acc": [listtt]})
                    added = 0

        if self.values[0] == "Member Older":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum guild membership length for each entrant in days.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "mem":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"mem": [listtt]})
                    added = 0

        if self.values[0] == "Role":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please mention the role entrants must have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkrol(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "role":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"role": [listtt]})
                    added = 0
        if self.values[0] == "Not Role":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please mention the role entrants must **not** have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkrol(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "notrole":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"notrole": [listtt]})
                    added = 0
        if self.values[0] == "Messages":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum amount of messages each entrant must have sent.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "msgs":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"msgs": [listtt]})
                    added = 0
        if self.values[0] == "Tag":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the discriminator that entrants must have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checktag(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "tag":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"tag": [listtt]})
                    added = 0
        if self.values[0] == "Voice Duration":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum voice chat duration for each entrant in minutes", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "vc":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"vc": [listtt]})
                    added = 0
        if self.values[0] == "Status":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})`", color=colorforembed)
            self.master.add_item(Statusdropdown(self.master, "yes"))
            await interaction.response.edit_message(embed=embed, view=self.master)
            await bot.wait_for('interaction', check=checkinteract(self.master.context.author))
            await bot.wait_for('message', check=checkint(self.master.context.author))
        if self.values[0] == "Bio":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the substring that must be in each entrants' custom status.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=check(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "bio":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"bio": [listtt]})
                    added = 0
        if self.values[0] == "Name":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the substring that must be in each entrants' name or nickname.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=check(self.master.context.author))
            if val:
                embed = discord.Embed(title="Set multiplier value", description=f"Type how many extra entries the multiplier should reward.", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self.master)
                val2 = await bot.wait_for('message', check=checkint(self.master.context.author))
                if val2:
                    listtt = {val.content:val2.content}
                for item in self.master.multi:
                     if list(item.keys())[0] == "name":
                         item[list(item.keys())[0]].append(listtt)
                         added = 1
                if added != 1:
                    self.master.multi.append({"name": [listtt]})
                    added = 0
        if self.values[0] == "Activity":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})`", color=colorforembed)
            self.master.add_item(ActivityDropdown(self.master, "yes"))
            await interaction.response.edit_message(embed=embed, view=self.master)
            await bot.wait_for('interaction', check=checkinteract(self.master.context.author))
            await bot.wait_for('message', check=checkint(self.master.context.author))
        await asyncio.sleep(0.5)
        embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
        embed.add_field(name="Basic Settings", value=f"""
        <:stem:890923334240469014> **Title**: {self.master.title}
        <:stem:890923334240469014> **Description**: None
        <:stem:890923334240469014> **Length**: {time_format(self.master.length)}
        <:stem:890923334240469014> **Emoji**: 🥳
        <:stem:890923334240469014> **Winners**: 1

         """, inline=False)

        requirrrr = []
        multiii = []
        for item in self.master.req:
            if list(item.keys())[0] == "acc":
                val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
            if list(item.keys())[0] == "mem":
                val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = requirrrr.append(f"have the {ite} role.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = requirrrr.append(f"**not** have the {ite} role.")
            if list(item.keys())[0] == "msgs":
                val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
            if list(item.keys())[0] == "tag":
                val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
            if list(item.keys())[0] == "vc":
                val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
            if list(item.keys())[0] == "status":
                val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
            if list(item.keys())[0] == "bio":
                val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
            if list(item.keys())[0] == "name":
                val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
            if list(item.keys())[0] == "activity":
                val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
        if len(requirrrr) != 0:
            embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
        else:
            embed.add_field(name="Requirements", value=f"""
            `No requirements Yet`
             """, inline=False)
        for item in self.master.multi:
            if list(item.keys())[0] == "acc":
                for ite in item.get('acc'):
                    val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "mem":
                for ite in item.get('mem'):
                    val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "msgs":
                for ite in item.get('msgs'):
                    val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "tag":
                for ite in item.get('tag'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "vc":
                for ite in item.get('vc'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "status":
                for ite in item.get('status'):
                    val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
            if list(item.keys())[0] == "bio":
                for ite in item.get('bio'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "name":
                for ite in item.get('name'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "activity":
                for ite in item.get('activity'):
                    val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
        if len(multiii) != 0:
            embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
        else:
            embed.add_field(name="Multipliers", value=f"""
            `No Multipliers Yet`
             """, inline=False)
        for item in self.master.children:
            item.disabled = False
        self.master.remove_item(self)
        self.master.children[1].label = "Add Multi"
        self.master.children[1].emoji="<:add:890925692336893953>"
        self.master.children[1].style = discord.ButtonStyle.grey
        await interaction.edit_original_message(embed=embed, view=self.master)

#REQUIREMENT DROPDOWN
class Dropdown(discord.ui.Select):
    def __init__(self, master):

        self.master = master
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Account Older", description="Must be a certain amount of days old"
            ),
            discord.SelectOption(
                label="Member Older", description="Must be a member for a certain amount of days"
            ),
            discord.SelectOption(
                label="Role", description="Must have the specified role"
            ),
            discord.SelectOption(
                label="Not Role", description="Must **not** have the specified role"
            ),
            discord.SelectOption(
                label="Messages", description="Must have sent the specified number of messages"
            ),
            discord.SelectOption(
                label="Tag", description="Must have the specified discriminator"
            ),
            discord.SelectOption(
                label="Voice Duration", description="Have been in VC for a certain amount of minutes"
            ),
            discord.SelectOption(
                label="Status", description="Must have the specified status(es)"
            ),
            discord.SelectOption(
                label="Bio", description="Must have this in their custom status"
            ),
            discord.SelectOption(
                label="Name", description="Must have this in their name"
            ),
            discord.SelectOption(
                label="Activity", description="Member must meet a specified activity threshold"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Select a requirement type",
            min_values=1,
            max_values=1,
            options=options,
        )


    async def callback(self, interaction: discord.Interaction):
        self.disabled = True

        def checkint(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric()
            return inner_check
        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check
        def checkinteract(author):
            def inner_check(message):
                return message.user == author
            return inner_check
        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        def checktag(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric() and len(message.content) == 4
            return inner_check
        if self.values[0] == "Account Older":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum account age for each entrant in days.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "acc":
                         item[list(item.keys())[0]] = int(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"acc": int(val.content)})
                    added = 0

        if self.values[0] == "Member Older":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum guild membership length for each entrant in days.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "mem":
                         item[list(item.keys())[0]] = int(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"mem": int(val.content)})
                    added = 0

        if self.values[0] == "Role":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please mention the role entrants must have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkrol(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "role":
                         item[list(item.keys())[0]].append(str(val.content))
                         added = 1
                if added != 1:
                    self.master.req.append({"role": [str(val.content)]})
                    print(self.master.req)
                    added = 0
        if self.values[0] == "Not Role":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please mention the role entrants must **not** have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkrol(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "notrole":
                         item[list(item.keys())[0]].append(str(val.content))
                         added = 1
                if added != 1:
                    self.master.req.append({"notrole": [str(val.content)]})
                    print(self.master.req)
                    added = 0
        if self.values[0] == "Messages":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum amount of messages each entrant must have sent.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "msgs":
                         item[list(item.keys())[0]] = int(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"msgs": int(val.content)})
                    print(self.master.req)
                    added = 0
        if self.values[0] == "Tag":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the discriminator that entrants must have.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checktag(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "tag":
                         item[list(item.keys())[0]] = str(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"tag": str(val.content)})
                    print(self.master.req)
                    added = 0
        if self.values[0] == "Voice Duration":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the minimum voice chat duration for each entrant in minutes", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=checkint(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "vc":
                         item[list(item.keys())[0]] = int(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"vc": int(val.content)})
                    print(self.master.req)
                    added = 0
        if self.values[0] == "Status":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})`")
            self.master.add_item(Statusdropdown(self.master))
            await interaction.response.edit_message(embed=embed, view=self.master)
            await bot.wait_for('interaction', check=checkinteract(self.master.context.author))
        if self.values[0] == "Bio":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the substring that must be in each entrants' custom status.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=check(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "bio":
                         item[list(item.keys())[0]] = str(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"bio": str(val.content)})

                    added = 0
        if self.values[0] == "Name":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})` \n Please type the substring that must be in each entrants' name or nickname.", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self.master)
            val = await bot.wait_for('message', check=check(self.master.context.author))
            if val:
                for item in self.master.req:
                     if list(item.keys())[0] == "name":
                         item[list(item.keys())[0]] = str(val.content)
                         added = 1
                if added != 1:
                    self.master.req.append({"name": str(val.content)})

                    added = 0
        if self.values[0] == "Activity":
            added = 0
            embed = discord.Embed(title="Set requirement value", description=f"Set the value for the requirement `({self.values[0]})`", color=colorforembed)
            self.master.add_item(ActivityDropdown(self.master))
            await interaction.response.edit_message(embed=embed, view=self.master)
            await bot.wait_for('interaction', check=checkinteract(self.master.context.author))

        embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
        embed.add_field(name="Basic Settings", value=f"""
        <:stem:890923334240469014> **Title**: {self.master.title}
        <:stem:890923334240469014> **Description**: None
        <:stem:890923334240469014> **Length**: {time_format(self.master.length)}
        <:stem:890923334240469014> **Emoji**: 🥳
        <:stem:890923334240469014> **Winners**: 1

         """, inline=False)

        requirrrr = []
        multiii = []
        for item in self.master.req:
            if list(item.keys())[0] == "acc":
                val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
            if list(item.keys())[0] == "mem":
                val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = requirrrr.append(f"have the {ite} role.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = requirrrr.append(f"**not** have the {ite} role.")
            if list(item.keys())[0] == "msgs":
                val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
            if list(item.keys())[0] == "tag":
                val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
            if list(item.keys())[0] == "vc":
                val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
            if list(item.keys())[0] == "status":
                val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
            if list(item.keys())[0] == "bio":
                val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
            if list(item.keys())[0] == "name":
                val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
            if list(item.keys())[0] == "activity":
                val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
        if len(requirrrr) != 0:
            embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
        else:
            embed.add_field(name="Requirements", value=f"""
            `No requirements Yet`
             """, inline=False)
        for item in self.master.multi:
            if list(item.keys())[0] == "acc":
                for ite in item.get('acc'):
                    val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "mem":
                for ite in item.get('mem'):
                    val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "msgs":
                for ite in item.get('msgs'):
                    val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "tag":
                for ite in item.get('tag'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "vc":
                for ite in item.get('vc'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "status":
                for ite in item.get('status'):
                    val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
            if list(item.keys())[0] == "bio":
                for ite in item.get('bio'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "name":
                for ite in item.get('name'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "activity":
                for ite in item.get('activity'):
                    val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
        if len(multiii) != 0:
            embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
        else:
            if not self.master.drop:
                embed.add_field(name="Multipliers", value=f"""
                `No Multipliers Yet`
                 """, inline=False)
        for item in self.master.children:
            item.disabled = False
        self.master.remove_item(self)
        self.master.children[0].label = "Add Req"
        self.master.children[0].emoji="<:add:890925692336893953>"
        self.master.children[0].style = discord.ButtonStyle.grey
        await interaction.edit_original_message(embed=embed, view=self.master)

class Logs(discord.ui.View):
    def __init__(self,ctx, id, msgid):
        self.msgid = msgid
        self.context = ctx
        self.channelid = id

        super().__init__()
    @discord.ui.select(placeholder="Select a requirement value",
    min_values=1,
    max_values=7,
    options = [
        discord.SelectOption(
            label="User Invite",  description="When a member was invited"
        ),
        discord.SelectOption(
            label="User Leave", description="When a member leaves"
        ),
        discord.SelectOption(
            label="Giveaway Start", description="When a giveaway has started"
        ),
        discord.SelectOption(
            label="Giveaway Edit", description="When a giveaway has been edited"
        ),
        discord.SelectOption(
            label="Giveaway End", description="When a giveaway has ended"
        ),
        discord.SelectOption(
            label="Giveaway Reroll", description="When a giveaway is rerolled"
        ),
        discord.SelectOption(
            label="Drop Send", description="When a drop is sent"
        ),
    ]
)
    async def select_callback(self, select, interaction):
        with open("config.json", "r+") as f:
            config2 = json.load(f)
            for value in select.values:
                if value == "User Invite":
                    config2["logs"]["invite"] = self.channelid
                if value == "User Leave":
                    config2["logs"]["leave"] = self.channelid
                if value == "Giveaway Start":
                    config2["logs"]["gstart"] = self.channelid
                if value == "Giveaway Edit":
                    config2["logs"]["gedit"] = self.channelid
                if value == "Giveaway End":
                    config2["logs"]["gend"] = self.channelid
                if value == "Giveaway Reroll":
                    config2["logs"]["groll"] = self.channelid
                if value == "Drop Send":
                    config2["logs"]["drop"] = self.channelid
            f.seek(0)
            json.dump(config2, f, indent=4)
        self.remove_item(select)
        msgg = bot.get_channel(int(self.msgid))
        messages = await msgg.history(limit=100).flatten()
        for msg in messages:
            if msg.embeds:
                if msg.embeds[0].title == "Add Channel Log":
                    await msg.delete()
                    break
        await interaction.response.send_message(f'The Log channels have been updated', ephemeral=True)
        embed = discord.Embed(title="Channel Logs", color=colorforembed)
        if config2["logs"]["invite"] != "none":
            embed.add_field(name="User Invite Log", value="<#"+str(config2["logs"]["invite"])+">")
        if config2["logs"]["leave"] != "none":
            embed.add_field(name="User Leave Log", value="<#"+str(config2["logs"]["leave"])+">")
        if config2["logs"]["gstart"] != "none":
            embed.add_field(name="Giveaway Start Log", value="<#"+str(config2["logs"]["gstart"])+">")
        if config2["logs"]["gedit"] != "none":
            embed.add_field(name="Giveaway Edit Log", value="<#"+str(config2["logs"]["gedit"])+">")
        if config2["logs"]["gend"] != "none":
            embed.add_field(name="Giveaway End Log", value="<#"+str(config2["logs"]["gend"])+">")
        if config2["logs"]["groll"] != "none":
            embed.add_field(name="Giveaway Roll Log", value="<#"+str(config2["logs"]["groll"])+">")
        if config2["logs"]["drop"] != "none":
            embed.add_field(name="Drop Send Log", value="<#"+str(config2["logs"]["drop"])+">")
        await interaction.edit_original_message(embed=embed, view=self)
        self.stop()
class Servers(discord.ui.View):
    def __init__(self, ctx):

        self.context = ctx
        super().__init__()

    @discord.ui.button(label="Add Role", style=discord.ButtonStyle.grey, emoji="<:add:890925692336893953>", row=1)
    async def addrole(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the role", description="Mention the role you want to add in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkrol(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                roletoadd = int(val.content.replace("<@&","").replace(">",""))
                if roletoadd not in config2["roles"]:
                    config2['roles'].append(roletoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Add Role"
                button.emoji="<:add:890925692336893953>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)



        else:
            button.label = "Add Role"
            button.emoji="<:add:890925692336893953>"
            button.style=discord.ButtonStyle.grey

    @discord.ui.button(label="Blacklist Channel", style=discord.ButtonStyle.grey, emoji="<:add:890925692336893953>", row=1)
    async def addchannel(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkchannel(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<#")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the channel", description="Mention the channel you want to add in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkchannel(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channeltoadd = int(val.content.replace("<#","").replace(">",""))
                if channeltoadd not in config2["blacklistchannels"]:
                    config2['blacklistchannels'].append(channeltoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Blacklist Channel"
                button.emoji="<:add:890925692336893953>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)


        else:
            button.label = "Blacklist Channel"
            button.emoji="<:add:890925692336893953>"
            button.style=discord.ButtonStyle.grey

    @discord.ui.button(label="Blacklist Role", style=discord.ButtonStyle.grey, emoji="<:add:890925692336893953>", row=2)
    async def blacklistrole(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the role", description="Mention the role you want to blacklist in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkrol(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                roletoadd = int(val.content.replace("<@&","").replace(">",""))
                if roletoadd not in config2["blacklistroles"]:
                    config2['blacklistroles'].append(roletoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Blacklist Role"
                button.emoji="<:add:890925692336893953>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)



        else:
            button.label = "Blacklist Role"
            button.emoji="<:add:890925692336893953>"
            button.style=discord.ButtonStyle.grey

    @discord.ui.button(label="Remove Role", style=discord.ButtonStyle.grey, emoji="<:remove:890925682127929354>", row=2)
    async def removerole(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the role", description="Mention the role you want to remove in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkrol(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                roletoadd = int(val.content.replace("<@&","").replace(">",""))
                if roletoadd in config2["roles"]:
                    config2['roles'].remove(roletoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Remove Role"
                button.emoji="<:remove:890925682127929354>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)



        else:
            button.label = "Remove Role"
            button.emoji="<:remove:890925682127929354>"
            button.style=discord.ButtonStyle.grey

    @discord.ui.button(label="Remove Blacklist Channel", style=discord.ButtonStyle.grey, emoji="<:remove:890925682127929354>", row=3)
    async def removechannel(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkchannel(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<#")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the channel", description="Mention the blacklisted channel you want to remove in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkchannel(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channeltoadd = int(val.content.replace("<#","").replace(">",""))
                if channeltoadd in config2["blacklistchannels"]:
                    config2['blacklistchannels'].remove(channeltoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Remove Blacklist Channel"
                button.emoji="<:remove:890925682127929354>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)


        else:
            button.label = "Remove Blacklist Channel"
            button.emoji="<:remove:890925682127929354>"
            button.style=discord.ButtonStyle.grey

    @discord.ui.button(label="Remove Blacklist Role", style=discord.ButtonStyle.grey, emoji="<:remove:890925682127929354>", row=3)
    async def removeblacklistrole(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkrol(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<@&")
            return inner_check
        if button.label != "Cancel":
            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Mention the role", description="Mention the blacklisted role you want to remove  in the configuration", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkrol(self.context.author))
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                roletoadd = int(val.content.replace("<@&","").replace(">",""))
                if roletoadd in config2["blacklistroles"]:
                    config2['blacklistroles'].remove(roletoadd)
                f.seek(0)
                json.dump(config2, f, indent=4)
            with open("config.json", "r+") as f:
                config2 = json.load(f)
                channels = []
                roles = []
                blacklistroles = []
                for role in config2["roles"]:
                    roles.append("<@&"+str(role)+">")
                for channel in config2["blacklistchannels"]:
                    channels.append("<#"+str(channel)+">")
                for role in config2["blacklistroles"]:
                    blacklistroles.append("<@&"+str(role)+">")
                if len(blacklistroles) == 0:
                    blacklistroles.append("None")
                if len(roles) == 0:
                    roles.append("None")
                if len(channels) == 0:
                    channels.append("None")
                embed = discord.Embed(title="Server Settings", description=f"""
                Roles who can user the bot:  {" ".join(roles)}
                Blacklisted Channels: {" ".join(channels)}
                Blacklisted Roles: {" ".join(blacklistroles)}
                """, color=colorforembed)
                button.label = "Blacklist Role"
                button.emoji="<:remove:890925682127929354>"
                button.style=discord.ButtonStyle.grey
                for item in self.children:
                    item.disabled = False
                await interaction.edit_original_message(embed=embed, view=self)



        else:
            button.label = "Blacklist Role"
            button.emoji="<:remove:890925682127929354>"
            button.style=discord.ButtonStyle.grey

class Buttons(discord.ui.View):
    def __init__(self, ctx, title, length, multi=None, req=None, msgid = None, drop=None, channelid=None):

        self.status = "notdone"
        self.value = None
        self.context = ctx
        if req==None:
            self.req = []
        else:
            self.req = req
        if multi == None:
            self.multi= []
        else:
            self.multi = multi
        self.msgid = msgid
        self.title = title
        self.length = length
        self.drop = drop
        self.channelid = channelid
        super().__init__()
    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label="Add Req", style=discord.ButtonStyle.grey, emoji="<:add:890925692336893953>", row=1)
    async def addreq(self, button: discord.ui.Button, interaction: discord.Interaction):
        if button.label != "Cancel":

            for item in self.children:

                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            self.add_item(Dropdown(self))
            embed = discord.Embed(title="Add Requirements", description="Choose a requirement type", color=colorforembed)

            await interaction.response.edit_message(embed=embed, view=self)

        else:
            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)
            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)

                item.disabled = False

            button.label = "Add Req"
            button.emoji="<:add:890925692336893953>"
            button.style=discord.ButtonStyle.grey
            embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
            else:
                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)
            await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="Add Multi", style=discord.ButtonStyle.grey, emoji="<:add:890925692336893953>",row=1)
    async def addmulti(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.drop:
            self.remove_item(button)
            await interaction.response.edit_message(view=self)
            return
        if button.label != "Cancel":

            for item in self.children:
                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            self.add_item(MultiDropdown(self))
            embed = discord.Embed(title="Add Requirements", description="Choose a requirement type", color=colorforembed)

            await interaction.response.edit_message(embed=embed, view=self)

        else:
            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)

            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)
                item.disabled = False
            button.label = "Add Multi"
            button.emoji="<:add:890925692336893953>"
            button.style=discord.ButtonStyle.grey
            embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
            else:
                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)
            await interaction.response.edit_message(embed=embed, view=self)



    @discord.ui.button(label="Remove Req", style=discord.ButtonStyle.grey, emoji="<:remove:890925682127929354>",row=2)
    async def removereq(self, button: discord.ui.Button, interaction: discord.Interaction):
        def checkint(author, listt):
            def inner_check(message):
                return message.author == author and message.content.isnumeric() and int(message.content) <= len(listt)
            return inner_check
        if len(self.req) == 0:
            return
        if button.label != "Cancel":

            for item in self.children:
                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Remove Requirement", description="Type the number next to the item you would like to remove. ", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            newreq = []
            for index, value in enumerate(requirrrr, 1):
                itemm = "**"+str(index)+".** "+str(value)
                newreq.append(itemm)
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="\n".join(newreq), inline=False)
            else:
                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkint(self.context.author, requirrrr))
            if val:
                del self.req[int(val.content)-1]
                for item in self.children:
                    if item.type == discord.ComponentType.select:
                        self.remove_item(item)
                    item.disabled = False
                button.label = "Remove Req"
                button.emoji="<:remove:890925682127929354>"
                button.style=discord.ButtonStyle.grey
                embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
                embed.add_field(name="Basic Settings", value=f"""
                <:stem:890923334240469014> **Title**: {self.title}
                <:stem:890923334240469014> **Description**: None
                <:stem:890923334240469014> **Length**: {time_format(self.length)}
                <:stem:890923334240469014> **Emoji**: 🥳
                <:stem:890923334240469014> **Winners**: 1

                 """, inline=False)
                requirrrr = []
                multiii = []
                for item in self.req:
                    if list(item.keys())[0] == "acc":
                        val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                    if list(item.keys())[0] == "mem":
                        val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = requirrrr.append(f"have the {ite} role.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = requirrrr.append(f"**not** have the {ite} role.")
                    if list(item.keys())[0] == "msgs":
                        val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                    if list(item.keys())[0] == "tag":
                        val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                    if list(item.keys())[0] == "vc":
                        val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                    if list(item.keys())[0] == "status":
                        val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                    if list(item.keys())[0] == "bio":
                        val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                    if list(item.keys())[0] == "name":
                        val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                    if list(item.keys())[0] == "activity":
                        val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
                if len(requirrrr) != 0:
                    embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
                else:
                    embed.add_field(name="Requirements", value=f"""
                    `No requirements Yet`
                     """, inline=False)
                for item in self.multi:
                    if list(item.keys())[0] == "acc":
                        for ite in item.get('acc'):
                            val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "mem":
                        for ite in item.get('mem'):
                            val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "msgs":
                        for ite in item.get('msgs'):
                            val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "tag":
                        for ite in item.get('tag'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "vc":
                        for ite in item.get('vc'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "status":
                        for ite in item.get('status'):
                            val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                    if list(item.keys())[0] == "bio":
                        for ite in item.get('bio'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "name":
                        for ite in item.get('name'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "activity":
                        for ite in item.get('activity'):
                            val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
                if len(multiii) != 0:
                    embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
                else:
                    if not self.drop:
                        embed.add_field(name="Multipliers", value=f"""
                        `No Multipliers Yet`
                         """, inline=False)
                await interaction.edit_original_message(embed=embed, view=self)
        else:
            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)
                item.disabled = False
            button.label = "Remove Req"
            button.emoji="<:remove:890925682127929354>"
            button.style=discord.ButtonStyle.grey
            embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
            else:
                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)
            await interaction.response.edit_message(embed=embed, view=self)



    @discord.ui.button(label="Remove Multi", style=discord.ButtonStyle.grey, emoji="<:remove:890925682127929354>",row=2)
    async def removemulti(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.drop:
            self.remove_item(button)
            await interaction.response.edit_message(view=self)
            return
        def checkint(author, listt):
            def inner_check(message):
                return message.author == author and message.content.isnumeric() and int(message.content) <= len(listt)
            return inner_check
        if len(self.multi) == 0:
            return
        if button.label != "Cancel":

            for item in self.children:
                item.disabled = True
            button.disabled = False
            button.label = "Cancel"
            button.style=discord.ButtonStyle.red
            button.emoji = "🛑"
            embed = discord.Embed(title="Remove Multiplier", description="Type the number next to the item you would like to remove. ", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="\n".join(requirrrr), inline=False)
            else:
                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")

                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with role {list(ite.keys())[0]}  get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without role {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users with activity level ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            newmulti = []
            for index, value in enumerate(multiii, 1):
                itemm = "**"+str(index)+".** "+str(value)
                newmulti.append(itemm)
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="\n".join(newmulti), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
            val = await bot.wait_for('message', check=checkint(self.context.author, multiii))
            if val:
                target = newmulti[int(val.content)-1]
                if "Account" in target:
                    newtarg = target.replace("Account older than", "").replace("days get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "acc":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Members" in target:
                    newtarg = target.replace("Members older than", "").replace("days get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "mem":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Users with role" in target:
                    newtarg = target.replace("Users with role", "").replace("get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "role":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Users without role" in target:
                    newtarg = target.replace("Users without role", "").replace("get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "notrole":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Users with atleast" in target:
                    newtarg = target.replace("Users with atleast", "").replace("msgs", "").replace("get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "msgs":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "tag" in target:
                    newtarg = target.replace("Users with", "").replace("tag get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "tag":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "VC " in target:
                    newtarg = target.replace("Users with", "").replace("VC minutes get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "vc":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Users who are" in target:
                    newtarg = target.replace("Users who are", "").replace("get","").replace("entries", "").replace("or","").replace("``","").replace("+","").split()
                    statuses = []
                    for item in newtarg[:-2]:
                        if "*" in item or "." in item:
                            continue
                        statuses.append(item)
                    newtargdict = {str(tuple(statuses)): newtarg[-2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "status":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "custom status " in target:
                    newtarg = target.replace("Users with", "").replace("in custom status get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "bio":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "name" in target:
                    newtarg = target.replace("Users with", "").replace("in name get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "name":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                if "Users with activity level" in target:
                    newtarg = target.replace("Users with activity level", "").replace("get","").replace("entries", "").replace("``","").replace("+","").split()
                    newtargdict = {newtarg[1]: newtarg[2]}
                    print(newtargdict)
                    for item in self.multi:
                        if list(item.keys())[0] == "activity":
                            print(item.get(list(item.keys())[0]))
                            item.get(list(item.keys())[0]).remove(newtargdict)
                    print(self.multi)
                for item in self.children:
                    if item.type == discord.ComponentType.select:
                        self.remove_item(item)
                    item.disabled = False
                button.label = "Remove Multi"
                button.emoji="<:remove:890925682127929354>"
                button.style=discord.ButtonStyle.grey
                embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
                embed.add_field(name="Basic Settings", value=f"""
                <:stem:890923334240469014> **Title**: {self.title}
                <:stem:890923334240469014> **Description**: None
                <:stem:890923334240469014> **Length**: {time_format(self.length)}
                <:stem:890923334240469014> **Emoji**: 🥳
                <:stem:890923334240469014> **Winners**: 1

                 """, inline=False)
                requirrrr = []
                multiii = []
                for item in self.req:
                    if list(item.keys())[0] == "acc":
                        val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                    if list(item.keys())[0] == "mem":
                        val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = requirrrr.append(f"have the {ite} role.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = requirrrr.append(f"**not** have the {ite} role.")
                    if list(item.keys())[0] == "msgs":
                        val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                    if list(item.keys())[0] == "tag":
                        val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                    if list(item.keys())[0] == "vc":
                        val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                    if list(item.keys())[0] == "status":
                        val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                    if list(item.keys())[0] == "bio":
                        val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                    if list(item.keys())[0] == "name":
                        val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                    if list(item.keys())[0] == "activity":
                        val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
                if len(requirrrr) != 0:
                    embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
                else:
                    embed.add_field(name="Requirements", value=f"""
                    `No requirements Yet`
                     """, inline=False)
                for item in self.multi:
                    if list(item.keys())[0] == "acc":
                        for ite in item.get('acc'):
                            val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "mem":
                        for ite in item.get('mem'):
                            val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "msgs":
                        for ite in item.get('msgs'):
                            val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "tag":
                        for ite in item.get('tag'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "vc":
                        for ite in item.get('vc'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "status":
                        for ite in item.get('status'):
                            val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                    if list(item.keys())[0] == "bio":
                        for ite in item.get('bio'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "name":
                        for ite in item.get('name'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "activity":
                        for ite in item.get('activity'):
                            val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
                if len(multiii) != 0:
                    embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
                else:
                    if not self.drop:
                        embed.add_field(name="Multipliers", value=f"""
                        `No Multipliers Yet`
                         """, inline=False)
                await interaction.edit_original_message(embed=embed, view=self)
        else:
            for item in self.children:
                if item.type == discord.ComponentType.select:
                    self.remove_item(item)
                item.disabled = False
            button.label = "Remove Multi"
            button.emoji="<:remove:890925682127929354>"
            button.style=discord.ButtonStyle.grey
            embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
            embed.add_field(name="Basic Settings", value=f"""
            <:stem:890923334240469014> **Title**: {self.title}
            <:stem:890923334240469014> **Description**: None
            <:stem:890923334240469014> **Length**: {time_format(self.length)}
            <:stem:890923334240469014> **Emoji**: 🥳
            <:stem:890923334240469014> **Winners**: 1

             """, inline=False)
            requirrrr = []
            multiii = []
            for item in self.req:
                if list(item.keys())[0] == "acc":
                    val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                if list(item.keys())[0] == "mem":
                    val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = requirrrr.append(f"have the {ite} role.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = requirrrr.append(f"**not** have the {ite} role.")
                if list(item.keys())[0] == "msgs":
                    val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                if list(item.keys())[0] == "tag":
                    val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                if list(item.keys())[0] == "vc":
                    val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                if list(item.keys())[0] == "status":
                    val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                if list(item.keys())[0] == "bio":
                    val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                if list(item.keys())[0] == "name":
                    val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                if list(item.keys())[0] == "activity":
                    val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
            if len(requirrrr) != 0:
                embed.add_field(name="Requirements", value="• "+"\n • ".join(requirrrr), inline=False)
            else:

                embed.add_field(name="Requirements", value=f"""
                `No requirements Yet`
                 """, inline=False)
            for item in self.multi:
                if list(item.keys())[0] == "acc":
                    for ite in item.get('acc'):
                        val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "mem":
                    for ite in item.get('mem'):
                        val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "role":
                    for ite in item.get('role'):
                        val = multiii.append(f"Users with {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "notrole":
                    for ite in item.get('notrole'):
                        val = multiii.append(f"Users without {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "msgs":
                    for ite in item.get('msgs'):
                        val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "tag":
                    for ite in item.get('tag'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "vc":
                    for ite in item.get('vc'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "status":
                    for ite in item.get('status'):
                        val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                if list(item.keys())[0] == "bio":
                    for ite in item.get('bio'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "name":
                    for ite in item.get('name'):
                        val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                if list(item.keys())[0] == "activity":
                    for ite in item.get('activity'):
                        val = multiii.append("Users who are at least ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
            if len(multiii) != 0:
                embed.add_field(name="Multipliers", value="• "+"\n • ".join(multiii), inline=False)
            else:
                if not self.drop:
                    embed.add_field(name="Multipliers", value=f"""
                    `No Multipliers Yet`
                     """, inline=False)
            await interaction.response.edit_message(embed=embed, view=self)



    @discord.ui.button(label="Start", style=discord.ButtonStyle.grey, emoji="<:start:890926248262533131>", row=2)
    async def startgive(self, button: discord.ui.Button, interaction: discord.Interaction):
        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check
        def checkchannel(author):
            def inner_check(message):
                return message.author == author and message.content.startswith("<#")
            return inner_check
        def checkint(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric()
            return inner_check
        def checkinteract(author):
            def inner_check(message):
                return message.user == author
            return inner_check
        def checktag(author):
            def inner_check(message):
                return message.author == author and message.content.isnumeric() and len(message.content) == 4
            return inner_check
        def checkimg(author):
            def inner_check(message):
                if message.content.lower() != "none":
                    return message.author == author and message.content.startswith("https://")
                else:
                    return True
            return inner_check
        while len(self.children) > 0:
            for item in self.children:
                self.remove_item(item)

        if not self.drop:
            if not self.msgid:
                embed = discord.Embed(title="Channel", description=f"Please Mention the Channel for Giveaway", color=colorforembed)
                await interaction.response.edit_message(embed=embed, view=self)
                val = await bot.wait_for('message', check=checkchannel(self.context.author))
                print(val.content.replace("<#","").replace(">",""))
                embed = discord.Embed(title="Winners", description=f"How many winners can there be for this giveaway?", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val2 = await bot.wait_for('message', check=checkint(self.context.author))

                embed = discord.Embed(title="Description", description=f"Give more details about your giveaway. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val3 = await bot.wait_for('message', check=check(self.context.author))

                embed = discord.Embed(title="Win_Message", description=f"Send this private message to the winners. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val4 = await bot.wait_for('message', check=check(self.context.author))


                embed = discord.Embed(title="Image", description=f"Image link to display in the embed. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val5 = await bot.wait_for('message', check=checkimg(self.context.author))
                id = random.randint(10000,99999)
                embed = discord.Embed(title="Giveaway has started!", description=f"View all your giveaways with ``/list` \n Edit with ``/edit {id}`` ", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                ch = bot.get_channel(int(val.content.replace("<#","").replace(">","")))
                if val3.content.lower() != "none" :
                    emb = discord.Embed(title=self.title, description=val3.content, color=colorforembed)
                else:
                    emb = discord.Embed(title=self.title, color=colorforembed)
                if val5.content.lower() != "none":
                    emb.set_image(url=val5.content)
                added = 0
                requirrrr = []
                multiii = []
                for item in self.req:
                    if list(item.keys())[0] == "acc":
                        val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                    if list(item.keys())[0] == "mem":
                        val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = requirrrr.append(f"have the {ite} role.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = requirrrr.append(f"**not** have the {ite} role.")
                    if list(item.keys())[0] == "msgs":
                        val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                    if list(item.keys())[0] == "tag":
                        val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                    if list(item.keys())[0] == "vc":
                        val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                    if list(item.keys())[0] == "status":
                        val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                    if list(item.keys())[0] == "bio":
                        val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                    if list(item.keys())[0] == "name":
                        val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                    if list(item.keys())[0] == "activity":
                        val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
                if len(requirrrr) != 0:
                    emb.add_field(name="Requirements", value="\n".join(requirrrr), inline=False)
                else:
                    emb.add_field(name="Requirements", value=f"""
                    `No requirements Yet`
                     """, inline=False)
                for item in self.multi:
                    if list(item.keys())[0] == "acc":
                        for ite in item.get('acc'):
                            val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")

                    if list(item.keys())[0] == "mem":
                        for ite in item.get('mem'):
                            val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "role":
                        for ite in item.get('role'):
                            val = multiii.append(f"Users with role {list(ite.keys())[0]}  get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "notrole":
                        for ite in item.get('notrole'):
                            val = multiii.append(f"Users without role {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "msgs":
                        for ite in item.get('msgs'):
                            val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "tag":
                        for ite in item.get('tag'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "vc":
                        for ite in item.get('vc'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "status":
                        for ite in item.get('status'):
                            val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                    if list(item.keys())[0] == "bio":
                        for ite in item.get('bio'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "name":
                        for ite in item.get('name'):
                            val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                    if list(item.keys())[0] == "activity":
                        for ite in item.get('activity'):
                            val = multiii.append("Users with activity level ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
                newmulti = []
                for index, value in enumerate(multiii, 1):
                    itemm = "**"+str(index)+".** "+str(value)
                    newmulti.append(itemm)
                if len(multiii) != 0:
                    emb.add_field(name="Multipliers", value="\n".join(newmulti), inline=False)
                else:
                    if not self.drop:
                        emb.add_field(name="Multipliers", value=f"""
                        `No Multipliers Yet`
                         """, inline=False)
                emb.add_field(name="No. of Winners:", value=val2.content, inline=False)
                x = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(seconds=self.length)
                emb.add_field(name="Time:", value="<t:"+str(int(x.timestamp()))+":R>")
                msg = await ch.send(embed=emb)

                await msg.add_reaction("👍")
                self.value = [self.multi, self.req, val2.content,self.title, self.length, str(msg.created_at), val3.content, val5.content, val4.content, msg.id,  id]
                diccct = {str(self.context.guild.id): [self.value]}
                timelist = {id: self.length}
                timedictt = {str(self.context.guild.id): [timelist]}

                conn = sqlite3.connect('giveaways.db')
                c = conn.cursor()

                c.execute('INSERT INTO giveaways VALUES ({},"{}","{}",{},"{}",{},"{}","{}","{}","{}",{},{})'.format(self.context.guild.id,self.multi, self.req,int(val2.content), self.title, self.length, str(msg.created_at), val3.content, val5.content, val4.content, msg.id, id))
                conn.commit()

                while True:
                    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                    target = row.fetchone()
                    if target[5] > 0:
                        await asyncio.sleep(10)
                        c.execute('UPDATE giveaways SET times = {} WHERE guildid = {} and msgid = {}'.format(target[5]-10, self.context.guild.id, msg.id))
                        conn.commit()
                        if target[7].lower() != "none" :
                            emb = discord.Embed(title=target[4], description=target[7], color=colorforembed)
                        else:
                            emb = discord.Embed(title=target[4], color=colorforembed)
                        if target[8].lower() != "none":
                            emb.set_image(url=target[8])
                        added = 0
                        requirrrr = []
                        multiii = []
                        for item in ast.literal_eval(target[2]):
                            if list(item.keys())[0] == "acc":
                                val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
                            if list(item.keys())[0] == "mem":
                                val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
                            if list(item.keys())[0] == "role":
                                for ite in item.get('role'):
                                    val = requirrrr.append(f"have the {ite} role.")
                            if list(item.keys())[0] == "notrole":
                                for ite in item.get('notrole'):
                                    val = requirrrr.append(f"**not** have the {ite} role.")
                            if list(item.keys())[0] == "msgs":
                                val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
                            if list(item.keys())[0] == "tag":
                                val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
                            if list(item.keys())[0] == "vc":
                                val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
                            if list(item.keys())[0] == "status":
                                val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
                            if list(item.keys())[0] == "bio":
                                val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
                            if list(item.keys())[0] == "name":
                                val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
                            if list(item.keys())[0] == "activity":
                                val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
                        if len(requirrrr) != 0:
                            emb.add_field(name="Requirements", value="\n".join(requirrrr), inline=False)
                        else:

                            emb.add_field(name="Requirements", value=f"""
                            `No Requirements Yet`
                             """, inline=False)
                        for item in ast.literal_eval(target[1]):
                            if list(item.keys())[0] == "acc":
                                for ite in item.get('acc'):
                                    val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")

                            if list(item.keys())[0] == "mem":
                                for ite in item.get('mem'):
                                    val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "role":
                                for ite in item.get('role'):
                                    val = multiii.append(f"Users with role {list(ite.keys())[0]}  get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "notrole":
                                for ite in item.get('notrole'):
                                    val = multiii.append(f"Users without role {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "msgs":
                                for ite in item.get('msgs'):
                                    val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "tag":
                                for ite in item.get('tag'):
                                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "vc":
                                for ite in item.get('vc'):
                                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "status":
                                for ite in item.get('status'):
                                    val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
                            if list(item.keys())[0] == "bio":
                                for ite in item.get('bio'):
                                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "name":
                                for ite in item.get('name'):
                                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
                            if list(item.keys())[0] == "activity":
                                for ite in item.get('activity'):
                                    val = multiii.append("Users with activity level ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
                        newmulti = []
                        for index, value in enumerate(multiii, 1):
                            itemm = "**"+str(index)+".** "+str(value)
                            newmulti.append(itemm)
                        if len(multiii) != 0:
                            emb.add_field(name="Multipliers", value="\n".join(newmulti), inline=False)
                        else:
                            if not self.drop:
                                emb.add_field(name="Multipliers", value=f"""
                                `No Multipliers Yet`
                                 """, inline=False)
                        emb.add_field(name="No. of Winners:", value=str(target[3]), inline=False)
                        x = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(seconds=target[5]-10)
                        emb.add_field(name="Time:", value="<t:"+str(int(x.timestamp()))+":R>")
                        await msg.edit(embed=emb)
                    else:
                        break
                conn.close()



                msg = await self.context.channel.fetch_message(msg.id)
                wineeers = await msg.reactions[0].users().flatten()
                if bot.user in wineeers:
                    wineeers.remove(bot.user)
                totalwinner = []
                dqwinners = []
                print(wineeers)

                for user in wineeers:

                    conn = sqlite3.connect('giveaways.db')
                    c = conn.cursor()
                    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                    target = row.fetchone()
                    guild = self.context.guild
                    for it in ast.literal_eval(target[2]):
                        if list(it.keys())[0] == "acc":
                            accolder = it[list(it.keys())[0]]
                            timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.created_at.replace(tzinfo=pytz.UTC)
                            if timeee.days < accolder:
                                dqwinners.append(user)
                                continue
                        if list(it.keys())[0] == "mem":
                            memolder = it[list(it.keys())[0]]
                            timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.joined_at.replace(tzinfo=pytz.UTC)
                            if timeee.days < memolder:
                                dqwinners.append(user)
                                continue
                        if list(it.keys())[0] == "role":
                            role = it[list(it.keys())[0]]
                            for rol in role:
                                reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                                if reqrole not in user.roles:
                                    dqwinners.append(user)
                                    continue
                        if list(it.keys())[0] == "notrole":
                            notrole = it[list(it.keys())[0]]
                            for rol in notrole:
                                reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                                if reqrole in user.roles:
                                    dqwinners.append(user)
                                    continue
                        if list(it.keys())[0] == "msgs":
                            msgs = it[list(it.keys())[0]]
                            with open("messages.json", "r+") as f:
                                msg = json.load(f)
                                for item in msg:
                                    if list(item.keys())[0] == str(user.id):
                                        totalmsgs = item[list(item.keys())[0]]

                                try:
                                    if int(totalmsgs) < int(msgs):
                                        dqwinners.append(user)
                                        continue
                                except:
                                    dqwinners.append(user)
                                    continue
                        if list(it.keys())[0] == "tag":
                            tag = it[list(it.keys())[0]]
                            if user.discriminator != tag:
                                dqwinners.append(user)
                                return
                        if list(it.keys())[0] == "vc":

                            vc = it[list(it.keys())[0]]
                            with open("vc.json", "r+") as f:
                                vc2 = json.load(f)
                                for item in vc2:
                                    if str(user.id) not in list(item.keys())[0]:
                                        dqwinners.append(user)
                                        continue
                                    if list(item.keys())[0] == str(user.id):
                                        target = item[list(item.keys())[0]]
                                        if target[2] < float(vc):
                                            dqwinners.append(user)
                                            continue
                        if list(it.keys())[0] == "status":
                            there = 0
                            status = it[list(it.keys())[0]]
                            for item in status:
                                print(item.lower(), str(guild.get_member(user.id).status))
                                if item.lower() == str(guild.get_member(user.id).status):
                                    there = 1
                            if there != 1:
                                dqwinners.append(user)
                                continue
                        if list(it.keys())[0] == "bio":
                            bio = it[list(it.keys())[0]]

                            for act in guild.get_member(user.id).activities:

                                if isinstance(act, discord.CustomActivity):
                                    customstat = act.name
                            try:
                                if customstat != bio:
                                    dqwinners.append(user)
                                    continue
                            except Exception as e:
                                print(e)
                                dqwinners.append(user)
                                continue
                        if list(it.keys())[0] == "name":
                            name = it[list(it.keys())[0]]
                            if user.name != name:
                                dqwinners.append(user)
                                continue
                        if list(it.keys())[0] == "activity":
                            act = it[list(it.keys())[0]]
                            with open("messages.json", "r+") as f:
                                msg = json.load(f)
                                for item in msg:
                                    if list(item.keys())[0] == str(user.id):
                                        totalmsgs = item[list(item.keys())[0]]

                                try:
                                    if act == "Lurker" and totalmsgs < 1:
                                        dqwinners.append(user)
                                        continue
                                    if act == "Inactive" and totalmsgs <50:
                                        dqwinners.append(user)
                                        continue
                                    if act == "Average" and totalmsgs <100:
                                        dqwinners.append(user)
                                        continue
                                    if act == "Active" and totalmsgs <150:
                                        dqwinners.append(user)
                                        continue
                                    if act == "Hyperactive" and totalmsgs <200:
                                        dqwinners.append(user)
                                        continue
                                except Exception as e:
                                    print("error", e)
                                    dqmember.append(user)
                                    continue

                    for it in ast.literal_eval(target[1]):
                        if user in dqwinners:
                            continue
                        if list(it.keys())[0] == "acc":
                            for multi in it[list(it.keys())[0]]:
                                accolder = list(multi.keys())[0]

                                timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.created_at.replace(tzinfo=pytz.UTC)
                                if timeee.days > int(accolder):
                                    for i in range(int(multi[accolder])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "mem":
                            for multi in it[list(it.keys())[0]]:
                                memolder = list(multi.keys())[0]
                                timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.joined_at.replace(tzinfo=pytz.UTC)
                                if timeee.days > int(memolder):
                                    for i in range(int(multi[memolder])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "role":
                            for multi in it[list(it.keys())[0]]:
                                recentri = list(multi.keys())[0]
                                reqrole = get(self.context.guild.roles, id=int(list(multi.keys())[0].replace("<@&", "").replace(">","")))
                                if reqrole in user.roles:
                                    for i in range(int(multi[recentri])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "notrole":
                            for multi in it[list(it.keys())[0]]:
                                recentri = list(multi.keys())[0]
                                reqrole = get(self.context.guild.roles, id=int(list(multi.keys())[0].replace("<@&", "").replace(">","")))
                                if reqrole not in user.roles:
                                    for i in range(int(multi[recentri])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "msgs":
                            for multi in it[list(it.keys())[0]]:
                                with open("messages.json", "r+") as f:
                                    msg = json.load(f)
                                    for item in msg:
                                        if list(item.keys())[0] == str(user.id):
                                            totalmsgs = item[list(item.keys())[0]]
                                    try:
                                        if int(totalmsgs) > int(list(multi.keys())[0]):
                                            for i in range(int(multi[list(multi.keys())[0]])):
                                                totalwinner.append(user)
                                    except:
                                        pass
                        if list(it.keys())[0] == "tag":
                            for multi in it[list(it.keys())[0]]:
                                tag = list(multi.keys())[0]
                                if user.discriminator == tag:
                                    for i in range(int(multi[tag])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "vc":
                            for multi in it[list(it.keys())[0]]:
                                vc = list(multi.keys())[0]
                                with open("vc.json", "r+") as f:
                                    vc2 = json.load(f)
                                    for item in vc2:
                                        if list(item.keys())[0] == str(user.id):
                                            target = item[list(item.keys())[0]]
                                            if target[2] > float(vc):
                                                for i in range(int(multi[vc])):
                                                    totalwinner.append(user)
                        if list(it.keys())[0] == "status":
                            for multi in it[list(it.keys())[0]]:
                                there = 0
                                status = list(multi.keys())[0]
                                status2 = ast.literal_eval(status)
                                for item in status2:
                                    if item.lower() == str(user.status):
                                        there = 1
                                if there == 1:
                                    for i in range(int(multi[status])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "bio":
                            for multi in it[list(it.keys())[0]]:
                                bio = list(multi.keys())[0]
                                for act in user.activities:
                                    if isinstance(act, discord.CustomActivity):
                                        customstat = act.name
                                try:
                                    if customstat == bio:
                                        for i in range(int(multi[bio])):
                                            totalwinner.append(user)
                                except Exception as e:
                                    pass
                        if list(it.keys())[0] == "name":
                            for multi in it[list(it.keys())[0]]:
                                name = list(multi.keys())[0]
                                if user.name == name:
                                    for i in range(int(multi[name])):
                                        totalwinner.append(user)
                        if list(it.keys())[0] == "activity":
                            for multi in it[list(it.keys())[0]]:
                                activity = list(multi.keys())[0]
                                with open("messages.json", "r+") as f:
                                    msg = json.load(f)
                                    for item in msg:
                                        if list(item.keys())[0] == str(user.id):
                                            totalmsgs = item[list(item.keys())[0]]

                                    try:
                                        if act == "Lurker" and totalmsgs > 1:
                                            for i in range(int(multi[activity])):
                                                totalwinner.append(user)
                                        if act == "Inactive" and totalmsgs >50:
                                            for i in range(int(multi[activity])):
                                                totalwinner.append(user)
                                        if act == "Average" and totalmsgs >100:
                                            for i in range(int(multi[activity])):
                                                totalwinner.append(user)
                                        if act == "Active" and totalmsgs >150:
                                            for i in range(int(multi[activity])):
                                                totalwinner.append(user)
                                        if act == "Hyperactive" and totalmsgs >200:
                                            for i in range(int(multi[activity])):
                                                totalwinner.append(user)
                                    except Exception as e:
                                        pass
                    if user not in dqwinners:
                        totalwinner.append(user)
                    conn.close()

                if len(totalwinner) != 0:
                    conn = sqlite3.connect('giveaways.db')
                    c = conn.cursor()
                    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                    target = row.fetchone()

                    winemb = discord.Embed(title="Congratulations!", description=f"You have won the giveaway for [{target[4]}]({msg.jump_url})", color=colorforembed)
                    conn.close()
                    endmsg = await msg.channel.send(embed=winemb)
                    emb = discord.Embed(title=self.title, description=f"[Giveaway Has Ended]({endmsg.jump_url})", color=colorforembed)
                    await msg.edit(embed=emb)
                    for i in range(int(val2.content)):
                        realwinner = random.choice(totalwinner)
                        totalwinner.remove(realwinner)
                        await msg.channel.send(content=f"🥳 | {realwinner.mention}")
                        conn = sqlite3.connect('giveaways.db')
                        c = conn.cursor()
                        row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                        target = row.fetchone()
                        if target[-3] != "none":
                            winemb = discord.Embed(title="Congratulations!", description=f"{target[-3]}", color=colorforembed)
                            await realwinner.send(embed=winemb)
                        conn.close()
                else:
                    conn = sqlite3.connect('giveaways.db')
                    c = conn.cursor()
                    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                    target = row.fetchone()
                    winemb = discord.Embed(title="Winner couldnt be decided", description=f"It looks like nobody entered the giveaway for [{target[4]}]({msg.jump_url})  ", color=colorforembed)
                    conn.close()
                    endmsg = await msg.channel.send(embed=winemb)
                    emb = discord.Embed(title=self.title, description=f"[Giveaway Has Ended]({endmsg.jump_url})", color=colorforembed)
                    await msg.edit(embed=emb)
                with open("config.json", "r+") as f:
                    config2 = json.load(f)
                    if config2["logs"]["gend"] != "none":
                        channelforlogs = bot.get_channel(int(config2["logs"]["gend"]))
                        conn = sqlite3.connect('giveaways.db')
                        c = conn.cursor()
                        row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(self.context.guild.id, msg.id))
                        target = row.fetchone()
                        await channelforlogs.send(f"Giveaway just ended with title {target[4]} {msg.jump_url}")
                        conn.close()
                self.stop()
            else:
                conn = sqlite3.connect('giveaways.db')
                c = conn.cursor()
                embed = discord.Embed(title="Winners", description=f"How many winners can there be for this giveaway?", color=colorforembed)
                await interaction.response.edit_message(embed=embed, view=self)
                val2 = await bot.wait_for('message', check=checkint(self.context.author))

                embed = discord.Embed(title="Description", description=f"Give more details about your giveaway. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val3 = await bot.wait_for('message', check=check(self.context.author))

                embed = discord.Embed(title="Win_Message", description=f"Send this private message to the winners. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val4 = await bot.wait_for('message', check=check(self.context.author))


                embed = discord.Embed(title="Image", description=f"Image link to display in the embed. Type none to skip", color=colorforembed)
                await interaction.edit_original_message(embed=embed, view=self)
                val5 = await bot.wait_for('message', check=checkimg(self.context.author))
                c.execute('UPDATE giveaways SET multipliers="{}",requirements="{}",winners={},description="{}", image="{}", winmsg="{}" WHERE guildid = {} and id = {} '.format(self.multi, self.req,int(val2.content),val3.content, val5.content,val4.content, self.context.guild.id, self.msgid))
                conn.commit()
                conn.close()
                print("DONE")
                self.stop()
        else:

            embed = discord.Embed(title="Win_Message", description=f"Send this private message to the winners. Type none to skip", color=colorforembed)
            await interaction.response.edit_message(embed=embed, view=self)
            val4 = await bot.wait_for('message', check=check(self.context.author))

            channel = bot.get_channel(int(self.channelid.replace("<#","").replace(">","")))
            guild = self.context.guild
            dqmember = []
            for member in channel.members:
                for it in self.req:
                    if list(it.keys())[0] == "acc":
                        accolder = it[list(it.keys())[0]]
                        timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - member.created_at.replace(tzinfo=pytz.UTC)
                        if timeee.days < accolder:
                            dqmember.append(member)
                            continue
                    if list(it.keys())[0] == "mem":
                        memolder = it[list(it.keys())[0]]
                        timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - member.joined_at.replace(tzinfo=pytz.UTC)
                        if timeee.days < memolder:
                            dqmember.append(member)
                            continue
                    if list(it.keys())[0] == "role":
                        role = it[list(it.keys())[0]]
                        for rol in role:
                            reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                            if reqrole not in member.roles:
                                dqmember.append(member)
                                continue
                    if list(it.keys())[0] == "notrole":
                        notrole = it[list(it.keys())[0]]
                        for rol in notrole:
                            reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                            if reqrole in member.roles:
                                dqmember.append(member)
                                continue
                    if list(it.keys())[0] == "msgs":
                        msgs = it[list(it.keys())[0]]
                        with open("messages.json", "r+") as f:
                            msg = json.load(f)
                            for item in msg:
                                if list(item.keys())[0] == str(member.id):
                                    totalmsgs = item[list(item.keys())[0]]

                            try:
                                if int(totalmsgs) < int(msgs):
                                    dqmember.append(member)
                                    continue
                            except:
                                dqmember.append(member)
                                continue
                    if list(it.keys())[0] == "tag":
                        tag = it[list(it.keys())[0]]
                        if member.discriminator != tag:
                            dqmember.append(member)
                            return
                    if list(it.keys())[0] == "vc":

                        vc = it[list(it.keys())[0]]
                        with open("vc.json", "r+") as f:
                            vc2 = json.load(f)
                            for item in vc2:
                                if str(member.id) not in list(item.keys())[0]:
                                    dqmember.append(member)
                                    continue
                                if list(item.keys())[0] == str(member.id):
                                    target = item[list(item.keys())[0]]
                                    if target[2] < float(vc):
                                        dqmember.append(member)
                                        continue
                    if list(it.keys())[0] == "status":
                        there = 0
                        status = it[list(it.keys())[0]]
                        for item in status:
                            print(item.lower(), str(guild.get_member(member.id).status))
                            if item.lower() == str(guild.get_member(member.id).status):
                                there = 1
                        if there != 1:
                            dqmember.append(member)
                            continue
                    if list(it.keys())[0] == "bio":
                        bio = it[list(it.keys())[0]]

                        for act in guild.get_member(member.id).activities:

                            if isinstance(act, discord.CustomActivity):
                                customstat = act.name
                        try:
                            if customstat != bio:
                                dqmember.append(member)
                                continue
                        except Exception as e:
                            print(e)
                            dqmember.append(member)
                            continue
                    if list(it.keys())[0] == "name":
                        name = it[list(it.keys())[0]]
                        if member.name != name:
                            dqmember.append(member)
                            continue
                    if list(it.keys())[0] == "activity":
                        act = it[list(it.keys())[0]]
                        with open("messages.json", "r+") as f:
                            msg = json.load(f)
                            for item in msg:
                                if list(item.keys())[0] == str(member.id):
                                    totalmsgs = item[list(item.keys())[0]]

                            try:
                                if act == "Lurker" and totalmsgs < 1:
                                    dqmember.append(member)
                                    continue
                                if act == "Inactive" and totalmsgs <50:
                                    dqmember.append(member)
                                    continue
                                if act == "Average" and totalmsgs <100:
                                    dqmember.append(member)
                                    continue
                                if act == "Active" and totalmsgs <150:
                                    dqmember.append(member)
                                    continue
                                if act == "Hyperactive" and totalmsgs <200:
                                    dqmember.append(member)
                                    continue
                            except Exception as e:
                                print("error", e)
                                dqmember.append(member)
                                continue
            winmembers = []

            for member in channel.members:
                if member not in dqmember:
                    winmembers.append(member)
            if bot.user in winmembers:
                winmembers.remove(bot.user)
            if len(winmembers) != 0:
                for member in winmembers:
                    winemb = discord.Embed(title="Congratulations!", description=f"You have won the drop for {self.title}", color=colorforembed)
                    endmsg = await channel.send(embed=winemb)
                    await channel.send(content=f"🥳 | {member.mention}")
                    if val4.content != "none":
                        winemb = discord.Embed(title="Congratulations!", description=f"{val4.content}", color=colorforembed)
                        await member.send(embed=winemb)
            else:
                winemb = discord.Embed(title="Winner couldnt be decided", description=f"It looks like nobody met the requirements for {self.title}  ", color=colorforembed)
                endmsg = await channel.send(embed=winemb)



@bot.slash_command(guild_ids=config["serverids"])  # create a slash command for the supplied guilds
async def roll(ctx,msgid):
        with open("config.json", "r+") as f:
            config2 = json.load(f)
            canbeused = 0
            for role in config2["roles"]:
                reqrole = get(ctx.guild.roles, id=role)
                if reqrole in ctx.author.roles:
                    canbeused = 1
            if canbeused != 1:
                await ctx.send("You are not eligible to use the command.")
                return
            if config2["logs"]["groll"] != "none":
                channelforlogs = bot.get_channel(int(config2["logs"]["groll"]))
                await channelforlogs.send(f"{ctx.author.name} just rerolled giveaway with msgid {msgid}")
        msgforgive = await ctx.channel.fetch_message(int(msgid))
        conn = sqlite3.connect('giveaways.db')
        c = conn.cursor()
        row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(ctx.guild.id, int(msgid)))
        target = row.fetchone()
        wineeers = await msgforgive.reactions[0].users().flatten()
        if bot.user in wineeers:
            wineeers.remove(bot.user)
        totalwinner = []
        for user in wineeers:
            totalwinner.append(user)
            conn = sqlite3.connect('giveaways.db')
            for it in ast.literal_eval(target[1]):
                if list(it.keys())[0] == "acc":
                    for multi in it[list(it.keys())[0]]:
                        accolder = list(multi.keys())[0]

                        timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.created_at.replace(tzinfo=pytz.UTC)
                        if timeee.days > int(accolder):
                            for i in range(int(multi[accolder])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "mem":
                    for multi in it[list(it.keys())[0]]:
                        memolder = list(multi.keys())[0]
                        timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.joined_at.replace(tzinfo=pytz.UTC)
                        if timeee.days > int(memolder):
                            for i in range(int(multi[memolder])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "role":
                    for multi in it[list(it.keys())[0]]:
                        recentri = list(multi.keys())[0]
                        reqrole = get(ctx.guild.roles, id=int(list(multi.keys())[0].replace("<@&", "").replace(">","")))
                        if reqrole in user.roles:
                            for i in range(int(multi[recentri])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "notrole":
                    for multi in it[list(it.keys())[0]]:
                        recentri = list(multi.keys())[0]
                        reqrole = get(ctx.guild.roles, id=int(list(multi.keys())[0].replace("<@&", "").replace(">","")))
                        if reqrole not in user.roles:
                            for i in range(int(multi[recentri])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "msgs":
                    for multi in it[list(it.keys())[0]]:
                        with open("messages.json", "r+") as f:
                            msg = json.load(f)
                            for item in msg:
                                if list(item.keys())[0] == str(user.id):
                                    totalmsgs = item[list(item.keys())[0]]
                            try:
                                if int(totalmsgs) > int(list(multi.keys())[0]):
                                    for i in range(int(multi[list(multi.keys())[0]])):
                                        totalwinner.append(user)
                            except:
                                pass
                if list(it.keys())[0] == "tag":
                    for multi in it[list(it.keys())[0]]:
                        tag = list(multi.keys())[0]
                        if user.discriminator == tag:
                            for i in range(int(multi[tag])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "vc":
                    for multi in it[list(it.keys())[0]]:
                        vc = list(multi.keys())[0]
                        with open("vc.json", "r+") as f:
                            vc2 = json.load(f)
                            for item in vc2:
                                if list(item.keys())[0] == str(user.id):
                                    target = item[list(item.keys())[0]]
                                    if target[2] > float(vc):
                                        for i in range(int(multi[vc])):
                                            totalwinner.append(user)
                if list(it.keys())[0] == "status":
                    for multi in it[list(it.keys())[0]]:
                        there = 0
                        status = list(multi.keys())[0]
                        status2 = ast.literal_eval(status)
                        for item in status2:
                            if item.lower() == str(user.status):
                                there = 1
                        if there == 1:
                            for i in range(int(multi[status])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "bio":
                    for multi in it[list(it.keys())[0]]:
                        bio = list(multi.keys())[0]
                        for act in user.activities:
                            if isinstance(act, discord.CustomActivity):
                                customstat = act.name
                        try:
                            if customstat == bio:
                                for i in range(int(multi[bio])):
                                    totalwinner.append(user)
                        except Exception as e:
                            pass
                if list(it.keys())[0] == "name":
                    for multi in it[list(it.keys())[0]]:
                        name = list(multi.keys())[0]
                        if user.name == name:
                            for i in range(int(multi[name])):
                                totalwinner.append(user)
                if list(it.keys())[0] == "activity":
                    for multi in it[list(it.keys())[0]]:
                        activity = list(multi.keys())[0]
                        with open("messages.json", "r+") as f:
                            msg = json.load(f)
                            for item in msg:
                                if list(item.keys())[0] == str(user.id):
                                    totalmsgs = item[list(item.keys())[0]]

                            try:
                                if act == "Lurker" and totalmsgs > 1:
                                    for i in range(int(multi[activity])):
                                        totalwinner.append(user)
                                if act == "Inactive" and totalmsgs >50:
                                    for i in range(int(multi[activity])):
                                        totalwinner.append(user)
                                if act == "Average" and totalmsgs >100:
                                    for i in range(int(multi[activity])):
                                        totalwinner.append(user)
                                if act == "Active" and totalmsgs >150:
                                    for i in range(int(multi[activity])):
                                        totalwinner.append(user)
                                if act == "Hyperactive" and totalmsgs >200:
                                    for i in range(int(multi[activity])):
                                        totalwinner.append(user)
                            except Exception as e:
                                pass
        if len(totalwinner) != 0:
            winemb = discord.Embed(title="Congratulations!", description=f"You have won the giveaway for [{target[4]}]({msgforgive.jump_url})", color=colorforembed)
            endmsg = await msgforgive.channel.send(embed=winemb)
            emb = discord.Embed(title=target[4], description=f"[Giveaway Has Ended]({endmsg.jump_url})", color=colorforembed)
            await msgforgive.edit(embed=emb)
            for i in range(int(target[3])):
                realwinner = random.choice(totalwinner)
                totalwinner.remove(realwinner)
                await msgforgive.channel.send(content=f"🥳 | {realwinner.mention}")
                if target[-3] != "none":
                    winemb = discord.Embed(title="Congratulations!", description=f"{target[-3]}", color=colorforembed)
                    await realwinner.send(embed=winemb)
                conn.close()
        else:
            winemb = discord.Embed(title="Winner couldnt be decided", description=f"It looks like nobody entered the giveaway for [{target[4]}]({msgforgive.jump_url})  ", color=colorforembed)
            endmsg = await msgforgive.channel.send(embed=winemb)
            emb = discord.Embed(title=target[4], description=f"[Giveaway Has Ended]({endmsg.jump_url})", color=colorforembed)
            await msgforgive.edit(embed=emb)

        conn.close()


@bot.slash_command(guild_ids=config["serverids"])  # create a slash command for the supplied guilds
async def create(ctx, title,  length):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return

    length = length.split()
    totaltime = 0
    for item in length:
        if "s" in item:
            timeee = item.replace("s", "")
            if timeee.isnumeric():
                totaltime += int(timeee)
            else:
                await ctx.send("Please choose a correct time format (1s, 1m, 1h, 1d)", ephemeral=True)
                return
        elif "m" in item:
            timeee = item.replace("m", "")
            if timeee.isnumeric():
                totaltime += int(timeee)*60
            else:
                await ctx.send("Please choose a correct time format (1s, 1m, 1h, 1d)", ephemeral=True)
                return
        elif "h" in item:
            timeee = item.replace("h", "")
            if timeee.isnumeric():
                totaltime += int(timeee)*3600
            else:
                await ctx.send("Please choose a correct time format (1s, 1m, 1h, 1d)", ephemeral=True)
                return
        elif "d" in item:
            timeee = item.replace("d", "")
            if timeee.isnumeric():
                totaltime += int(timeee)*3600*24
            else:
                await ctx.send("Please choose a correct time format (1s, 1m, 1h, 1d)", ephemeral=True)
                return
        else:
            await ctx.send("Please choose a correct time format (1s, 1m, 1h, 1d)", ephemeral=True)
            return
    view = Buttons(ctx, title, totaltime)
    embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
    embed.add_field(name="Basic Settings", value=f"""
    <:stem:890923334240469014> **Title**: {title}
    <:stem:890923334240469014> **Description**: None
    <:stem:890923334240469014> **Length**: {time_format(totaltime)}
    <:stem:890923334240469014> **Emoji**: 🥳
    <:stem:890923334240469014> **Winners**: 1

     """, inline=False)
    embed.add_field(name="Requirements", value=f"""
     `No Requirements Yet`
      """, inline=False)
    embed.add_field(name="Multipliers", value=f"""
    `No Multipliers Yet`
     """, inline=False)
    await ctx.send(embed=embed, view=view, ephemeral=False)


    await view.wait()
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        if config2["logs"]["gstart"] != "none":
            channelforlogs = bot.get_channel(int(config2["logs"]["gstart"]))
            await channelforlogs.send(f"{ctx.author.name} just created giveaway with title {title}")
@bot.slash_command(guild_ids=config["serverids"])  # create a slash command for the supplied guilds
async def edit(ctx, id):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return


    conn = sqlite3.connect('giveaways.db')
    c = conn.cursor()
    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND id = {}'.format(ctx.guild.id, int(id)))
    target = row.fetchone()
    if target != None:
        multi = ast.literal_eval(target[1])
        req = ast.literal_eval(target[2])
        title = target[4]
        totaltime = target[5]
        view = Buttons(ctx, title, totaltime, multi, req, int(id))
        if target[7].lower() != "none" :
            emb = discord.Embed(title=target[4], description=target[7], color=colorforembed)
        else:
            emb = discord.Embed(title=target[4], color=colorforembed)
        if target[8].lower() != "none":
            emb.set_image(url=target[8])
        added = 0
        requirrrr = []
        multiii = []
        for item in ast.literal_eval(target[2]):
            if list(item.keys())[0] == "acc":
                val = requirrrr.append(f"Account must be older than ``{item.get('acc')}`` days.")
            if list(item.keys())[0] == "mem":
                val = requirrrr.append(f"Be in this discord for at least ``{item.get('mem')}`` days.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = requirrrr.append(f"have the {ite} role.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = requirrrr.append(f"**not** have the {ite} role.")
            if list(item.keys())[0] == "msgs":
                val = requirrrr.append(f"Have sent ``{item.get('msgs')}`` messages.")
            if list(item.keys())[0] == "tag":
                val = requirrrr.append(f"Have the ``#{item.get('tag')}`` tag.")
            if list(item.keys())[0] == "vc":
                val = requirrrr.append(f"Been in VCs ``{item.get('vc')}`` minutes.")
            if list(item.keys())[0] == "status":
                val = requirrrr.append(" Must be {} ".format(" or ".join(item.get('status'))))
            if list(item.keys())[0] == "bio":
                val = requirrrr.append(f"Have `{item.get('bio')}` in your custom status. ")
            if list(item.keys())[0] == "name":
                val = requirrrr.append(f"Must have ``{item.get('name')}`` in name.")
            if list(item.keys())[0] == "activity":
                val = requirrrr.append(f"Must be at least ``{item.get('activity')}`` level of activity.")
        if len(requirrrr) != 0:
            emb.add_field(name="Requirements", value="\n".join(requirrrr), inline=False)
        else:
            emb.add_field(name="Requirements", value=f"""
            `No requirements Yet`
             """, inline=False)
        for item in ast.literal_eval(target[1]):
            if list(item.keys())[0] == "acc":
                for ite in item.get('acc'):
                    val = multiii.append(f"Account older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")

            if list(item.keys())[0] == "mem":
                for ite in item.get('mem'):
                    val = multiii.append(f"Members older than ``{list(ite.keys())[0]}`` days get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "role":
                for ite in item.get('role'):
                    val = multiii.append(f"Users with role {list(ite.keys())[0]}  get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "notrole":
                for ite in item.get('notrole'):
                    val = multiii.append(f"Users without role {list(ite.keys())[0]} get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "msgs":
                for ite in item.get('msgs'):
                    val = multiii.append(f"Users with atleast``{list(ite.keys())[0]}`` msgs get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "tag":
                for ite in item.get('tag'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` tag get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "vc":
                for ite in item.get('vc'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` VC minutes get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "status":
                for ite in item.get('status'):
                    val = multiii.append("Users who are ``{}`` get ``+{} entries``.".format(" or ".join(ast.literal_eval(list(ite.keys())[0])),ite.get(list(ite.keys())[0])))
            if list(item.keys())[0] == "bio":
                for ite in item.get('bio'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in custom status get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "name":
                for ite in item.get('name'):
                    val = multiii.append(f"Users with ``{list(ite.keys())[0]}`` in name get ``+{ite.get(list(ite.keys())[0])} entries``.")
            if list(item.keys())[0] == "activity":
                for ite in item.get('activity'):
                    val = multiii.append("Users with activity level ``{}`` get ``+{} entries``.".format(list(ite.keys())[0] , ite.get(list(ite.keys())[0])))
        newmulti = []
        for index, value in enumerate(multiii, 1):
            itemm = "**"+str(index)+".** "+str(value)
            newmulti.append(itemm)
        if len(multiii) != 0:
            emb.add_field(name="Multipliers", value="\n".join(newmulti), inline=False)
        else:
            if not self.drop:
                emb.add_field(name="Multipliers", value=f"""
                `No Multipliers Yet`
                 """, inline=False)
        emb.add_field(name="No. of Winners:", value=str(target[3]), inline=False)
        x = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(seconds=target[5])
        emb.add_field(name="Time:", value="<t:"+str(int(x.timestamp()))+":R>")
        await ctx.send(embed=emb, view=view, ephemeral=False)
        added = 1
        await view.wait()
        with open("config.json", "r+") as f:
            config2 = json.load(f)
            if config2["logs"]["gedit"] != "none":
                channelforlogs = bot.get_channel(int(config2["logs"]["gedit"]))
                await channelforlogs.send(f"{ctx.author.name} just edited giveaway with id {id}")
    else:
        await ctx.send("Please write the correct id", ephemeral=True)


@bot.event
async def on_raw_reaction_add(payload):

    if payload.member == bot.user:
        return
    channel = bot.get_channel(payload.channel_id)
    user = await bot.fetch_user(payload.user_id)
    guild = bot.get_guild(payload.guild_id)
    message = await channel.fetch_message(payload.message_id)
    conn = sqlite3.connect('giveaways.db')
    c = conn.cursor()
    row = c.execute('SELECT * from giveaways WHERE guildid = {} AND msgid = {}'.format(guild.id, int(payload.message_id)))
    target = row.fetchone()
    for it in ast.literal_eval(target[2]):
        if list(it.keys())[0] == "acc":
            accolder = it[list(it.keys())[0]]

            timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - user.created_at.replace(tzinfo=pytz.UTC)
            if timeee.days < accolder:
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "mem":
            memolder = it[list(it.keys())[0]]
            timeee = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) - payload.member.joined_at.replace(tzinfo=pytz.UTC)
            if timeee.days < memolder:
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "role":
            role = it[list(it.keys())[0]]
            for rol in role:
                reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                if reqrole not in payload.member.roles:
                    await message.remove_reaction("👍", payload.member)
                    embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                    await user.send(embed=embed)
                    return
        if list(it.keys())[0] == "notrole":
            notrole = it[list(it.keys())[0]]
            for rol in notrole:
                reqrole = get(guild.roles, id=int(rol.replace("<@&", "").replace(">","")))
                if reqrole in payload.member.roles:
                    await message.remove_reaction("👍", payload.member)
                    embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                    await user.send(embed=embed)
                    return
        if list(it.keys())[0] == "msgs":
            msgs = it[list(it.keys())[0]]
            with open("messages.json", "r+") as f:
                msg = json.load(f)
                for item in msg:
                    if list(item.keys())[0] == str(message.author.id):
                        totalmsgs = item[list(item.keys())[0]]

                try:
                    if int(totalmsgs) < int(msgs):
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                except:
                    await message.remove_reaction("👍", payload.member)
                    embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                    await user.send(embed=embed)
                    return
        if list(it.keys())[0] == "tag":
            tag = it[list(it.keys())[0]]
            if user.discriminator != tag:
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "vc":

            vc = it[list(it.keys())[0]]
            with open("vc.json", "r+") as f:
                vc2 = json.load(f)
                for item in vc2:
                    if str(user.id) not in list(item.keys())[0]:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)

                        return
                    if list(item.keys())[0] == str(user.id):
                        target = item[list(item.keys())[0]]
                        if target[2] < float(vc):
                            await message.remove_reaction("👍", payload.member)
                            embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                            await user.send(embed=embed)

                            return
        if list(it.keys())[0] == "status":
            there = 0
            status = it[list(it.keys())[0]]
            for item in status:
                print(item.lower(), str(guild.get_member(payload.user_id).status))
                if item.lower() == str(guild.get_member(payload.user_id).status):
                    there = 1
            if there != 1:
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "bio":
            bio = it[list(it.keys())[0]]

            for act in guild.get_member(payload.user_id).activities:

                if isinstance(act, discord.CustomActivity):
                    customstat = act.name
            try:
                if customstat != bio:
                    await message.remove_reaction("👍", payload.member)
                    embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                    await user.send(embed=embed)
                    return
            except Exception as e:
                print(e)
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "name":
            name = it[list(it.keys())[0]]
            if user.name != name:
                await message.remove_reaction("👍", payload.member)
                embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                await user.send(embed=embed)
                return
        if list(it.keys())[0] == "activity":
            act = it[list(it.keys())[0]]
            with open("messages.json", "r+") as f:
                msg = json.load(f)
                for item in msg:
                    if list(item.keys())[0] == str(user.id):
                        totalmsgs = item[list(item.keys())[0]]

                try:
                    if act == "Lurker" and totalmsgs < 1:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                    if act == "Inactive" and totalmsgs <50:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                    if act == "Average" and totalmsgs <100:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                    if act == "Active" and totalmsgs <150:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                    if act == "Hyperactive" and totalmsgs <200:
                        await message.remove_reaction("👍", payload.member)
                        embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                        await user.send(embed=embed)
                        return
                except Exception as e:
                    print("error", e)
                    await message.remove_reaction("👍", payload.member)
                    embed = discord.Embed(title="You can't join the giveaway", description="You don't meet the requirements for the giveaway.", color=colorforembed)
                    await user.send(embed=embed)
                    return





@bot.event
async def on_message(message):
    added = 0
    if message.author == bot.user:
        return
    with open("config.json", "r+") as ff:
        config2 = json.load(ff)
        if message.channel.id in config2["blacklistchannels"]:
            return
        for role in config2["blacklistroles"]:
            member = message.guild.get_member(message.author.id)
            reqrole = get(message.guild.roles, id=role)
            if reqrole in member.roles:
                return

    with open("messages.json", "r+") as f:
        msg = json.load(f)
        for item in msg:
            if list(item.keys())[0] == str(message.author.id):
                item[list(item.keys())[0]] += 1
                added = 1
                f.seek(0)
                json.dump(msg, f, indent=4)
        if added != 1:
            msg.append({str(message.author.id): 1})
            f.seek(0)
            json.dump(msg, f, indent=4)
            added = 0

@bot.slash_command(guild_ids=config["serverids"])  # create a slash command for the supplied guilds
async def drop(ctx, title, channel):
        with open("config.json", "r+") as f:
            config2 = json.load(f)
            canbeused = 0
            for role in config2["roles"]:
                reqrole = get(ctx.guild.roles, id=role)
                if reqrole in ctx.author.roles:
                    canbeused = 1
            if canbeused != 1:
                await ctx.send("You are not eligible to use the command.")
                return
            if config2["logs"]["drop"] != "none":
                channelforlogs = bot.get_channel(int(config2["logs"]["drop"]))
                await channelforlogs.send(f"{ctx.author.name} just dropped giveaway with title {title} on channel {bot.get_channel(int(channel)).name}")
        view = Buttons(ctx, title, 100, drop="yes", channelid=channel)
        embed = discord.Embed(title="Create a New Giveaway", color=colorforembed)
        embed.add_field(name="Basic Settings", value=f"""
        <:stem:890923334240469014> **Title**: {title}
        <:stem:890923334240469014> **Description**: None
        <:stem:890923334240469014> **Emoji**: 🥳
         """, inline=False)
        embed.add_field(name="Requirements", value=f"""
         `No Requirements Yet`
          """, inline=False)
        await ctx.send(embed=embed, view=view, ephemeral=False)


        await view.wait()
        with open("config.json", "r+") as f:
            config2 = json.load(f)
            if config2["logs"]["drop"] != "none":
                channelforlogs = bot.get_channel(int(config2["logs"]["drop"]))
                await channelforlogs.send(f"{ctx.author.name} just dropped giveaway with title {title} on channel {bot.get_channel(int(channel)).name}")
@bot.slash_command(guild_ids=config["serverids"])  # c  reate a slash command for the supplied guilds
async def clear(ctx):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return
    with open("messages.json", "r+") as f:
        msg = json.load(f)
        msg = []
        f.seek(0)
        json.dump(msg, f, indent=4)
    with open("vc.json", "r+") as f:
        vc = json.load(f)
        vc = []
        f.seek(0)
        json.dump(vc, f, indent=4)

@bot.slash_command(guild_ids=config["serverids"]) # create a slash command for the supplied guilds
async def leaderboard(ctx,channel, type:Option(str, "Must be one of these (msg, vc)", choices=["msg", "vc"])):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return
    channel = bot.get_channel(int(channel.replace("<#","").replace(">","")))
    if type == "msg":
        msgs = []
        position = 1
        with open("messages.json", "r+") as f:
            msg = json.load(f)
            msg = sorted(msg, key=lambda x : list(x.values())[0], reverse=True)
            for item in msg:
                userr = await bot.fetch_user(int(list(item.keys())[0]))
                msgs.append(f"``#{position}``. <:Message:891104566685347881> — {userr.name} — ``{item[list(item.keys())[0]]} Messages``\n")
                position +=1
        embed = discord.Embed(title="Messages Leaderboard", description="".join(msgs), color=colorforembed)

        embedmsg = await channel.send(embed=embed)
        while True:
            await asyncio.sleep(10)
            position = 1
            with open("messages.json", "r+") as f:
                msgs = []
                msg = json.load(f)
                msg = sorted(msg, key=lambda x : list(x.values())[0], reverse=True)
                for item in msg:
                    userr = await bot.fetch_user(int(list(item.keys())[0]))
                    msgs.append(f"``#{position}``. <:Message:891104566685347881> — {userr.name} — ``{item[list(item.keys())[0]]} Messages``\n")
                    position +=1
            embed = discord.Embed(title="Messages Leaderboard", description="".join(msgs), color=colorforembed)
            messages = await channel.history(limit=100).flatten()
            for msg in messages:
                if msg.embeds:
                    if msg.embeds[0].title == "Messages Leaderboard":
                        await msg.edit(embed=embed)
    elif type == "vc":
        vcs = []
        position = 1
        with open("vc.json", "r+") as f:
            vc = json.load(f)
            vc = sorted(vc, key=lambda x : list(x.values())[0][-1], reverse=True)
            for item in vc:
                userr = await bot.fetch_user(int(list(item.keys())[0]))
                vcs.append(f"``#{position}``. <:VoiceChat:891103809189863444> — {userr.name} — ``{int(item[list(item.keys())[0]][-1])} Minutes``\n")
                position +=1
        embed = discord.Embed(title="Voice Leaderboard", description="".join(vcs), color=colorforembed)
        await ctx.send(embed=embed)
        while True:
            await asyncio.sleep(10)
            position = 1
            with open("messages.json", "r+") as f:
                vcs = []
                vc = sorted(vc, key=lambda x : list(x.values())[0][-1], reverse=True)
                for item in vc:
                    userr = await bot.fetch_user(int(list(item.keys())[0]))
                    vcs.append(f"``#{position}``. <:VoiceChat:891103809189863444> — {userr.name} — ``{int(item[list(item.keys())[0]][-1])} Minutes``\n")
                    position +=1
            embed = discord.Embed(title="Voice Leaderboard", description="".join(vcs), color=colorforembed)
            messages = await channel.history(limit=100).flatten()
            for msg in messages:
                if msg.embeds:
                    if msg.embeds[0].title == "Voice Leaderboard":
                        await msg.edit(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    with open("config.json", "r+") as ff:
        config2 = json.load(ff)
        for role in config2["blacklistroles"]:
            reqrole = get(member.guild.roles, id=role)
            if reqrole in member.roles:
                return
    added = 0
    with open("vc.json", "r+") as f:
        vc = json.load(f)
        if not before.channel and after.channel:
            print("joined")
            for item in vc:
                if list(item.keys())[0] == str(member.id):
                    target = item[list(item.keys())[0]]
                    target[0] = str(datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                    f.seek(0)
                    json.dump(vc, f, indent=4)
                    added = 1
            if added != 1:
                dictt = {str(member.id): [str(datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)),"", 0]}
                vc.append(dictt)
                f.seek(0)
                json.dump(vc, f, indent=4)
        if not after.channel and before.channel:
            print("left")
            for item in vc:
                if list(item.keys())[0] == str(member.id):
                    target = item[list(item.keys())[0]]

                    target[1] = str(datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
                    leavingt = parser.parse(target[1])
                    joiningt = parser.parse(target[0])
                    totalmins = leavingt -joiningt
                    target[2] += int(totalmins.seconds)/60
                    f.seek(0)
                    json.dump(vc, f, indent=4)

@bot.slash_command(guild_ids=config["serverids"])  # c  reate a slash command for the supplied guilds
async def server(ctx):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return

    with open("config.json", "r+") as f:
        config2 = json.load(f)
        channels = []
        roles = []
        blacklistroles = []
        for role in config2["roles"]:
            roles.append("<@&"+str(role)+">")
        for channel in config2["blacklistchannels"]:
            channels.append("<#"+str(channel)+">")
        for role in config2["blacklistroles"]:
            blacklistroles.append("<@&"+str(role)+">")
        if len(blacklistroles) == 0:
            blacklistroles.append("None")
        if len(roles) == 0:
            roles.append("None")
        if len(channels) == 0:
            channels.append("None")
        embed = discord.Embed(title="Server Settings", description=f"""
        Roles who can user the bot:  {" ".join(roles)}
        Blacklisted Channels: {" ".join(channels)}
        Blacklisted Roles: {" ".join(blacklistroles)}
        """, color=colorforembed)

        await ctx.send(embed=embed, view=Servers(ctx))



@bot.slash_command(guild_ids=config["serverids"])  # c  reate a slash command for the supplied guilds
async def logs(ctx, id:Option(str, "Thread")):
    view = Logs(ctx,int(id), ctx.channel.id)
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        canbeused = 0
        for role in config2["roles"]:
            reqrole = get(ctx.guild.roles, id=role)
            if reqrole in ctx.author.roles:
                canbeused = 1
        if canbeused != 1:
            await ctx.send("You are not eligible to use the command.")
            return
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        if config2["logs"] =={}:
            embed = discord.Embed(title="Add Channel Log", description="``No Logs Channel Yet``", color=colorforembed)
        else:
            embed = discord.Embed(title="Add Channel Log", color=colorforembed)
            if config2["logs"]["invite"] != "none":
                embed.add_field(name="User Invite Log", value="<#"+str(config2["logs"]["invite"])+">")
            if config2["logs"]["leave"] != "none":
                embed.add_field(name="User Leave Log", value="<#"+str(config2["logs"]["leave"])+">")
            if config2["logs"]["gstart"] != "none":
                embed.add_field(name="Giveaway Start Log", value="<#"+str(config2["logs"]["gstart"])+">")
            if config2["logs"]["gedit"] != "none":
                embed.add_field(name="Giveaway Edit Log", value="<#"+str(config2["logs"]["gedit"])+">")
            if config2["logs"]["gend"] != "none":
                embed.add_field(name="Giveaway End Log", value="<#"+str(config2["logs"]["gend"])+">")
            if config2["logs"]["groll"] != "none":
                embed.add_field(name="Giveaway Roll Log", value="<#"+str(config2["logs"]["groll"])+">")
            if config2["logs"]["drop"] != "none":
                embed.add_field(name="Drop Send Log", value="<#"+str(config2["logs"]["drop"])+">")
        await ctx.send(embed=embed, view=view)

        await view.wait()

@bot.event
async def on_member_join(member):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        if config2["logs"]["invite"] != "none":
        	print(int(config2["logs"]["invite"]))
        	channelforlogs = bot.get_channel(int(config2["logs"]["invite"]))
        	await channelforlogs.send(f"{member.name} has joined the server")
    invites_before_join = custom_invites[str(member.guild.id)]
    invites_after_join = await member.guild.invites()
    if len(invites_before_join) == 0:
        for invite in invites_after_join:
            tup = [invite.inviter.name, 1, member.name, 'test']
            invite_uses[str(member.guild.id)].append(tup)
            with open('invites.json', 'r+') as fp:
                fp.seek(0)
                json.dump(invite_uses, fp)
            return
    for invite in invites_before_join:
        if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
            custom_invites[str(member.guild.id)] = invites_after_join
            for i in invite_uses[str(member.guild.id)]:
                if invite.inviter.name == i[0] and member.name == i[2]:
                    i[1] += 1
                    with open('invites.json', 'r+') as fp:
                        fp.seek(0)
                        json.dump(invite_uses, fp)
                    return
        tup = [invite.inviter.name, 1, member.name, 'test']
        invite_uses[str(member.guild.id)].append(tup)
        with open('invites.json', 'r+') as fp:
            fp.seek(0)
            json.dump(invite_uses, fp)
        return
    else:
        custom_invites[str(member.guild.id)] = invites_after_join
        tup = [invite.inviter.name, 1, member.name, 'test']
        invite_uses[str(member.guild.id)].append(tup)
        with open('invites.json', 'r+') as fp:
            fp.seek(0)
            json.dump(invite_uses, fp)
        return

@bot.event
async def on_member_remove(member):
    with open("config.json", "r+") as f:
        config2 = json.load(f)
        if config2["logs"]["leave"] != "none":
            channelforlogs = bot.get_channel(int(config2["logs"]["leave"]))
            await channelforlogs.send(f"{member.name} just left the server")
    custom_invites[str(member.guild.id)] = await member.guild.invites()
    for invite in invite_uses[str(member.guild.id)]:
        if invite[2] == member.name:
            invite[1] -= 1
            with open('invites.json', 'r+') as fp:
                fp.seek(0)
                json.dump(invite_uses, fp)
            return


@bot.slash_command(guild_ids=config["serverids"])  # c  reate a slash command for the supplied guilds
async def help(ctx):
    embed = discord.Embed(title="Help Command", description="""<a:GiveawayBox:891089778060189748> **Giveaways**\n⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺\n
    **<a:CuteGiveaway:887371033072504842> Commands used for creating a giveaway**\n
    ⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺⸺\n\n<a:Giveaway:878416482172821545>
    **Creating your first giveaway**\nStart the interactive wizard with ``/create``.\n\n
    You can then add your requirements and choose how your giveaway should run. After that, click the button to start it!\n\n
    <a:GiveawayBlob:891089778517356574> **Giveaway management**\n
    You can use the ``/list`` command to list all the giveaways you have done, including active ones.\n\n
    <a:ArrowSlideRight:889661564150485023> ``/edit <Giveaway ID>`` edits a giveaway.\n
    <a:ArrowSlideRight:889661564150485023> ``/roll <Message ID>`` ends/rerolls an active/completed giveaway.\n\n
    <a:CatGame:886106018457743431> **Leaderboards**\nYou can create auto updating leaderboards by specifying the channel. ``/leaderboard [channel] <type>``. They will update every 5 minutes with the newest data. Delete the messages to remove them.\n\n<a:PaimonCookies:885646876387446807> **User information**\nYou can view user information with ``/info [member]``.\n\n
    <a:GiveawayExplosion:891089778529931295> **Server management**\nSay you would like to reset statistics for your server, like message counts. Just use ``/clear``, To add blacklist channels use ``/server`` and I will bring up an interactive menu where you can manage everything about your server's data.\n\nTyping ``/logs [channelid]`` will bring up the logs menu where you can choose channels to send specific events to.""", color=colorforembed)
    await ctx.send(embed=embed)

@bot.slash_command(guild_ids=config["serverids"])  # c  reate a slash command for the supplied guilds
async def info(ctx, member:Option(discord.Member, "Mention discord member you want to view info of")):
    embed = discord.Embed(title="Info", description=f"""<a:KleeNoted:890177351755890699> **{member.name}'s Info**\n<:BlankSpace:885911191430504448>""", color=colorforembed)
    msgsforuser = 0
    vcsforuser = 0
    with open("messages.json", "r+") as f:
        msg = json.load(f)
        for item in msg:
            if list(item.keys())[0] == str(member.id):
                embed.add_field(name="<:Message:891104566685347881> Messages", value=f"{item[list(item.keys())[0]]}")
                msgsforuser = 1
                break
    with open("vc.json", "r+") as f:
        vc = json.load(f)
        for item in vc:
            if list(item.keys())[0] == str(member.id):
                vcsforuser = 1
                embed.add_field(name="<:VoiceChat:891103809189863444> Voice Activity", value=f"{int(item[list(item.keys())[0]][-1])} minutes")
                break
    if msgsforuser == 0:
        embed.add_field(name="<:Message:891104566685347881> Messages", value=f"0")
    if vcsforuser == 0:
        embed.add_field(name="<:VoiceChat:891103809189863444> Voice Activity", value=f"0 minutes")
    invitedby = 0
    invitesforuser = 0
    with open("invites.json", "r+") as f:
        d = defaultdict(int)
        invites = json.load(f)
        if len(invites[str(ctx.guild.id)]) != 0:
            users = invites[str(ctx.guild.id)]
            for i in users:
                if i[2] == member.name:
                    embed.add_field(name="<:InvitedBy:891106551174144000> Invited by", value=f"{i[0]}")
                    invitedby = 1
                if i[1] == 0:
                    users.remove(i)
            for t in users:
                d[(t[0], t[-1])] += t[1]
            result = [(k[0], d[k], k[1]) for k in d]
            users = result
            for user in users:
                print(user)
                if user[0] == member.name:
                    embed.add_field(name="<:Invited:891103809399558244> Invites", value=f"{user[1]} invites")
                    invitesforuser = 1
                    break
    if invitedby == 0:
        embed.add_field(name="<:InvitedBy:891106551174144000> Invited by", value=f"None")
    if invitesforuser == 0:
        embed.add_field(name="<:Invited:891103809399558244> Invites", value=f"0 invites")
    embed.add_field(name="<:Joined:891103809038876762> Joined", value=f'<t:{int(member.joined_at.timestamp())}:R>')
    embed.add_field(name="<:React:891103809068212245> Created", value=f'<t:{int(member.created_at.timestamp())}:R>')
    await ctx.send(embed=embed)



bot.run(config["token"])
