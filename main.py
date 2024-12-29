# Shelby

from dotenv import load_dotenv
import datetime
import json
import os

from discord import app_commands
import discord

from dictionary import Dictionary
from edit_word import EditMenu

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

def now():
    # returns current timestamp
    time = datetime.datetime.now()
    date = [time.month, time.day, time.year, time.hour, time.minute, time.second]
    for i in range(len(date)):
        date[i] = str(date[i])
        if len(date[i])==1: date[i] = '0' + date[i]
    return '[{}-{}-{} {}:{}:{}]'.format(*date)

def get_dictionary(user: str):
    try:
        with open(f'dictionaries/{user}.json', 'r') as file:
            return json.load(file)
    except:
        return {}

@client.event
async def on_ready():
    # sync command tree in all guilds
    for guild in client.guilds:
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
    
    # send messages upon starting
    guilds = '\n - '.join([f'{guild.name} (id: {guild.id})' for guild in client.guilds])
    print(f'{client.user} is active in the following guilds:')
    print(f' - {guilds}\n')
    me = client.get_user(587040390603866122)
    await me.send('Yadoyadoking...!')
    print('Shelby sent a DM to doduodrio (id: 587040390603866122) upon activating!\n')

# @client.event
# async def on_message(message):
#     # if it's your own message, don't react
#     if message.author == client.user:
#         return
#     # otherwise, react
#     msg = message.content.lower() # "hElLo!" => "hello!"

@tree.command(description='Add a word to your dictionary')
@app_commands.describe(
    word='The word or phrase to add',
    definition='The definition of the word or phrase being added'
)
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
        print(f'{now()} [{i.user.name}] add_word: word added (word: "{word}", definition: "{definition}")')

@tree.command(description='Display the words in your dictionary')
async def display(i: discord.Interaction):
    dictionary = Dictionary(i.user.name)
    await dictionary.send(i)
    print(f'{now()} [{i.user.name}] display: displayed dictionary')

@tree.command(description='Edit a word in your dictionary')
@app_commands.describe(word='The word or phrase to edit')
async def edit_word(i: discord.Interaction, word: str):
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

client.run(TOKEN)