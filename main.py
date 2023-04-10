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

bot.load("cogs.updater")
bot.load("cogs.payment")



bot.start()

"""
    'Fishing-Baits': {
        'Earthworm': {
            'emoji_name': 'earthworm_ca2',
            'emoji_id': 922887338357567499
        },
        'Iceworm': {
            'emoji_name': 'iceworm_ca2',
            'emoji_id': 922887338655354962
        },
        'Corpseworm': {
            'emoji_name': 'corpseworm',
            'emoji_id': 922887338269499414
        },
        'Toxic Worm': {
            'emoji_name': 'toxic_worm_ca2',
            'emoji_id': 922887339037044756
        },
        'Sandworm': {
            'emoji_name': 'sandworm_ca2',
            'emoji_id': 922887338848296970
        },
        'Beetle': {
            'emoji_name': 'beetle_ca2',
            'emoji_id': 922887338412097656
        },
        'Grasshopper': {
            'emoji_name': 'grasshopper_ca2',
            'emoji_id': 922887338810548265
        },
        'Wasp': {
            'emoji_name': 'wasp_ca2',
            'emoji_id': 922887339070619708
        },
        'Scallop': {
            'emoji_name': 'scallop_ca2',
            'emoji_id': 922887338756030515
        },
        'Crab': {
            'emoji_name': 'crab_ca2',
            'emoji_id': 922887338567286784
        },
        'Bass': {
            'emoji_name': 'bass_ca2',
            'emoji_id': 922873492058284094
        }
    }"""


  

