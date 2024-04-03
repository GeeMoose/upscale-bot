# 处理逻辑的Helper文件
import cv2

import os
import requests
import json
import base64
import re
import discord
import io

# mapped model with usual occasion
mapped_dict = {
    'General': 'RealESRGAN_General_x4_v3',
    # 'general': 'RealESRGAN_General_x4_v3',
    'Anime': 'realesrgan-x4plus-anime',
    # 'anime': 'realesrgan-x4plus-anime',
    'Landscope': 'remacri',
    # 'landscope': 'remacri',
    'Protrait': 'GFPGANv1.4.pth',
    # 'protrait': 'GFPGANv1.4.pth'
}

PATTERN = r'(.*?)\?'

# Create a class called UIFormat that subclasses discord.ui.View
class UIFormat(discord.ui.View):
    def __init__(self,ctx,imageurl,model,scale,result):
        super().__init__(timeout=None, disable_on_timeout=True)
        self.imageurl = imageurl
        self.model = model 
        self.scale = scale
        self.result = result
        self.ctx = ctx
    
    @discord.ui.button(label="General", style=discord.ButtonStyle.gray, custom_id='model_general')
    async def button_general(self, button, interaction):
        # 同类选项要有排他性
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='model']:
            x.style = discord.ButtonStyle.gray
        self.model = 'General'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="Anime", style=discord.ButtonStyle.gray, custom_id='model_anime')
    async def button_anime(self, button, interaction): 
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='model']:
            x.style = discord.ButtonStyle.gray
        self.model = 'Anime'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="Landscope", style=discord.ButtonStyle.gray, custom_id='model_landscope')
    async def button_landscope(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='model']:
            x.style = discord.ButtonStyle.gray
        self.model = 'Landscope'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="Protrait", style=discord.ButtonStyle.gray, custom_id='model_protrait')
    async def button_protrait(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='model']:
            x.style = discord.ButtonStyle.gray
        self.model = 'Protrait'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="1x", row = 1, style=discord.ButtonStyle.gray, custom_id='scale_1x')
    async def button_1x(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='scale']:
            x.style = discord.ButtonStyle.gray
        self.scale = '1'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="2x", row = 1, style=discord.ButtonStyle.gray, custom_id='scale_2x')
    async def button_2x(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='scale']:
            x.style = discord.ButtonStyle.gray
        self.scale = '2'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="3x", row = 1, style=discord.ButtonStyle.gray, custom_id='scale_3x')
    async def button_3x(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='scale']:
            x.style = discord.ButtonStyle.gray
        self.scale = '3'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="4x", row = 1, style=discord.ButtonStyle.gray, custom_id='scale_4x')
    async def button_4x(self, button, interaction):
        for x in [x for x in self.children if x.style == discord.ButtonStyle.blurple and x.custom_id[:5]=='scale']:
            x.style = discord.ButtonStyle.gray
        self.scale = '4'
        button.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view = self) # Send a message when the button is clicked
    @discord.ui.button(label="", row = 1, style=discord.ButtonStyle.gray, custom_id='options_reset',emoji='🔄')
    async def button_reset(self, button, interaction):
        for item in [x for x in self.children if x.style == discord.ButtonStyle.blurple]:
            # await interaction.response.defer()
            item.style = discord.ButtonStyle.gray
        await interaction.response.edit_message(view = self)
    @discord.ui.button(label="Go", row = 2, style=discord.ButtonStyle.gray, custom_id='image_upscale',emoji='😉')
    async def button_upscale(self, button, interaction):
        # await ctx.send(input)
        # aws后端交互
        # await ctx.defer()
        await interaction.response.defer()
        await interaction.followup.send(f'Processing {self.ctx.author.display_name} work ...')
        # 若没有选择，直接upscale，提示选择后超分
        if self.model == '' and self.scale == '':
            await interaction.followup.send('Sorry! There are no enough options to be chosen to upscale. Please Verify Your Choose.')
            return
        
        response = await request(self.imageurl,self.model,self.scale)
        if response.status_code == 200:
            await process_data(self.ctx,response,self.result)
        else:
            await self.ctx.respond("Sorry! There seems to be a network error. Please try again later.")
    async def on_timeout(self):
        # if self.is_finished():
        self.disable_all_items()
        if self.message:
            await self.message.edit(view=None)
        
    
    
        
# 对上传图片的大小和分辨率审核
async def check_passport(imageurl): 
    
    match = re.search(PATTERN,imageurl)
    if match:
        block = match.group(1).split('/')
    else:
        block = imageurl.split('/')

    filename = block[-1]
    origin_file_path = "inputs/" + filename
    # 支持文件类型
    if filename.split('.')[-1] not in ['png','jpg','jpeg','webp','PNG','JPG','JPEG','WEBP']:
        return 'The image extension is not supported currently! ',None, False
    
    response = requests.get(imageurl)
    if response.status_code == 200:
        with open(origin_file_path,"wb") as file:
            file.write(response.content)
        try:
            # 图片大小
            size = os.path.getsize(origin_file_path)
            if size > 3145728:
                return 'The file size is too large! Try compressing it to reduce the size.',None, False
            img = cv2.imread(origin_file_path, cv2.IMREAD_UNCHANGED)
            # 分辨率
            h,w = img.shape[0:2]
            if h*w > 2560000:
                return 'The resolution is too high! Try reducing the resolution.',None, False
            return filename, response.content, True
        
        except Exception as e:
            return e, None, False
       
    else:
        return 'There seems to be a network issue. Please wait a moment and try again',None, False
            

# request aws后端
async def request(imageurl,model,scale):
    match = re.search(PATTERN,imageurl)
    if match:
        imageurl = match.group(1)
        
    headers = {'Content-type': 'application/json'}
    data={
        'imageUrl': imageurl,
        'model': mapped_dict[model],
        'scale': scale
    }

    r = requests.post('http://44.202.128.59:8888/image-upscaling', data=json.dumps(data),headers=headers)
    
    return r



async def process_data(ctx, response: requests.Response, result):
    try:
        # 显示返回的图片到discord上
        data = response.json()['result']
        res = re.search(',',data)
        _,start_idx = res.span()
        file = discord.File(io.BytesIO(base64.b64decode(data[start_idx:])),result)
        await ctx.respond(f'{ctx.author.mention}',file=file)
            
    except:
        await ctx.respond("An exception occurred during the return process. Please contact adminators for repairs.")
       
        
