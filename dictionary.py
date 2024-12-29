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
        super().__init__()
        self.user = user
        self.page = 0
    
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
            for i in range((min(self.page*PAGE_SIZE, len(self.words)%PAGE_SIZE)-1)%PAGE_SIZE+1):
                word = self.words[self.page*PAGE_SIZE+i]
                definition = self.dictionary[word]['definition']
                embed.add_field(name=word, value=f'> {definition}', inline=False)
            embed.set_footer(text=f'Page {self.page+1} of {self.page_count}')
        else:
            embed.add_field(name='', value='(You have no words in your dictionary.)')
            embed.set_footer(text='Page 0 of 0')
        
        return embed

    async def send(self, i: discord.Interaction):
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.message = await i.original_response()

    @discord.ui.button(style=discord.ButtonStyle.primary, label='<')
    async def left_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        if self.page != (self.page-1)%self.page_count:
            self.page = (self.page-1)%self.page_count
            await self.message.edit(embed=self.get_embed(), view=self)
        else:
            self.get_dictionary_info()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='>')
    async def right_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        if self.page != (self.page+1)%self.page_count:
            self.page = (self.page+1)%self.page_count
            await self.message.edit(embed=self.get_embed(), view=self)
        else:
            self.get_dictionary_info()