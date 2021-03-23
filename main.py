import os
import time
from time import gmtime

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from discord.ext import tasks, commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from mcrcon import MCRcon

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


bot = Bot(command_prefix='#')
credentials, subscription_id = get_credentials()
compute_client = ComputeManagementClient(credentials, subscription_id)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command(name='start', help='Start minecraft server')
async def startServer(context):
    await context.send("Starting minecraft server...")
    start_operation = compute_client.virtual_machines.begin_start(GROUP_NAME, VM_NAME)
    start_operation.wait()
    time.sleep(10)
    await context.channel.send("Minecraft server is ready!")


@bot.command(name='stop', help='Stop minecraft server')
async def sropServer(context):
    await context.send("Stoping minecraft server...")

    try:
        with MCRcon(os.getenv('SERVER_URL'), os.getenv('RCON_PASSWORD')) as mcr:
            resp = mcr.command("stop")
    except:
        await context.send("Minecraft server seems to be stopped. Deallocating VM...")

    start_operation = compute_client.virtual_machines.begin_deallocate(GROUP_NAME, VM_NAME)
    start_operation.wait()
    await context.send("Minecraft server has stopped!")


bot.run(TOKEN)
