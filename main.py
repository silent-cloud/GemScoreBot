import discord
import os
import logging
import json
import validators
import asyncio
from discord.ext import commands
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)

# token = None
# with open("info.txt", "r") as info_data:
#     token = info_data.readline()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

bot.remove_command('help')

@bot.command()
async def verify(ctx, user: discord.Member):
    user_exists = False
    verified = False
    i = 0

    with open("data.json", "r") as data_file:
        json_data = data_file.read()
    data_list = json.loads(json_data)

    while i < len(data_list) and not user_exists:
        if data_list[i]['user'] == str(user):
            user_exists = True
            if not data_list[i]['is_verified']:
                data_list[i]['is_verified'] = True
                data_list[i]['verified_by'] = ctx.author.display_name + " (" + str(ctx.author) + ")"
            else:
                verified = True
            break
        else:
            i += 1

    if user_exists and not verified:
        new_entry = json.dumps(data_list, indent=4)
        with open("data.json", "w") as data_file:
            data_file.write(new_entry)
        await ctx.send('Verified gem score for {0.name}.'.format(user))
    elif user_exists and verified:
        await ctx.send('Gem score already verified for {0.name}.'.format(user))
    else:
        await ctx.send('{0.name} does not have gem score submitted.'.format(user))


@bot.command()
async def unverify(ctx, user: discord.Member):
    user_exists = False
    unverified = False
    i = 0

    with open("data.json", "r") as data_file:
        json_data = data_file.read()
    data_list = json.loads(json_data)

    while i < len(data_list) and not user_exists:
        if data_list[i]['user'] == str(user):
            user_exists = True
            if data_list[i]['is_verified']:
                data_list[i]['is_verified'] = False
                data_list[i]['verified_by'] = ""
            else:
                unverified = True
            break
        else:
            i += 1

    if user_exists and not unverified:
        new_entry = json.dumps(data_list, indent=4)
        with open("data.json", "w") as data_file:
            data_file.write(new_entry)
        await ctx.send('Unverified gem score for {0.name}.'.format(user))
    elif user_exists and unverified:
        await ctx.send('Gem score already unverified for {0.name}.'.format(user))
    else:
        await ctx.send('{0.name} does not have gem score submitted.'.format(user))


@bot.command()
async def update(ctx, arg1):
    valid = validators.url(arg1)
    if valid:
        with open("data.json", "r") as data_file:
            json_data = data_file.read()
        data_list = json.loads(json_data)
        user_exists = False
        i = 0
        while i < len(data_list) and not user_exists:
            if data_list[i]['user'] == str(ctx.author):
                user_exists = True
                data_list[i]['link'] = arg1
                data_list[i]['is_verified'] = False
                data_list[i]['verified_by'] = ""
                new_entry = json.dumps(data_list, indent=4)
                with open("data.json", "w") as data_file:
                    data_file.write(new_entry)
            else:
                i += 1
        if not user_exists:
            entry = {"user": str(ctx.author), "link": arg1, "is_verified": False, "verified_by": ""}
            data_list.append(entry)
            new_entry = json.dumps(data_list, indent=4)
            print(new_entry)
            with open("data.json", "w") as data_file:
                data_file.write(new_entry)
        await ctx.send("Updated Score!")
    else:
        await ctx.send("Invalid Url")


