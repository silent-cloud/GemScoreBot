import discord
import logging
import json
import validators
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

token = None
with open("info.txt", "r") as info_data:
    token = info_data.readline()

bot = commands.Bot(command_prefix=';')


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
                data_list[i]['verified_by'] = str(ctx.author) + " (" + ctx.author.display_name + ")"
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
async def gem(ctx):
    user_name = str(ctx.author) + " (" + ctx.author.display_name + ")"
    user_avatar = str(ctx.author.avatar_url)
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
        if data_list[i]['user'] == str(ctx.author):
            user_exists = True
            user_verified = data_list[i]['is_verified']
            user_verified_by = data_list[i]['verified_by']
            user_gem_link = data_list[i]['link']
            break
        else:
            i += 1

    if user_verified:
        user_verified_msg = "Yes"
    else:
        user_verified_msg = "No"

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
        await ctx.send("You have not submitted your gem, please use the update command to submit your gem.")


# TODO Gem command with user

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


bot.run(token)