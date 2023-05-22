import os
import discord
from dotenv import load_dotenv
import gspread
from itertools import cycle
from keep_alive import keep_alive
from discord.ext import tasks

# Note: google api token .json file for accessing a google sheet must exist at .config/service_account.json
# Flask app to keep script running. Useful if hsoted on replit
#keep_alive()

# Get discord info from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Define app intents for discord integration
intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents = intents)

# Define status for the discord bot (can cycle between several as below)
status = cycle(['Defending the Vault','Becomming a Shadow', 'Raiding the Vault', 'Becomming Immortal'])

@tasks.loop(seconds=100)
# Sets status to "online" when booted
async def change_status():
  await client.change_presence(activity=discord.Game(next(status)))

# Boot up bot and perform checks after starting
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    change_status.start()
    print("Your bot is ready")
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n'.join([member.name for member in guild.members])
    print(members)
    ids = [member.id for member in guild.members]

# Function to get a code from an excel sheet corresponding to a username  
def getPassword(username):
    sa = gspread.service_account(filename = ".config/service_account.json")
    sh = sa.open("Immortal stats")
    wks = sh.worksheet("passwords")

    nameCol = wks.get('C2:C302')
    passwords = wks.get('A2:A302')
    #does username exist
    try:
        listname = list([username])
        nameExist = nameCol.index(listname)
        new_pass =  ''.join(passwords[nameExist])
        print(new_pass)
        
    except:
        #get first empty row idx
        index = nameCol.index([])
    
        #get index of password
        new_pass = ''.join(passwords[index])

        #write name to password
        sheetIdx = str(index+2)
        updateRow = ''.join(['C',sheetIdx])
        wks.update(updateRow, username)
        print(updateRow)
    return new_pass

# Function to get username in excel sheet corresponding to the max value in another column 
def getWhale():
    sa = gspread.service_account(filename = ".config/service_account.json")
    sh = sa.open("Immortal stats")
    wks = sh.worksheet("Stats")
    #print("loaded worksheet")
    resonance = wks.get('D2:D302')
    flat_list = [item for sublist in resonance for item in sublist]
    intList = [int(i) for i in flat_list]
    maxRes = str(max(intList))
    listRes = list([maxRes])
    idx = resonance.index(listRes)
    nameCol = wks.get('A2:A302') 
    whalename = ''.join(nameCol[idx])
    whaleID = str(whalename)
    return maxRes, whaleID

# What to do when bot directly messaged with a specific phrase
@client.event
async def on_message(message):
    if message.author == client.user:
        return
       
    if message.content == '!pass':
        username = message.author.name
        yourPassword = getPassword(username)
        response = ''.join(['Your Password is: ', yourPassword, '\n Please log in to the app here: https://spreat-sheet-immortal.netlify.app/' ])
        await message.channel.send(response)

    if message.content == '!whale':
      print("whale detected")
      maxRes, whaleID = getWhale()
      response = ''.join(['Currently, the biggest whale in The Alliance is: ', whaleID, ', with a whopping ', str(maxRes), ' resonance!'])
      #print(response)
      await message.channel.send(response)


# Start Bot
client.run(TOKEN)



