TOKEN = "ODgxMTc4MzEzMTYxMzEwMjI4.GrkZA6.GAQbruKBybM0xladnR6T-Q71qI_8Upzja-stxc"
CALC_DB_URL = "mongodb+srv://smartboi:pega11963112@smartboi.g8shibc.mongodb.net/?retryWrites=true&w=majority"


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
