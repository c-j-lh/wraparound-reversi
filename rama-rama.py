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
            state = new_reversi_state()
            history = [state]
            passX = passO = False
            player = None  # who sent this?
            messages.append(await message.channel.send('game restarted'
                + "```" + str(state) + "```"))
            players[True] = message.author
            print(message.author)
            return

        if inp == 'undo':
            if len(messages) > 2:
                history = history[:-2]
                state = history[-1]
                passX = passO = False
                print('deleting')
                client.delete_message(messages[-1])
                client.delete_message(messages[-2])
                messages = messages[:-2]
                return

        if state is None:
            await message.channel.send('No game is ongoing')
            return
        if message.author != players[state.turn]:
            await message.channel.send('Not your turn')
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
        print('here3', row, col)
        state_ = state.make_move(row, col)
        if state_ is None:
            await message.channel.send('\tsomething must flip')
            return
        print('here4', state_)
        state = state_
        history.append(state)
        print('here4.5', noisy)
        if noisy:
            print('here5', state_)
            await messages.append(message.channel.send("```" + str(state) + "```"))
        if state.terminal:
            state = passX = passO = None
            O = sum(1 for row in state.board for cell in row if cell is False)
            X = sum(1 for row in state.board for cell in row if cell is True)
            await message.channel.send(f"X has {X:2d} points"
                + f"O has {O:2d} points"
                + f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")

        # bot O's turn
        if state.find_children():
            passX = False
            state = agentO.play(state)
            await messages.append(message.channel.send("```" + str(state) + "```"))
        else:
            passX = True
            state = ReversiState(state.board, not state.turn, state.winner, state.terminal)
            await messages.append(message.channel.send(f"{agentO.name} has to pass, it's your turn\n"))
        history.append(state)
        if state.terminal:
            state = passX = passO = None
            O = sum(1 for row in state.board for cell in row if cell is False)
            X = sum(1 for row in state.board for cell in row if cell is True)
            message.channel.send(f"X has {X:2d} points"
                + f"O has {O:2d} points"
                + f"{'X' if X>O else 'O'} won by {abs(X-O)} points!")
                
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
