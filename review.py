from functions import *
import datetime
import discord
import random

class Review(discord.ui.View):
    def __init__(self, mode: str, user: str, num_words: int):
        super().__init__(timeout=None)
        self.mode = mode # word or definition
        self.user = user
        self.current_word = 0
        self.num_words = num_words # must be between 1 and the number of words in dictionary
        self.dictionary = get_dictionary(self.user)

        self.review_words = {}
        for i in range(self.num_words):
            random_word = self.dictionary.pop(random.choice(list(self.dictionary)))
            self.review_words[random_word['word']] = random_word
            self.review_words[random_word['word']]['revealed'] = False
        self.words = list(self.review_words.keys())
    
    def get_embed(self):
        embed = discord.Embed(
            color = discord.Color.dark_teal(),
            title = f"Reviewing {self.user}'s Dictionary",
            description = f"*You are reviewing {'word' if self.mode=='word' else 'definition'}s from your dictionary.*",
            timestamp = datetime.datetime.now()
        )

        current_word = self.review_words[self.words[self.current_word]]
        if self.mode == 'word':
            embed.add_field(name='Word', value=current_word['word'], inline=False)
            embed.add_field(name='Definition', value=current_word['definition'] if current_word['revealed'] else '*(This definition has not been revealed yet)*')
        else:
            embed.add_field(name='Word', value=current_word['word'] if current_word['revealed'] else '*(This word has not been revealed yet)*', inline=False)
            embed.add_field(name='Definition', value=current_word['definition'])
        embed.set_footer(text=f'Word {self.current_word+1} of {self.num_words}')

        return embed
    
    async def send(self, i: discord.Interaction):
        if self.current_word != 0:
            self.left_button.disabled = False
        if self.current_word+1 != self.num_words:
            self.right_button.disabled = False
        if self.current_word == 0:
            self.left_button.disabled = True
        if self.current_word+1 == self.num_words:
            self.right_button.disabled = True
        await i.response.send_message(embed=self.get_embed(), view=self)
        self.original_response = await i.original_response()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='<')
    async def left_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        if self.current_word != (self.current_word-1)%self.num_words:
            self.current_word = (self.current_word-1)%self.num_words
            await self.update()
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label='Reveal Definition')
    async def reveal_definition_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        self.review_words[self.words[self.current_word]]['revealed'] = True
        await self.update()

    @discord.ui.button(style=discord.ButtonStyle.primary, label='>')
    async def right_button(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.defer()
        if self.current_word != (self.current_word+1)%self.num_words:
            self.current_word = (self.current_word+1)%self.num_words
            await self.update()
    
    async def update(self):
        if self.current_word != 0:
            self.left_button.disabled = False
        if self.current_word+1 != self.num_words:
            self.right_button.disabled = False
        if self.current_word == 0:
            self.left_button.disabled = True
        if self.current_word+1 == self.num_words:
            self.right_button.disabled = True
        if self.review_words[self.words[self.current_word]]['revealed']:
            self.reveal_definition_button.disabled = True
        else:
            self.reveal_definition_button.disabled = False
        await self.original_response.edit(embed=self.get_embed(), view=self)