from functions import *
import datetime
import discord
import json

class WordEditor(discord.ui.Modal):
    def __init__(self, word: str, definition: str, callback):
        if len(word)>29:
            super().__init__(title=f'Editing word {word[0:29]}...')
        else:
            super().__init__(title=f'Editing word {word}')
        self.word_input = discord.ui.TextInput(label='Word', default=word, max_length=100)
        self.add_item(self.word_input)
        self.definition_input = discord.ui.TextInput(label='Definition', default=definition, style=discord.TextStyle.paragraph, max_length=256)
        self.add_item(self.definition_input)
        self.callback = callback # function to call when input form is submitted
    
    async def on_submit(self, i: discord.Interaction):
        await self.callback(i, self.word_input.value, self.definition_input.value)

class DeleteWordConfirmation(discord.ui.View):
    def __init__(self, word, delete_word):
        super().__init__(timeout=None)
        self.word = word
        self.delete_word = delete_word
    
    def get_embed(self):
        embed = discord.Embed(
            title = 'Pending Confirmation',
            description = f'Are you sure you want to delete `{self.word}` from your dictionary?'
        )
        embed.add_field(name='', value='**WARNING:** This CANNOT be undone.')
        return embed

    async def send(self, i: discord.Interaction):
        await i.response.send_message(embed=self.get_embed(), view=self, ephemeral=True)
        self.original_response = await i.original_response()
    
    @discord.ui.button(style=discord.ButtonStyle.danger, label='Cancel')
    async def cancel_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        await self.original_response.delete()
    
    @discord.ui.button(style=discord.ButtonStyle.success, label='Confirm')
    async def confirm_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        await self.original_response.delete()
        await self.delete_word(i)

class EditMenu(discord.ui.View):
    def __init__(self, user, word):
        super().__init__(timeout=None)
        self.user = user
        self.word = word

    async def is_original_user(self, i: discord.Interaction):
        if i.user.name != self.user:
            await i.response.send_message('This is not for you.', ephemeral=True)
            print(f'{now()} [{i.user.name}] display: tried to use {self.user}\'s interaction')
            return False
        return True
    
    def get_embed(self):
        self.dictionary = get_dictionary(self.user)
        try:
            self.definition = self.dictionary[self.word]['definition']
        except:
            pass

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
        self.interaction = i
    
    async def edit_word(self, i: discord.Interaction, new_word: str, new_definition: str):
        # load dictionary data
        self.dictionary = get_dictionary(self.user)
        try:
            self.definition = self.dictionary[self.word]['definition']
        except:
            # word doesn't exist (could be deleted somehow)
            await i.response.send_message(f'The word `{self.word}` could not be found in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to edit word "{self.word}" but it could not be found')
            
            # disable buttons because word no longer exists
            self.edit_word_button.disabled = True
            self.delete_word_button.disabled = True
            original_response = await self.interaction.original_response()
            await original_response.edit(embed=self.get_embed(), view=self)
            return

        if new_word in self.dictionary.keys() and new_word != self.word:
            # two words cannot share the same key
            await i.response.send_message(f'The word `{new_word}` already exists in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to edit word "{self.word}" to pre-existing word "{new_word}"')
        elif len(new_word)>100:
            await i.response.send_message(f'The word `{new_word}` is too long.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: word was too long (word: "{new_word}", definition: "{new_definition}")')
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
            original_response = await self.interaction.original_response()
            await original_response.edit(embed=self.get_embed(), view=self)

            # send confirmation message
            await i.response.send_message('Your changes have been saved.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: edited word "{self.word}"')
            print(f'    old: "{old_word["word"]}" with definition "{old_word["definition"]}"')
            print(f'    new: "{new_word}" with definition "{new_definition}"')

    @discord.ui.button(style=discord.ButtonStyle.primary, label='Edit Word')
    async def edit_word_button(self, i: discord.Interaction, b: discord.ui.Button):
        if not await self.is_original_user(i):
            return

        # load dictionary data
        self.dictionary = get_dictionary(self.user)
        try:
            self.definition = self.dictionary[self.word]['definition']
        except:
            # word doesn't exist (could be deleted somehow)
            await i.response.send_message(f'The word `{self.word}` could not be found in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to edit word "{self.word}" but it could not be found')
            
            # disable buttons because word no longer exists
            self.edit_word_button.disabled = True
            self.delete_word_button.disabled = True
            original_response = await self.interaction.original_response()
            await original_response.edit(embed=self.get_embed(), view=self)
            return
        
        modal = WordEditor(self.word, self.dictionary[self.word]['definition'], self.edit_word)
        await i.response.send_modal(modal)
    
    async def delete_word(self, i: discord.Interaction):
        # load dictionary data
        self.dictionary = get_dictionary(self.user)
        
        # delete word from dictionary and update file
        try:
            self.dictionary.pop(self.word)
        except:
            # word doesn't exist (could be deleted somehow)
            await self.interaction.followup.send(f'The word `{self.word}` could not be found in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to delete word "{self.word}" but it could not be found')

            # disable buttons because word no longer exists
            self.edit_word_button.disabled = True
            self.delete_word_button.disabled = True
            original_response = await self.interaction.original_response()
            await original_response.edit(embed=self.get_embed(), view=self)
            return
        
        with open(f'dictionaries/{self.user}.json', 'w') as file:
            file.write(json.dumps(self.dictionary, indent=4))

        # update original response
        self.edit_word_button.disabled = True
        self.delete_word_button.disabled = True
        original_response = await self.interaction.original_response()
        await original_response.edit(embed=self.get_embed(), view=self)
        await self.interaction.followup.send(f'The word `{self.word}` has been deleted from your dictionary.', ephemeral=True)
        print(f'{now()} [{i.user.name}] edit_word: deleted word (word: "{self.word}")')
        print(f'    word: "{self.word}" with definition "{self.definition}"')
    
    @discord.ui.button(style=discord.ButtonStyle.danger, label='Delete Word')
    async def delete_word_button(self, i: discord.Interaction, b: discord.ui.Button):
        if not await self.is_original_user(i):
            return
        
        # load dictionary data
        self.dictionary = get_dictionary(self.user)
        try:
            self.definition = self.dictionary[self.word]['definition']
        except:
            # word doesn't exist (could be deleted somehow)
            await i.response.defer()
            await self.interaction.followup.send(f'The word `{self.word}` could not be found in your dictionary.', ephemeral=True)
            print(f'{now()} [{i.user.name}] edit_word: tried to delete word "{self.word}" but it could not be found')

            # disable buttons because word no longer exists
            self.edit_word_button.disabled = True
            self.delete_word_button.disabled = True
            original_response = await self.interaction.original_response()
            await original_response.edit(embed=self.get_embed(), view=self)
            return

        confirmation = DeleteWordConfirmation(self.word, self.delete_word)
        await confirmation.send(i)