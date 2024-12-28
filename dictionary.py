import datetime
import discord
import json

PAGE_SIZE = 5

class Dictionary(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.page = 0
    
    def get_dictionary_info(self):
        try:
            with open(f'dictionaries/{self.user}.json', 'r') as file:
                self.dictionary = json.load(file)
        except:
            self.dictionary = {}
        self.words = sorted(self.dictionary.keys())
        self.page_count = max(int((len(self.words)-1)/PAGE_SIZE)+1, 1)

    def get_embed(self):
        self.get_dictionary_info()
        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"{self.user}'s Dictionary",
            description = f"*This is {self.user}'s dictionary.*",
            timestamp = datetime.datetime.now()
        )
        for i in range((min(self.page*PAGE_SIZE, len(self.words)%PAGE_SIZE)-1)%PAGE_SIZE+1):
            word = self.words[self.page*PAGE_SIZE+i]
            definition = self.dictionary[word]
            embed.add_field(name=word, value=f'> {definition}', inline=False)
        embed.set_footer(text=f'Page {self.page+1} of {self.page_count}')
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