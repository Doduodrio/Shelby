# Shelby

from dotenv import load_dotenv
import datetime
import json
import os

from discord import app_commands
import discord

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
    word='The word or phrase to add.',
    definition='The definition of the word or phrase being added.'
)
async def add_word(i: discord.Interaction, word: str, definition: str):
    # load pre-existing words from file
    try:
        with open(f'{i.user.name}.json', 'r') as file:
            dictionary = json.load(file)
    except:
        dictionary = {}
    
    # add word to dictionary
    if word in dictionary:
        await i.response.send_message(f'The word `{word}` already exists in your dictionary.')
        print(f'{now()} [{i.user.name}] add_word: word already exists ({word}, {definition})')
    else:
        dictionary[word] = [definition]
        # update file with new word
        with open(f'{i.user.name}.json', 'w') as file:
            file.write(json.dumps(dictionary, indent=4))
        await i.response.send_message(f'The word `{word}` has been added to your dictionary!`', ephemeral=True)
        print(f'{now()} [{i.user.name}] add_word: word added ({word}, {definition})')

@tree.command(description='Display the words in your dictionary')
async def display(i: discord.Interaction):
    pass

client.run(TOKEN)