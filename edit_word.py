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

class WordEditor(discord.ui.Modal):
    def __init__(self, word: str, definition: str, callback):
        super().__init__(title=f'Editing word {word}')
        self.word_input = discord.ui.TextInput(label='Word', default=word)
        self.add_item(self.word_input)
        self.definition_input = discord.ui.TextInput(label='Definition', default=definition)
        self.add_item(self.definition_input)
        self.callback = callback # function to call when input form is submitted
    
    async def on_submit(self, i: discord.Interaction):
        await self.callback(i, self.word_input.value, self.definition_input.value)

class EditMenu(discord.ui.View):
    def __init__(self, user, word):
        super().__init__()
        self.user = user
        self.word = word
    
    def get_embed(self):
        self.dictionary = get_dictionary(self.user)
        self.definition = self.dictionary[self.word]['definition']

        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"Editing {self.user}'s Dictionary",
            description = f"*You are editing* **{self.word}**.",
            timestamp = datetime.datetime.now()
        )
        embed.add_field(name='Word', value=self.word, inline=False)
        embed.add_field(name='Definition', value=self.definition, inline=False)

        return embed
    
    async def send(self, i: discord.Interaction):
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.original_response = await i.original_response()
    
    async def edit_word(self, i: discord.Interaction, new_word: str, new_definition: str):
        if new_word in self.dictionary.keys() and new_word != self.word:
            # two words cannot share the same key
            await i.response.send_message(f'The word `{new_word}` already exists in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to change word "{self.word}" to pre-existing word "{new_word}"')
        else:
            # delete old entry and make new entry with new data
            old_word = self.dictionary.pop(self.word)
            self.dictionary[new_word] = {
                'word': new_word,
                'definition': new_definition,
                'date added': old_word['date added']
            }
            self.word = new_word
            self.definition = new_definition

            # update file with new data
            with open(f'dictionaries/{self.user}.json', 'w') as file:
                file.write(json.dumps(self.dictionary, indent=4))
            
            # update original response with new data
            await self.original_response.edit(embed=self.get_embed(), view=self)

            # send confirmation message
            await i.response.send_message(f'Your changes have been saved.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: changed word')
            print(f'    old: "{old_word["word"]}" with definition "{old_word["definition"]}"')
            print(f'    new: "{new_word}" with definition "{new_definition}"')

    @discord.ui.button(style=discord.ButtonStyle.primary, label='Edit Word')
    async def edit_word_button(self, i: discord.Interaction, b: discord.ui.Button):
        modal = WordEditor(self.word, self.dictionary[self.word]['definition'], self.edit_word)
        await i.response.send_modal(modal)
    
    async def delete_word(self, i: discord.Interaction):
        pass
    
    @discord.ui.button(style=discord.ButtonStyle.danger, label='Delete Word')
    async def delete_word_button(self, i: discord.Interaction, b: discord.ui.Button):
        pass