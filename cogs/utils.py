import interactions
import interactions as it
from interactions import Client
from interactions import CommandContext as CC
from interactions import ComponentContext as CPC 
from pymongo import MongoClient



from settings.config import *
from tools.visio import visualizator


class Utility(interactions.Extension):
    def __init__(self,client: Client,default_channels) -> None:
        self.bot = client
        self.DBclient = MongoClient(CALC_DB_URL)
        self.DB = self.DBclient["Miscs"]
        self.channel_collection = self.DB["config"]
        self.default_channels:dict[str,list] = default_channels
        return None


    

    def add_channel(self,guild_id:str,channel_id:int) -> bool:
        added = True
        try:
            
            self.channel_collection.update_one({"_id": "channels"}, {"$set": {guild_id: [channel_id]}}) #update the cloud
            self.default_channels[guild_id] = [channel_id] # update the local
        except Exception as e :
            print(e)
            added = False
        return added

    def update_channel(self,guild_id:str,channel_id:int) -> bool:
        updated = True
        try:
            self.channel_collection.update_one({"_id": "channels"}, {"$push": {guild_id: channel_id}}) #update the cloud
            self.default_channels[guild_id].append(channel_id) # update the local
        except Exception as e :
            print(e)
            updated = False
        return updated

    def delete_channel(self,guild_id:str,channel_id:int) -> bool:
        updated = True
        try:
            self.channel_collection.update_one({"_id": "channels"}, {"$pull": {guild_id: channel_id}}) #update the cloud
            self.default_channels[guild_id].remove(channel_id) # update the local
            if self.default_channels[guild_id] == [] :
                self.channel_collection.update_one({"_id": "channels"}, { "$unset": {guild_id: ""}}) #update the cloud
                self.default_channels.pop(guild_id) # update the local
        except Exception as e :
            print(e)
            updated = False
        return updated

    def check_channel(self,guild_id:str,channel_id:int) -> bool:
        
        if guild_id in self.default_channels:
            if channel_id in self.default_channels[guild_id]:
                return [True]
            else:
                return [False,self.default_channels[guild_id]]
        else:
            return [None]        



    @interactions.extension_command(
        name="help",
        description="show all commands with their description",
        options=[
            it.Option(
                name="command",
                description="the command to look for",
                required=False,
                type=it.OptionType.STRING,
                choices=[
                    it.Choice(
                        name="calc",
                        value="calc"
                    ),
                    it.Choice(
                        name="set_channel",
                        value="set_channel"
                    ),
                    it.Choice(
                        name="ping",
                        value="ping"
                    )
                ]
            )
        ]
    )
    async def help(self,ctx:CC,command:str=None):
        ######################################
        channel_state = self.check_channel(guild_id=str(ctx.guild_id),channel_id=int(ctx.channel_id))

        if channel_state[0] == False:
            channel_ids = channel_state[1]
            channel_tags = [f"<#{channel_ids[_id]}>" for _id in range(len(channel_ids))]
            tags = " or ".join(channel_tags)
            await ctx.send(content=f"you can't use me here, go to {tags} please",ephemeral=True)
            return
        #####################################
        _embed  = it.Embed()
        if command == None:
            _embed.title = "Help"
            for _command in COMMANDS:
                _embed.add_field(name=f'/{_command} :',value=f'```{COMMANDS[_command]["name"]}```\n{COMMANDS[_command]["description"]}')
        else:
            _name = COMMANDS[command]["name"]
            _description = COMMANDS[command]["description"]
            _args = COMMANDS[command]["args"]
            _embed.title = command.title()
            _embed.description = f"```{_name}```"
            _embed.add_field(
                            name="description",
                            value=f"{_description}"
                            )
            if _args != None:
                _text = ""
                for _arg in _args:
                    _req = "yes" if _args[_arg]["required"] else "optional"
                    _text = _text + f'**----{_arg}** :\n|--------**description:** {_args[_arg]["description"]}\n|--------**required:** {_req}\n'

                _embed.add_field(
                                name="arguments",
                                value=_text
                                )
        await ctx.send(embeds=_embed)

    @interactions.extension_command(
        name="set_channel",
        description="lock the bot to a specified channel",
        options=[
            it.Option(
                name="channel",
                description="the channel to lock the bot in",
                required=True,
                type=it.OptionType.CHANNEL
                )
        ],
        default_member_permissions=it.Permissions.ADMINISTRATOR

    )
    async def set_channel(self,ctx:CC,channel:it.Channel):
        
        await ctx.defer(ephemeral=True)
        channel_id = int(channel.id)
        guild_id = str(ctx.guild_id)
        state = ""
        if guild_id in self.default_channels: #a default channel already exit
            if channel_id in self.default_channels[guild_id]:
                updated = self.delete_channel(guild_id=guild_id,channel_id=channel_id)
                state = "removed"
            else:
                updated = self.update_channel(guild_id=guild_id,channel_id=channel_id)
                state = "added"

        elif guild_id not in self.default_channels: #no default channel
            updated = self.add_channel(guild_id=guild_id,channel_id=channel_id)
            state = "added"
        if updated:
            await ctx.send(f"<#{channel.id}> has been {state} as default channel for the bot.",ephemeral=True)
        else:
            await ctx.send("There's been an error, please try again later.",ephemeral=True)

    @interactions.extension_command(
            name="ping",
            description="show the bot ping"
            )
    async def ping(self,ctx:CC):
        ######################################
        channel_state = self.check_channel(guild_id=str(ctx.guild_id),channel_id=int(ctx.channel_id))

        if channel_state[0] == False:
            channel_ids = channel_state[1]
            channel_tags = [f"<#{channel_ids[_id]}>" for _id in range(len(channel_ids))]
            tags = " or ".join(channel_tags)
            await ctx.send(content=f"you can't use me here, go to {tags} please",ephemeral=True)
            return
        #####################################
        await ctx.send(f"pong! {round(self.bot.latency)}s")

    @interactions.extension_command(
        name="analytics",
        description="show analytics for the bot activities",
        options=[
            it.Option(
                name="type",
                description="the type of the analytics to show",
                required=True,
                type=it.OptionType.STRING,
                choices=[
                    it.Choice(
                        name="Calculator",
                        value="calc"
                    ),
                    it.Choice(
                        name="Guides",
                        value="guides"
                    )
                ]
            )
        ]
    )
    async def analytics(self,ctx:CC,type:str):
        ######################################
        channel_state = self.check_channel(guild_id=str(ctx.guild_id),channel_id=int(ctx.channel_id))

        if channel_state[0] == False:
            channel_ids = channel_state[1]
            channel_tags = [f"<#{channel_ids[_id]}>" for _id in range(len(channel_ids))]
            tags = " or ".join(channel_tags)
            await ctx.send(content=f"you can't use me here, go to {tags} please",ephemeral=True)
            return
        #####################################
        await ctx.defer()
        vision = visualizator()
        _filename = vision.create_image(skills_type=type)
        placeholder = "Calculator" if type == "calc" else "Guides"

        _embed = it.Embed(
                        title=f"{placeholder} Analytics"
                        )
        _file = it.File(f"{_filename}")        
        _embed.set_image(url=f"attachment://{_filename}")
        await ctx.send(embeds=[_embed],files=_file)



def setup(client:Client,default_channels):
    Utility(client,default_channels)
    print("utils loaded")


