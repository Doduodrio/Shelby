import datetime
import discord
import json

PAGE_SIZE = 5

def get_dictionary(user):
    try:
        with open(f'dictionaries/{user}.json', 'r') as file:
            return json.load(file)
    except:
        return {}

class Dictionary(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
        self.page = 0
        self.get_dictionary_info()
    
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
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.original_response = await i.original_response()

    @discord.ui.button(style=discord.ButtonStyle.primary, label='<')
    async def left_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        self.page -= 1
        self.get_dictionary_info()
        await self.update()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='>')
    async def right_button(self, i: discord.Interaction, b: discord.ui.Button):
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