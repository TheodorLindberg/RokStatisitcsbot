from datetime import datetime
import discord
import json

from discord import player
from discord import message
from discord import file
from jinja2 import environment

import os

from dotenv import load_dotenv

load_dotenv()

from main import makeGraph, makePowerGraph, makeResourceGraph

channel_bot = 785793156993253387
channel_power = 921146672103444560
channel_storage = 921366734278103090
channel_graph = 921146721621393429

fields = {
    "power": ['power', 'p'],
    "power_building": ['building', 'bp', 'bp'],
    "technology_power": ['tech', 'rp', 'pr'],
    "troops_power": ['troops', 'tp', 'pt'],
    "commander_power": ['commander', 'cp', 'pc'],
    "resource_gathered": ['gathered', 'rg'],
    "top50": ['top50', 't50'],
    "top100": ['top100', 't100'],
    "top200": ['top20', 't200'],
}

idToPlayer = {
    365469050794672128: "Lancer",
    237495183934095361: "Pilbagsskytten",
    377018183623901184: "StolBord"
}

with open('data.json') as json_file:
    data_json = json.load(json_file)

with open('message_id.json') as json_file:
    graph_message_id_json = json.load(json_file)


def parseMessage(message):

    try:
        field = None
        fieldKeyword = None
        playerId = message.author.id
        playerName = message.author.name
        date = message.created_at

        if len(message.raw_mentions) > 0:
            playerId = message.raw_mentions[0]
            if playerId in idToPlayer:
                playerName = idToPlayer[playerId]
            else:
                playerName = playerId

        for fieldName, keys in fields.items():
            for key in keys:
                if key in message.content:
                    fieldKeyword = key
                    field = fieldName

        if field is not None:
            contentValue = message.content[:]
            if "<" in contentValue:
                contentValue = contentValue[0:contentValue.find(
                    "<")] + contentValue[contentValue.find(">"):-1]

            contentValue = contentValue.replace(fieldKeyword, "")
            contentValue = contentValue.replace(" ", "")
            value = None
            sufixFactor = 1
            if "k" in contentValue:
                sufixFactor = 1000
                contentValue = contentValue.replace("k", "")
            if "m" in contentValue:
                sufixFactor = 1000000
                contentValue = contentValue.replace("m", "")

            value = int(float(contentValue) * sufixFactor)
            return (field, value, playerId, playerName, date)
        else:
            return None
    except ValueError:
        return None


def addFieldValue(field, value, date, playerId):
    if field in data_json:
        data_json[field].append({
            "id": playerId,
            "field": field,
            "value": value,
            "date": str(date)
        })
    else:
        data_json[field] = [{
            "id": playerId,
            "field": field,
            "value": value,
            "date": str(date)
        }]

    with open('data.json', 'w') as outfile:
        json.dump(data_json, outfile)


class MyClient(discord.Client):

    async def on_ready(self):
        print('Logged on as', self.user)
        self.graph_channel = self.get_channel(channel_graph)
        self.storage_channel = self.get_channel(channel_storage)

    async def updateGraph(self, filename, title, field):
        global power_message_id
        res = await self.storage_channel.send(file=discord.File('graphs/' +
                                                                filename))
        if res is not None and len(res.attachments) == 1:
            url = res.attachments[0].url
            print(url)
            embed = discord.Embed(title=title)
            embed.set_image(url=url)
            embed.set_footer(text="Updaterad: " +
                             datetime.now().strftime("%b %d %H:%M"))
            if field in graph_message_id_json:
                message = await self.graph_channel.fetch_message(
                    graph_message_id_json[field])
                await message.edit(embed=embed)
            else:
                message_res = await self.graph_channel.send(embed=embed)
                graph_message_id_json[field] = message_res.id
                with open('message_id.json', 'w') as outfile:
                    json.dump(graph_message_id_json, outfile)

    async def handleGraphUpdate(self, field):
        if field == "power":
            file = makePowerGraph(data_json)
            await self.updateGraph(file, "Power graf", field)
        elif field == "resource_gathered":
            file = makeResourceGraph(data_json)
            await self.updateGraph(file, "Resurs graf", field)

    async def on_message(self, message):

        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.channel.id == channel_graph:
            print("{id} msg: {m}".format(id=message.id, m=message.content))

        if message.channel.id == channel_power:
            if "update" in message.content:
                await message.channel.send("update")
                if "resource" in message.content:
                    await self.handleGraphUpdate("resource_gathered")
                if "power" in message.content:
                    await self.handleGraphUpdate("power")
                return

            parsed = parseMessage(message)
            if parsed:
                (field, value, playerId, playerName, date) = parsed

                addFieldValue(field, value, date, playerId)
                await message.channel.send(
                    'set {f} for player {p} to {v} at{d}'.format(f=field,
                                                                 p=playerName,
                                                                 v=value,
                                                                 d=date))
                await self.handleGraphUpdate(field)


def main():
    try:
        client = MyClient()
        token = os.environ.get("TOKEN")
        if token is not None:
            client.run(token)
        else:
            print("No token")
    finally:
        print("Shutdown")


if __name__ == '__main__':
    main()

#p 136k
#pb 10600
#pr 9639
#pt 34043
#pc 108600

#rg
#p50
#p100
#p150