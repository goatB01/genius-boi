import os
from interactions.ext.wait_for import setup
from interactions import Client
from pymongo import MongoClient
from settings.config import *
#import logging



default_channels:dict[str,list[int]] = MongoClient(DB_URL1)["Miscs"]["config"].find_one({"_id":"channels"})

bot = Client(token=TOKEN,disable_sync=False)
#logging.basicConfig(level=logging.DEBUG)

setup(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {str(bot.me.name)}!')


bot.load("cogs.utils",default_channels=default_channels)
bot.load("cogs.calc",default_channels=default_channels)
bot.load("cogs.compass",default_channels=default_channels)

#bot.load("cogs.updater")
#bot.load("cogs.payment")



bot.start()

