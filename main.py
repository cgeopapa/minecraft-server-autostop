import os
import time
import discord
from dotenv import load_dotenv
from mcrcon import MCRcon
from azure.mgmt.compute import ComputeManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import ClientSecretCredential

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GROUP_NAME = os.getenv('GROUP_NAME')
VM_NAME = os.getenv('VM_NAME')

def get_credentials():
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    credentials = ClientSecretCredential(
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET'),
        tenant_id=os.getenv('AZURE_TENANT_ID')
    )
    return credentials, subscription_id

client = discord.Client()
credentials, subscription_id = get_credentials()
compute_client = ComputeManagementClient(credentials, subscription_id)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '!start':
        await message.channel.send("Starting minecraft server...")
        start_operation = compute_client.virtual_machines.begin_start(GROUP_NAME, VM_NAME)
        start_operation.wait()
        time.sleep(10)
        await message.channel.send("Minecraft server is ready!")
        return
    if message.content == '!stop':
        await message.channel.send("Stoping minecraft server...")

        try:
            with MCRcon(os.getenv('SERVER_URL'), os.getenv('RCON_PASSWORD')) as mcr:
                resp = mcr.command("stop")
        except:
            await message.channel.send("Minecraft server seems to be stopped. Deallocating VM...")

        start_operation = compute_client.virtual_machines.begin_deallocate(GROUP_NAME, VM_NAME)
        start_operation.wait()
        await message.channel.send("Minecraft server has stopped!")
        return
    if message.content == '!help':
        await message.channel.send("!start -> Start the Minecraft server\n!stop -> Stop the Minecraft server")
        return

client.run(TOKEN)