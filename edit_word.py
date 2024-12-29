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

class TextInput(discord.ui.Modal):
    def __init__(self, title: str, input_name: str, callback):
        super().__init__(title=title)
        self.input = discord.ui.TextInput(label=input_name)
        self.add_item(self.input)
        self.callback = callback # function to call when input form is submitted
    
    async def on_submit(self, i: discord.Interaction):
        await self.callback(i, self.input.value)

class EditMenu(discord.ui.View):
    def __init__(self, user, word):
        super().__init__()
        self.user = user
        self.word = word
    
    def get_embed(self):
        self.dictionary = get_dictionary(self.user)

        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"Editing {self.user}'s Dictionary",
            description = f"*You are editing* **{self.word}**.",
            timestamp = datetime.datetime.now()
        )
        embed.add_field(name='Word', value=self.word, inline=False)
        embed.add_field(name='Definition', value=self.dictionary[self.word], inline=False)

        return embed
    
    async def send(self, i: discord.Interaction):
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.interaction = i
    
    async def edit_word(self, i: discord.Interaction, new_word: str):
        if new_word in self.dictionary.keys():
            await i.response.send_message(f'The word `{new_word}` already exists in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to change word "{self.word}" to pre-existing word "{new_word}"')
        else:
            await i.response.send_message(f'The word `{self.word}` has been changed to `{new_word}`.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: changed word "{self.word}" to "{new_word}')

            # move old word data to a new key
            old_word = self.dictionary.pop(self.word)
            self.dictionary[new_word] = {
                'word': new_word,
                'definition': old_word['definition'],
                'date added': old_word['date added']
            }
            self.word = new_word

            # update file with new word
            with open(f'dictionaries/{self.user}.json', 'w') as file:
                file.write(json.dumps(self.dictionary, indent=4))
            
            # update original response with new word
            response = await self.interaction.original_response()
            await response.edit(emded=self.get_embed(), view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary, label='Edit Word')
    async def edit_word_button(self, i: discord.Interaction, b: discord.ui.Button):
        modal = TextInput(f'Editing word {self.word}', 'New word', self.edit_word)
        await i.response.send_modal(modal)