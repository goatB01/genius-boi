import os

COMMANDS={
    "calc":{
        "name":f"/calc [current_Lvl] [target_Lvl] [current_%]* [target_%]*",
        "description":"calculate resourses needed from your current level to a target level.",
        "args":{
            "current Lvl":{
                "description":"your current level",
                "required": True
                   },
            "target Lvl":{
                "description":"the target level",
                "required":True
                   },
            "current %":{
                "description":"your current level %",
                "required":False
                   },
            "target %":{
                "description":"the % of the target level",
                "required":False
                   }
               }
           },
    "ping":{
        "name":"/ping",
        "description":"show the bot ping.",
        "args":None
           },
    "set_channel":{
        "name":"/set_channel [#channel]",
        "description":"set a channel as default channel(s) for the bot.\nif no channel is specified, the bot will run in any channel.",
        "args":{
            "#channel":{
                "description":"the channel to be set as default channel for the bot",
                "required":True
                   }
               }
           }
}
"""the bot token saved in env vars as 'TOKEN' """
TOKEN = os.getenv("TOKEN")
"""the database connection string saved in env vars as 'DB_URL' """
DB_URL = os.getenv("DB_URL")
CALC_DB_URL = os.getenv("CALC_DB_URL")


job_list=[
    "woodcutter",
    "crafter",
    "miner",
    "smither",
    "fisher",
    "tailor"
]
job_rsc={
    "woodcutter": "logs",
    "crafter": "relics",
    "miner": "ores",
    "smither": "bars",
    "fisher": "fish",
    "tailor": "magic"
}
categories = [ "logs",
                "ores",
                "relics",
                "bars",
                "fish",
                "magic"
            ] 


            