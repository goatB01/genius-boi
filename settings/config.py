import os

"""the bot token saved in env vars as 'TOKEN' """
TOKEN = os.getenv("TOKEN")
"""the database connection string saved in env vars as 'DB_URL0' """
DB_URL0 = os.getenv("DB_URL0")
"""the database connection string saved in env vars as 'DB_URL1' """
DB_URL1 = os.getenv("CALC_DB_URL1")


COMMANDS={
    "calc":{
        "name":f"/calc [current_Lvl] [target_Lvl] [current_%]* [target_%]*",
        "description":"Calculate the resourses needed to get from your current level to a target level.",
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
        "description":"Show the bot ping.",
        "args":None
           },
    "set_channel":{
        "name":"/set_channel [#channel]",
        "description":"Set a channel as default channel(s) for the bot.\nIf no channel is specified, the bot will run in any channel.\nIf the channel is already a default, it will be removed.",
        "args":{
            "#channel":{
                "description":"The channel to be set as default channel for the bot",
                "required":True
                   }
               }
           },
    "guides":{
        "name":"/guides [skill]",
        "description":"Create a guide of the chosen skill with with dynamic boost menu.",
        "args":{
            "skill":{
                "description":"The skill to make the guide on",
                "required":True
                   }
               }
           },
    "support_server":{
        "name":"/support_server",
        "description":"Get an invite link to the support server,\nWhere you can ask for help, give feedbacks or report bugs.",
        "args":None
    }
}



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


            