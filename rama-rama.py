# bot.py
import os
import random
import asyncio

import discord
from dotenv import load_dotenv
from reversi import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
idle = discord.Activity(type=discord.ActivityType.watching, name=";;start")
active = discord.Game(name="wraparound reversi")
animation_delay = .15
#await client.change_presence(activity=activity)



@client.event
async def on_ready():
    #for guild in client.guilds:
    #    if guild.name == GUILD:
    #        break
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    print('Guild members:\n', ', '.join(member.name for member in guild.members))
    await client.change_presence(activity=idle)
    message = await guild.text_channels[0].send("rama-rama is online now")
    await asyncio.sleep(2)
    await message.edit(content="edited")




noisy = True

agentO = Greedy('Bot O')
players = [None ,None]
state = passX = passO = None
history = []
messages = []
# ignoring passO for now

@client.event
async def on_message(message):
    global agentO, players, state, passX, passO, history, messages
    if message.author == client.user:
        return

    if message.content[:2] == ';;':
        inp = message.content[2:].lower()
        if inp == 'start':
            inp = inp[5:].split()
            state = new_reversi_state()
            history = [state]
            passX = passO = False
            player = None  # who sent this?
            messages.append(await message.channel.send('game restarted'
                + "```" + str(state) + "```"))
            players[True] = message.author
            print(message.author)
            await client.change_presence(activity=active)
            return

        if inp == 'undo':
            if len(messages) > 2:
                history = history[:-2]
                state = history[-1]
                passX = passO = False
                print('deleting')
                await message.channel.delete_messages(messages[-2:])
                #await client.delete_message(messages[-1])
                #await client.delete_message(messages[-2])
                messages = messages[:-2]
                return
            else:
                await message.channel.send('No moves to undo!')

        if state is None:
            await message.channel.send('No game is ongoing')
            return
        #if message.author != players[state.turn]:
        #    await message.channel.send('Not your turn')
        #    return
        #if not state.turn is True:
        #    await message.channel.send('Not your turn (you are X)')
        #    return

        print('here1')
        try:
            row, col = map(int, inp.split(","))
        except ValueError:
            await message.channel.send('\tplease enter 2 comma-separated numbers')
            return
        print('here2')
        if row<0 or row>=8 or col<0 or col>=8 or state.board[row][col] is not None: 
            await message.channel.send('\tcell must be empty')
            return
        print('heranimation_delay', row, col)
        state_ = state.make_move(row, col)
        if state_ is None:
            await message.channel.send('\tsomething must flip')
            return
        print('here4', state_)
        oldstate = state
        state = state_
        history.append(state)
        print('here4.5', noisy)
        if noisy:
            print('here5', state_)
            board = [list(row) for row in oldstate.board]
            board[state.previous[0]][state.previous[1]] = oldstate.turn
            interm = ReversiState(board=board, turn=oldstate.turn, winner=oldstate.winner, 
                    terminal=oldstate.terminal, previous=state.previous)
            messages.append(await message.channel.send("```" + str(interm) + "```"))
            for i in range(8):
                for j in range(8):
                    if interm.board[i][j] != state.board[i][j]:
                        interm.board[i][j] = '~'
            await asyncio.sleep(animation_delay)
            await messages[-1].edit(content="```" + str(interm) + "```")

            await asyncio.sleep(animation_delay)
            await messages[-1].edit(content="```" + str(state) + "```")
        if state.terminal:
            O = sum(1 for row in state.board for cell in row if cell is False)
            X = sum(1 for row in state.board for cell in row if cell is True)
            await message.channel.send(f"X has {X:2d} points\n"
                + f"O has {O:2d} points\n"
                + f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
            state = passX = passO = None
            await client.change_presence(activity=idle)

        ## bot O's turn
        #if state.find_children():
        #    passX = False
        #    state = agentO.play(state)
        #    messages.append(await message.channel.send("```" + str(state) + "```"))
        #else:
        #    passX = True
        #    state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
        #    messages.append(await message.channel.send(f"{agentO.name} has to pass, it's your turn\n"))
        #history.append(state)
        #if state.terminal:
        #    O = sum(1 for row in state.board for cell in row if cell is False)
        #    X = sum(1 for row in state.board for cell in row if cell is True)
        #    await message.channel.send(f"X has {X:2d} points\n"
        #        + f"O has {O:2d} points\n"
        #        + f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
        #    state = passX = passO = None
        #    await client.change_presence(activity=idle)
                
    elif message.content == 'raise-exception':
        raise discord.DiscordException

#@client.event
#async def on_error(event, *args, **kwargs):
#    with open('err.log', 'a') as f:
#        if event == 'on_message':
#            f.write(f'Unhandled message: {args[0]}\n')
#        else:
#            raise

client.run(TOKEN)


