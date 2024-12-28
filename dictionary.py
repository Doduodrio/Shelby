import datetime
import discord
import json

class Dictionary(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        try:
            with open(f'{user}.json', 'r') as file:
                self.dictionary = json.load(file)
        except:
            self.dictionary = {}
        self.words = sorted(self.dictionary.keys())
        self.page = 0
        self.page_count = int(len(self.words)/10)
    
    def get_embed(self):
        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"{self.user}'s Dictionary",
            description = f"*This is {self.user}'s dictionary.*",
            timestamp = datetime.datetime.now(),
            footer = f'Page {self.page+1} of {self.page_count}'
        )
        for i in range(10):
            word = self.words[self.page*10+i]
            definition = self.dictionary[word]
            embed.add_field(name=word, value=f'> {definition}', inline=False)
        return embed

    async def send(self, i: discord.Interaction):
        self.message = await i.response.send_message(embed=self.get_embed(), view=self)

    @discord.ui.button(style=discord.ButtonStyle.primary, label='<', disabled=True)
    async def left_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        self.page -= 1
        await self.update()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='>', disabled=False)
    async def right_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        self.page += 1
        await self.update()
    
    async def update(self):
        if self.page == 0:
            self.left_button.disabled = True
            self.right_button.disabled = False
        elif self.page == self.page_count:
            self.left_button.disabled = False
            self.right_button.disabled = True
        else:
            self.left_button.disabled = False
            self.right_button.disabled = False
        await self.message.edit(embed=self.get_embed(), view=self)