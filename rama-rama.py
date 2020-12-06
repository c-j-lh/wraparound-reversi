# bot.py
import os
import random

import discord
from dotenv import load_dotenv
from reversi import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()



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


    O = sum(1 for row in state.board for cell in row if cell is False)
    X = sum(1 for row in state.board for cell in row if cell is True)
    if noisy:
        print(f"X has {X:2d} points")
        print(f"O has {O:2d} points")
        print(f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
    return X-O

state = new_reversi_state()
noisy = True
if noisy: print(state)
passX = passO = False
agentO = Greedy('Bot O')
player = None

count = 0

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content[:2] == '::':
        inp = message.content[2:]
        global count
        if inp == 'start':
            count = 0
            await message.channel.send('game restarted')
            return

        try:
            print('befro')
            inp = int(inp)
            print('past')
        except ValueError:
            print('not int')
            return
        count += inp
        await message.channel.send(f"count is now {count}")

        count += 5
        await message.channel.send(f"comp played. count is now {count}")
        ## X's turn
        #if state.find_children():
        #    passX = False
        #    state = 
        #    if noisy: print(state)
        #else:
        #    passX = True
        #    state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
        #    if noisy: print(f"{agentX.name} has to pass, it's your turn\n")
        #if state.terminal:
        #    break

        ## O's turn
        #if state.find_children():
        #    passO = False
        #    state = agentO.play(state)
        #    if noisy: print(state)
        #else:
        #    passO = True
        #    state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
        #    if noisy: print(f"{agentO.name} has to pass, it's your turn\n")
        #if state.terminal:
        #    print('game finished')
        #    state = new_reversi_state()
        #    passX = passO = False

        await message.channel.send("Ok. Starting...")
    elif message.content == 'raise-exception':
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)
