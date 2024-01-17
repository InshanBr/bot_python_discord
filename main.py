import os
from io import BytesIO
import re
import discord
import PyPDF2
from dotenv import load_dotenv
from random import randint

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
data = {}
dado = 20

intents=discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

client = discord.Client(intents=intents)

list_rolls = ['força', 'vigor', 'agilidade', 'destreza', 'luta', 'intelecto', 'prontidao', 'presença']
text = '!'
for i in list_rolls: text += i + ','
help = f"""
Comandos:
!read - Informar esse comando junto com o envio da ficha
!receave - Recebe as informações dos dados que o usuario enviou caso exista
!all - Informação de teste para mostrar os dados dos usuarios # Apenas em testes
Dados de atributos - {text[:-1]}
"""


def dice(dices:int,num_dice:int,atribute:int): # Executa a rolagem do dado de acordo com as informações enviadas.
    if dices < 1 or num_dice < 1:
        return 'Dado Incorreto'
    dices,num_dice = int(dices),int(num_dice)
    rolled = []
    rolled_num = 0
    dices_text = ''
    for _ in range(dices): rolled.append(randint(1,num_dice)); rolled_num += rolled[-1]
    length = len(rolled)
    for x,i in enumerate(rolled):
        if x+1 < length:
            dices_text += f'{i},'
        else:
            dices_text += f'{i}'
    rolled_num += atribute
    dices_text = f"` {rolled_num} ` ⟵ [{dices_text}] {dices}d{num_dice}"
    if atribute != 0:
        if atribute < 0: dices_text += f' - {abs(atribute)}'
        else: dices_text += f' + {atribute}'
    return  dices_text

@client.event
async def on_ready():
    print(f'{client.user} online!')

@client.event
async def on_message(message):
    if message.author == client.user: # Ignora mensagens do próprio bot.
        return  

    if message.content.startswith('!help'): # Comando para enviar os comandos do bot.
        await message.channel.send(help)
        
    if message.content.startswith('!read'): # Comando para ler o pdf enviado junto com ele.
        if message.attachments:
            file_content = await message.attachments[0].read()
            pdf_bytes = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_bytes)
            fields = pdf_reader.get_fields()
            data[message.author] = {
                'heroi':fields['Herói']['/V'],
                'força':fields['Forca']['/V'],
                'vigor':fields['Vigor']['/V'],
                'agilidade':fields['Agilidade']['/V'],
                'destreza':fields['Destreza']['/V'],
                'luta':fields['Luta']['/V'],
                'intelecto':fields['Intelecto']['/V'],
                'prontidao':fields['Prontidao']['/V'],
                'presença':fields['Presenca']['/V']
            }
            await message.reply('Dados lidos com sucesso!')
    
    if message.content.startswith('!receave'): # Comando para enviar as informações salvas do usuario caso existam.
        try:
            send = ''
            for i in data[message.author]: send += (f'{i} : {data[message.author][i]}\n')
            await message.reply(send)
        except:
            await message.reply(f'{message.author} não possui registros!')

    if message.content.startswith(('!força', '!vigor', '!agilidade', '!destreza', '!luta', '!intelecto', '!prontidao', '!presença')): # Comando para rolar o dado com base no atributo informado.
        text = re.sub('[!]', '', message.content)
        try:
            if text in list_rolls:
                num_adict = int(data[message.author][text])
                dice_rolled = randint(1, 20)
                result = dice_rolled + num_adict
                response = f"'{text}': ` {result} ` ⟵ [{dice_rolled}] 1d20 + {num_adict}"
            else:
                response = "Dado Incorreto!"
        except:
            response = "Dados não carregados!"
        await message.reply(response)
client.run(TOKEN)
