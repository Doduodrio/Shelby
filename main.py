# Shelby

from dotenv import load_dotenv
from unidecode import unidecode
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
    # sync command tree globally (global)
    await tree.sync(guild=None)

    # sync command tree in all guilds (local)
    # for guild in client.guilds:
    #     tree.copy_global_to(guild=guild)
    #     await tree.sync(guild=guild)
    
    # clear command tree in all guilds
    # for guild in client.guilds:
    #     tree.clear_commands(guild=guild)
    #     await tree.sync(guild=guild)
    
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
    
    try:
        # add word to dictionary
        if word in dictionary:
            await i.response.send_message(f'The word `{word}` already exists in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] add_word: word already exists (word: "{word}", definition: "{definition}")')
        elif len(word)>100:
            await i.response.send_message(f'The word `{word}` is too long (must be 100 characters or less).', ephemeral=True)
            print(f'{now()} [{i.user.name}] add_word: word was too long (word: "{word}", definition: "{definition}")')
        elif len(definition)>256:
            await i.response.send_message(f'The definition `{definition}` is too long (must be 256 characters or less).', ephemeral=True)
            print(f'{now()} [{i.user.name}] add_word: definition was too long (word: "{word}", definition: "{definition}")')
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
    except Exception as e:
        await error(i, e, 'add_word')

@tree.command(description='Display the words in your dictionary')
async def display(i: discord.Interaction):
    try:
        dictionary = Dictionary(i.user.name)
        await dictionary.send(i)
        print(f'{now()} [{i.user.name}] display: displayed dictionary')
    except Exception as e:
        await error(i, e, 'display')

@tree.command(description='Edit a word in your dictionary')
@app_commands.describe(word='The word or phrase to edit')
async def edit_word(i: discord.Interaction, word: str):
    dictionary = get_dictionary(i.user.name)
    try:
        if word not in dictionary:
            await i.response.send_message(f'The word `{word}` could not be found.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to edit word "{word}" but it could not be found')
        else:
            edit_menu = EditMenu(i.user.name, word)
            await edit_menu.send(i)
            print(f'{now()} [{i.user.name}] edit_word: editing word (word: "{word}")')
    except Exception as e:
        await error(i, e, 'edit_word')
@edit_word.autocomplete('word')
async def edit_word_autocomplete(i: discord.Interaction, current: str):
    current = current.lower()
    dictionary = get_dictionary(i.user.name)
    choices = []
    for word in sorted(dictionary.keys()):
        word_ = unidecode(word)
        if current in word.lower() or current in word_.lower():
            if len(word)>100:
                choices.append(app_commands.Choice(name=word[0:100], value=word[0:100]))
            else:
                choices.append(app_commands.Choice(name=word, value=word))
    if len(choices) > 25:
        choices = choices[0:25]
    return choices

@tree.command(description='Review some words from your dictionary (definitions hidden)')
@app_commands.describe(number='The number of words you want to review')
async def review_words(i: discord.Interaction, number: str):
    dictionary = get_dictionary(i.user.name)
    try:
        num = int(number)
        invalid = False
    except:
        # input wasn't a number
        invalid = True
    try:
        if invalid or num == 0 or num > len(dictionary.keys()):
            await i.response.send_message(f'`{number}` is not a valid number of words to review.', ephemeral=True)
            print(f'{now()} [{i.user.name}] review_words: tried to review invalid number of words (number: {number})')
        else:
            review_menu = Review('word', i.user.name, num)
            await review_menu.send(i)
            print(f'{now()} [{i.user.name}] review_words: reviewed {number} words from the dictionary')
            print('    words:', ', '.join(list(review_menu.review_words.keys())))
    except Exception as e:
        await error(i, e, 'review_words')

@tree.command(description='Review some definitions from your dictionary (words hidden)')
@app_commands.describe(number='The number of definitions you want to review')
async def review_definitions(i: discord.Interaction, number: str):
    dictionary = get_dictionary(i.user.name)
    try:
        num = int(number)
        invalid = False
    except:
        # input wasn't a number
        invalid = True
    try:
        if invalid or num == 0 or num > len(dictionary.keys()):
            await i.response.send_message(f'`{number}` is not a valid number of definitions to review.', ephemeral=True)
            print(f'{now()} [{i.user.name}] review_definitions: tried to review invalid number of definitions (number: {number})')
        else:
            review_menu = Review('definition', i.user.name, num)
            await review_menu.send(i)
            print(f'{now()} [{i.user.name}] review_definitions: reviewed {number} definitions from the dictionary')
            print('    definitions of:', ', '.join(list(review_menu.review_words.keys())))
    except Exception as e:
        await error(i, e, 'review_definitions')

@tree.command(description='Display a list of all commands with descriptions')
async def help(i: discord.Interaction):
    embed = discord.Embed(
        color = discord.Color.dark_teal(),
        title = 'Help Menu',
        description = '*You are viewing a list of all commands.*',
        timestamp = datetime.datetime.now()
    )
    embed.add_field(name='display', value='> Display all of the words in your dictionary. Use the "Go to page" button to jump to any page immediately.', inline=False)
    embed.add_field(name='add_word', value='> Add a word to your dictionary. (100 characters max for words, 256 characters max for definitions, and no duplicate words.)', inline=False)
    embed.add_field(name='edit_word', value='> Bring up a menu to edit or delete the selected word. Remember, deleting a word is permanent, and if you want it back, you\'ll have to add it back yourself.', inline=False)
    embed.add_field(name='review_words', value='> Review a random selection of words from your dictionary with the words shown and the definitions hidden.', inline=False)
    embed.add_field(name='review_definitions', value='> Review a random selection of words from your dictionary with the words hidden and the definitions shown.', inline=False)

    await i.response.send_message(embed=embed)
    print(f'{now()} [{i.user.name}] help: used the help command')

client.run(TOKEN)