@bot.command()
async def gem(ctx, *args):

  # No arguments, display the user's gem score
  if (len(args) < 1):
    user = ctx.author
    user_name = ctx.author.display_name + " (" + str(ctx.author) + ")"
    user_avatar = str(ctx.author.avatar_url)
  elif(len(args) == 1 and len(args[0]) == 1):
    await ctx.send("Cannot search with one character, please try again.")
    return
  else:
    user = ""
    user_raw = ' '.join(args)
    user_list = ctx.guild.members
    duplicate_name_list = []

    if (user_raw.startswith("<@!")):
      user_raw = user_raw.strip("<@!>")
      user_raw = str(await bot.fetch_user(int(user_raw)))

    # Check the member list for name given, either nickname or discord tag
    for i in user_list:
      if (user_raw.lower() in i.display_name.lower() or user_raw.lower() in str(i).lower()):
        duplicate_name_list.append(i)

    if (len(duplicate_name_list) == 0):
      await ctx.send("There is no user in the server with that name.")
      return
    # No duplicate found
    elif (len(duplicate_name_list) == 1):
      user = duplicate_name_list[0]
    # Duplicates found
    elif (len(duplicate_name_list) > 1):
      channel = ctx.channel

      message = "```I found {} users with that name\n".format(len(duplicate_name_list))
      message = message + "Please type the number of the user whose gem you want to see\n\n"
        
      count = 0
      for i in duplicate_name_list:
        count = count + 1
        message = message + "[{}] {} ({})\n".format(count, i.display_name, str(i))
      message = message + "```"

      await channel.send(message)

      def check(m):
        return m.author == ctx.author and m.content.isnumeric() and 1 <= int(m.content) <= len(duplicate_name_list) and m.channel == channel

      try:
        msg = await bot.wait_for('message', timeout=60.0, check=check)
      except asyncio.TimeoutError:
        #def is_me(m):
          #return m.author == bot.user

        #await channel.purge(limit=1, check=is_me)
        await channel.send("You did not respond in time. Please try again.")
        return
      else:
        user = duplicate_name_list[int(msg.content) - 1]



  user_name = user.display_name + " (" + str(user) + ")"
  user_avatar = str(user.avatar_url)

  user_exists = False
  user_gem_link = ""
  user_verified = False
  user_verified_msg = ""
  user_verified_by = ""
  i = 0

  with open("data.json", "r") as data_file:
      json_data = data_file.read()
  data_list = json.loads(json_data)

  while i < len(data_list) and not user_exists:
      if data_list[i]['user'] == str(user):
          user_exists = True
          user_verified = data_list[i]['is_verified']
          user_verified_by = data_list[i]['verified_by']
          user_gem_link = data_list[i]['link']
          break
      else:
          i += 1

  user_verified_msg = "Yes" if user_verified else "No"

  if user_exists:
    embed = discord.Embed()
    embed.set_author(name=user_name)
    embed.set_thumbnail(url=user_avatar)
    embed.add_field(name="Verified?", value=user_verified_msg, inline=True)
    if user_verified:
      embed.add_field(name="Verified By", value=user_verified_by, inline=True)
    embed.add_field(name="Gem Score Link:", value=user_gem_link, inline=False)
    embed.set_image(url=user_gem_link)
    await ctx.send(embed=embed)
  else:
    if (len(args) < 1):
      await ctx.send("You have not submitted your gem, please use the update command to submit your gem.")
    else:
      await ctx.send("This person has not submitted their gem.")

@verify.error
async def verify_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You have not specified a user you want to verify.')

@unverify.error
async def unverify_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You have not specified a user you want to unverify.')

@update.error
async def update_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You have not specified a link to the gem score picture.')

@bot.command()
async def help(ctx):
  message = "```;update <link> - to record your gem score\n"
  message = message + ";gem - to display your gem score\n"
  message = message + ";gem <user> - to see other people's gem score\n"
  message = message + ";verify - to verify someone's gem (no role checks yet)\n"
  message = message + ";unverify - to unverify someone's gem (no role checks yet)```"
  await ctx.send(message)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

keep_alive()
bot.run(os.getenv('TOKEN'))

# TODO: Add Search by Nickname functionality to gem command (Finished)
# Steps:
# (1) Convert *args to type String
# (2) Join the *args by using space
# (3) Iterate through the list of members in the guild
# (4) Compare the joined argument with member display_names
# (5) If joined argument and display_name matchm, add all caught entries to a dynamic array
# (6) If dynamic array size is greater than 1, display a question to the user about whose gem score they want to see by listing all caught entries by "nickname (discord tag)"
# (7) If dynamic array size is 1, display gem score
# (8) If dynamic array is 0, search by discord tag instead
# (9) If discord tag exists, display gem
# (10) If discord tag doesn't exist, display appropriate error message.

#TODO: Cancel display gem duplicate question after user calls up gem command again