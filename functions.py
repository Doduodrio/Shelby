import datetime
import discord
import json

logging = True
t = datetime.datetime.now()
logtime = '{}-{}-{}_{}.{}.{}'.format(*[t.year, t.month, t.day, t.hour, t.minute, t.second])

# override the default print function!
print_copy = print
def print(*args, **kwargs):
    print_copy(*args, **kwargs)
    if not logging:
        return
    # log_2025-01-01_00.00.00.txt
    with open(f'logs/log_{logtime}.txt', 'a') as file:
        print_copy(*args, file=file, **kwargs)

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