# libraries used belong to their owners
import asyncio
import datetime
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='@', intents=discord.Intents.all(), case_insensitive=True,
                   description="It looks like your server needs some freedom...")

try:
    inp = open('DB_input.txt', 'r')
except FileNotFoundError:
    inp = open('DB_input.txt', 'x')
    import sys
    sys.exit(74)

try:
    ipt = open('DB_mintime.txt', 'r')
except FileNotFoundError:
    ipt = open('DB_mintime.txt', 'x')
    import sys
    sys.exit(74)

tok = inp.read()
inp.close()
if tok == '[Erase all and paste the token here]':
    import sys
    sys.exit(74)

mnt = list(ipt)
mtc = int(mnt[0])
mtm = mnt[1]
if (mtc != int) or (mtm != any(('week', 'day', 'hour'))):
    import sys
    sys.exit(74)

emo = [':white_check_mark:', ':x:']  # GUI reactions list 1 - agree; 2 - disagree
idl = []
mts = int


# mfs stole the real goto
# can`t have shit in Python
async def goto(ln):
    global line
    line = ln


@bot.command()
async def helpcmd(ctx):
    await ctx.send('@newVote action object time-weeks time-days time-hours time-minutes'
                   'addparam1 addparam2 addparam3'
                   '\nCommands: ban @MEMBER time-voting(4) PERMAMENT(True/False) REASON TIME-BAN-DAYS'
                   '\nunban @MEMBER time-voting(4)'
                   '\n kick @MEMBER time-voting(4) REASON'
                   '\n timeout @MEMBER time-voting(4) REASON TIME-TIMEOUT-WEEKS TIME-TIMEOUT-DAYS'
                   '\n giverole @MEMBER time-voting(4) @ROLE'
                   '\n removerole @MEMBER time-voting(4) @ROLE')


