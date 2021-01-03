from mcrcon import MCRcon

with MCRcon(host="sundromi.germanywestcentral.cloudapp.azure.com", password="rcon") as mcr:
    resp = mcr.command("stop")
    print(resp)
