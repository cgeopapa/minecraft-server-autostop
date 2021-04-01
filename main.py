import asyncio
import os

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from dispike import Dispike
from dispike.followup import FollowUpMessages
from dispike.models import IncomingDiscordInteraction
from dispike.register.models import (
    DiscordCommand,
)
from dispike.response import DiscordResponse
from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GROUP_NAME = os.getenv('GROUP_NAME')
VM_NAME = os.getenv('VM_NAME')
PORT = int(os.environ.get("PORT", 5000))


def get_credentials():
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    credentials = ClientSecretCredential(
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET'),
        tenant_id=os.getenv('AZURE_TENANT_ID')
    )
    return credentials, subscription_id


startCommand = DiscordCommand(
    name="start",
    description="start minecraft server",
    options=[]
)
stopCommand = DiscordCommand(
    name="stop",
    description="stop minecraft server",
    options=[]
)
bot = Dispike(client_public_key="51aca7e76e8edef6ad758d38e93fd685af4b2168d0596435f5d659c75d8f55d0",
              application_id="825407954848317500",
              bot_token=TOKEN)
credentials, subscription_id = get_credentials()
compute_client = ComputeManagementClient(credentials, subscription_id)
bot.register(startCommand, guild_only=True, guild_to_target=798133022091640893)
bot.register(stopCommand, guild_only=True, guild_to_target=798133022091640893)


async def stopMCServer(ctx: IncomingDiscordInteraction):
    await asyncio.sleep(0.1)
    followup = FollowUpMessages(bot=bot, interaction=ctx)
    try:
        with MCRcon(os.getenv('SERVER_URL'), os.getenv('RCON_PASSWORD')) as mcr:
            mcr.command("stop")
    except:
        await followup.async_create_follow_up_message(DiscordResponse(follow_up_message=False, content="Minecraft server seems to be stopped. Deallocating VM..."))
    start_operation = compute_client.virtual_machines.begin_deallocate(GROUP_NAME, VM_NAME)
    start_operation.wait()
    await followup.async_create_follow_up_message(DiscordResponse(content="Minecraft server has stopped!"))


async def startMCServer(ctx: IncomingDiscordInteraction):
    await asyncio.sleep(0.1)
    start_operation = compute_client.virtual_machines.begin_start(GROUP_NAME, VM_NAME)
    start_operation.wait()
    await asyncio.sleep(20)
    followup = FollowUpMessages(bot=bot, interaction=ctx)
    await followup.async_create_follow_up_message(DiscordResponse(content="Minecraft server is ready!"))


@bot.interaction.on("start")
async def startInteraction(ctx: IncomingDiscordInteraction) -> DiscordResponse:
    await bot.background(startMCServer, ctx)
    return DiscordResponse(content="Starting minecraft server...")


@bot.interaction.on("stop")
async def sropServer(ctx: IncomingDiscordInteraction) -> DiscordResponse:
    await bot.background(stopMCServer, ctx)

    return DiscordResponse(content="Stopping minecraft server...")


bot.run(port=PORT)