async def newVote(ctx):
    global emo
    global idl
    if ctx.content.startswith("@newVote"):
        params = ctx.content.split(' ')
        act = params[1].strip()
        obj = params[2].strip()
        tmw = params[3].strip()
        tmd = params[4].strip()
        tmh = params[5].strip()
        tmm = params[6].strip()
        ap1 = params[7].strip()
        ap2 = params[8].strip()
        ap3 = params[9].strip()

        if any((act, obj, all((tmw, tmd, tmh, tmm)))) is None:
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif act != any(('ban', 'unban', 'kick', 'timeout', 'giverole', 'removerole')):
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif all((tmw, tmd, tmh, tmm)) != int:
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif (act == 'ban') and (ap1 != ('True' or 'False')):
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif (act == 'ban') and ((ap1 == 'False') and ((ap3 != int) or (ap3 == 0))):
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif (act == 'timeout') and (((ap2 != int) or (ap2 == 0)) and ((ap3 != int) or (ap3 == 0))):
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)
        elif ((act == 'giverole') or (act == 'removerole')) and ap1 is None:
            await ctx.send('Parameters missing/incorrect.')
            helpcmd(ctx)

        else:
            emb = discord.Embed(title=f'VOTING: {act} {obj}',
                                description=f'Initiated by {ctx.author}'
                                            f'\n{act} {obj} {ap1} {ap2} {ap3}'
                                            f'\nWeeks: {tmw}; days: {tmd}; hours: {tmh}; minutes: {tmm}'
                                            f'\nRemaining time: [TIME]',
                                color=0x12ff51)
            snt = await ctx.channel.send(emb)

            await snt.add_reaction(emo[0])
            await snt.add_reaction(emo[1])

            idl.append(snt.id)

            end = datetime.datetime.utcnow() + datetime.timedelta(weeks=tmw, days=tmd, hours=tmh, minutes=tmm)
            rmt = (end - datetime.datetime.utcnow()).total_seconds()

            async def rmu():
                global rmt
                global snt
                if rmt > 0:
                    await asyncio.sleep(1)
                    rmt -= 1
                    emb = discord.Embed(title=f'VOTING: {act} {obj}',
                                        description=f'Initiated by {ctx.author}'
                                                    f'\n{act} {obj} {ap1} {ap2} {ap3}'
                                                    f'\nWeeks: {tmw}; days: {tmd}; hours: {tmh}; minutes: {tmm}'
                                                    f'\nRemaining time: {rmt}',
                                        color=0x12ff51)
                    await snt.edit(embed=emb)
                    return False

                else:
                    snt = await ctx.channel.fetch_message(snt.id)

                    vrc = {}
                    trc = 0

                    for reaction in snt.reactions:
                        for ind, emoji in enumerate(emo):
                            if reaction.emoji == emoji:
                                vrc[ind] = reaction.count - 1
                                if reaction.count > 1:
                                    trc += 1

                    acp = bool
                    if (vrc.get(emo[0]) >= vrc.get(emo[1])) and (trc >= (ctx.guild.member_count * 0.5)):
                        if act == 'ban':
                            eta = datetime.datetime.utcnow() + datetime.timedelta(days=ap3)
                            rta = (eta - datetime.datetime.utcnow()).total_seconds()
                            member = obj
                            await member.ban(duration=rta, reason=ap2)
                        elif act == 'unban':
                            user = obj
                            await ctx.guild.unban(user)
                        elif act == 'kick':
                            user = obj
                            await user.kick(reason=ap1)
                        elif act == 'timeout':
                            eta = datetime.datetime.utcnow() + datetime.timedelta(weeks=ap2, days=ap3)
                            rta = (eta - datetime.datetime.utcnow()).total_seconds()
                            member = obj
                            await member.timeout(duration=rta, reason=ap1)
                        elif act == 'giverole':
                            user = obj
                            await user.add_roles(user, ap1)
                        elif act == 'removerole':
                            user = obj
                            await user.remove_roles(user, ap1)
                        else:
                            await ctx.send('Error: action not identified.')
                            acp = False
                            flr = 'Error: action not identified.'
                        acp = True
                        flr = None
                    else:
                        acp = False
                        flr = 'Not enough members voted. Minimum: 50%'

                    vre = discord.Embed(title=f'VOTING: {act} {obj}',
                                        description=f'Initiated by {ctx.author}'
                                                    f'\n{act} {obj} {ap1} {ap2} {ap3}'
                                                    f'\nWeeks: {tmw}; days: {tmd}; hours: {tmh}; minutes: {tmm}'
                                                    f'\nRemaining time: 0 (FINISHED)'
                                                    f'\nTotal votes: {trc}'
                                                    f'\nAgreed: {vrc.get(emo[0])}'
                                                    f'\nDisagreed: {vrc.get(emo[1])}'
                                                    f'\n{(vrc.get(emo[0]))/trc} have agreed'
                                                    f'\nAccepted: {acp}'
                                                    f'\n{flr}',
                                        color=0x12ff51)
                    await ctx.channel.send(embed=vre)

            loop = asyncio.get_event_loop()
            loop.run_until_complete(rmu())
            if rmt >= 0:
                await goto(167)

    @bot.event
    async def on_raw_reaction_add(payload):
        global mtc, mts
        global mtm
        global idl
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = message.guild
        member = await guild.fetch_member(payload.user_id)

        if payload.member.bot:
            return
        if mtm == 'week':
            mts = mtc * 604800
        elif mtm == 'day':
            mts = mtc * 86400
        elif mtm == 'hour':
            mts = mtc * 3600
        mja = payload.member.joined_at()
        mja.replace('-', ' ')
        mja.replace(':', ' ')
        mja.replace('.', ' ')
        jal = mja.split(sep=' ')
        # change the 52 to 52.1428571 for better accuracy
        # change the 4 to 4.3452381 for better accuracy
        tbn = (datetime.datetime.utcnow() - datetime.timedelta(weeks=((jal[0] * 52) + (jal[1] * 4)),
                                                               days=jal[2], hours=jal[3],
                                                               minutes=jal[4], seconds=jal[5])).total_seconds()
        if tbn < mts:
            await message.remove_reaction(payload.emoji.name, member)
            await ctx.send(f'Twink account protection system: minimum time is {mtc} {mtm}')
            return

        sbb = False
        for i in idl:
            if i == message.id:
                sbb = True
                break
        if not sbb:
            return

        if payload.emoji.name not in emo:
            await message.remove_reaction(payload.emoji.name, member)
            return

        urc = 0
        for r in message.reactions:
            async for u in r.users():
                if u.id == payload.user_id:
                    urc += 1
                    if urc > 1:
                        await message.remove_reaction(payload.emoji.name, member)
                        break


bot.run(tok)
