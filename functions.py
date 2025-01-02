import datetime
import discord
import json

def now():
    # returns current timestamp
    time = datetime.datetime.now()
    date = [time.month, time.day, time.year, time.hour, time.minute, time.second]
    for i in range(len(date)):
        date[i] = str(date[i])
        if len(date[i])==1: date[i] = '0' + date[i]
    return '[{}-{}-{} {}:{}:{}]'.format(*date)

def get_dictionary(user):
    try:
        with open(f'dictionaries/{user}.json', 'r') as file:
            return json.load(file)
    except:
        return {}

async def error(i: discord.Interaction, e: Exception, location: str):
    await i.response.send_message(f'Something went wrong.', ephemeral=True)
    print(f'[ERROR] {now()} [{i.user.name}] display: an error occured in {location} (error: {e})')