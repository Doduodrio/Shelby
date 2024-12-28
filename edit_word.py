import datetime
import discord
import json

def get_dictionary(user):
    try:
        with open(f'dictionaries/{user}.json', 'r') as file:
            return json.load(file)
    except:
        return {}

class EditWord(discord.ui.View):
    def __init__(self):
        pass