# Shelby

from dotenv import load_dotenv
import datetime
import json
import os

from discord import app_commands
import discord

from functions import *
from dictionary import Dictionary
from edit_word import EditMenu
from review import Review

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN') # add the bot token in a .env file

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(
    activity=discord.Game(name='Pokémon Silver'),
    intents=intents
)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    # sync command tree in all guilds
    for guild in client.guilds:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    await tree.sync()
    
    # send messages upon starting
    guilds = '\n - '.join([f'{guild.name} (id: {guild.id})' for guild in client.guilds])
    print(f'{client.user} is active in the following guilds:')
    print(f' - {guilds}\n')
    me = client.get_user(587040390603866122)
    await me.send('Yadoyadoking...!')
    print('Shelby sent a DM to doduodrio (id: 587040390603866122) upon activating!\n')

@tree.command(description='Add a word to your dictionary')
@app_commands.describe(word='The word or phrase to add', definition='The definition of the word or phrase being added')
async def add_word(i: discord.Interaction, word: str, definition: str):
    # load pre-existing words from file
    dictionary = get_dictionary(i.user.name)
    
    # add word to dictionary
    if word in dictionary:
        await i.response.send_message(f'The word `{word}` already exists in your dictionary.', ephemeral=True)
        print(f'{now()} [{i.user.name}] add_word: word already exists (word: "{word}", definition: "{definition}")')
    else:
        dictionary[word] = {
            'word': word,
            'definition': definition,
            'date added': datetime.datetime.now().isoformat(' ')
        }
        # update file with new word
        with open(f'dictionaries/{i.user.name}.json', 'w') as file:
            file.write(json.dumps(dictionary, indent=4))
        await i.response.send_message(f'The word `{word}` has been added to your dictionary!', ephemeral=True)
        print(f'{now()} [{i.user.name}] add_word: added word {word}')
        print(f'    word: "{word}" with definition "{definition}"')

@tree.command(description='Display the words in your dictionary')
async def display(i: discord.Interaction):
    dictionary = Dictionary(i.user.name)
    await dictionary.send(i)
    print(f'{now()} [{i.user.name}] display: displayed dictionary')

@tree.command(description='Edit a word in your dictionary')
@app_commands.describe(word='The word or phrase to edit')
async def edit_word(i: discord.Interaction, word: str):
    dictionary = get_dictionary(i.user.name)
    if word not in dictionary:
        await i.response.send_message(f'The word `{word}` could not be found.', ephemeral=True)
        print(f'{now()} [{i.user.name}] edit_word: tried to edit word "{word}" but it could not be found')
    else:
        edit_menu = EditMenu(i.user.name, word)
        await edit_menu.send(i)
        print(f'{now()} [{i.user.name}] edit_word: editing word (word: "{word}")')
@edit_word.autocomplete('word')
async def edit_word_autocomplete(i: discord.Interaction, current: str):
    dictionary = get_dictionary(i.user.name)
    choices = []
    for word in sorted(dictionary.keys()):
        if current.lower() in word.lower():
            choices.append(app_commands.Choice(name=word, value=word))
    return choices

@tree.command(description='Review some words from your dictionary')
@app_commands.describe(number='The number of words you want to review')
async def review(i: discord.Interaction, number: str):
    try:
        num = int(number)
    except:
        pass # fill in later
    review_menu = Review(number)

client.run(TOKEN)