from functions import *
import datetime
import discord
import json

PAGE_SIZE = 5

class GoToPage(discord.ui.Modal):
    def __init__(self, callback):
        super().__init__(title='Go to which page?')
        self.page_input = discord.ui.TextInput(label='Page number')
        self.add_item(self.page_input)
        self.callback = callback # function to call when input form is submitted
    
    async def on_submit(self, i: discord.Interaction):
        await self.callback(i, self.page_input.value)

class Dictionary(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.page = 0
        self.get_dictionary_info()
    
    async def is_original_user(self, i: discord.Interaction):
        if i.user.name != self.user:
            await i.response.send_message('This is not for you.', ephemeral=True)
            print(f'{now()} [{i.user.name}] display: tried to use {self.user}\'s interaction')
            return False
        return True
    
    def get_dictionary_info(self):
        self.dictionary = get_dictionary(self.user)
        self.words = sorted(self.dictionary.keys())
        self.page_count = max(int((len(self.words)-1)/PAGE_SIZE)+1, 1)

    def get_embed(self):
        self.get_dictionary_info()

        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"{self.user}'s Dictionary",
            description = f"*You are viewing your dictionary.*",
            timestamp = datetime.datetime.now()
        )

        if self.words:
            if self.page+1==self.page_count and len(self.words)%PAGE_SIZE!=0:
                num = len(self.words)%PAGE_SIZE
            else:
                num = PAGE_SIZE
            for i in range(num):
                word = self.words[self.page*PAGE_SIZE+i]
                definition = self.dictionary[word]['definition']
                embed.add_field(name=word, value=f'> {definition}', inline=False)
            embed.set_footer(text=f'Page {self.page+1} of {self.page_count}')
        else:
            embed.add_field(name='', value='(You have no words in your dictionary.)')
            embed.set_footer(text='Page 0 of 0')
        
        return embed

    async def send(self, i: discord.Interaction):
        if self.page != 0:
            self.left_button.disabled = False
        if self.page+1 != self.page_count:
            self.right_button.disabled = False
        if self.page == 0:
            self.left_button.disabled = True
        if self.page+1 == self.page_count:
            self.right_button.disabled = True
        if self.page_count<=1:
            self.go_to_page_button.disabled = True
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.original_response = await i.original_response()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='<')
    async def left_button(self, i: discord.Interaction, b: discord.ui.Button):
        if not await self.is_original_user(i):
            return
        await i.response.defer()
        self.page -= 1
        self.get_dictionary_info()
        await self.update()
    
    async def go_to_page(self, i: discord.Interaction, page_number: str):
        try:
            page_number = int(page_number)
            invalid = False
        except:
            # input wasn't a number
            invalid = True
        
        try:
            if invalid or page_number<1 or page_number>self.page_count:
                await i.response.send_message(f'`{page_number}` is not a valid page number.', ephemeral=True)
                print(f'{now()} [{i.user.name}] display: could not jump to page {page_number}')
            else:
                self.page = page_number-1
                self.get_dictionary_info()
                await self.update()
                await i.response.defer()
                print(f'{now()} [{i.user.name}] display: jumped to page {page_number}')
        except Exception as e:
            await error(i, e, 'Dictionary.go_to_page')

    @discord.ui.button(style=discord.ButtonStyle.primary, label='Go to page')
    async def go_to_page_button(self, i: discord.Interaction, b: discord.ui.Button):
        if not await self.is_original_user(i):
            return
        modal = GoToPage(self.go_to_page)
        await i.response.send_modal(modal)
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='>')
    async def right_button(self, i: discord.Interaction, b: discord.ui.Button):
        if not await self.is_original_user(i):
            return
        await i.response.defer()
        self.page += 1
        self.get_dictionary_info()
        await self.update()
    
    async def update(self):
        if self.page != 0:
            self.left_button.disabled = False
        if self.page+1 != self.page_count:
            self.right_button.disabled = False
        if self.page == 0:
            self.left_button.disabled = True
        if self.page+1 == self.page_count:
            self.right_button.disabled = True
        await self.original_response.edit(embed=self.get_embed(), view=self)