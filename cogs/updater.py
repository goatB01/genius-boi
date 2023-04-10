import interactions
import interactions as it
from interactions import Client, Button, ButtonStyle, Modal, TextInput,TextStyleType
from interactions import CommandContext as CC

import asyncio
import interactions.ext.wait_for
from interactions.ext.wait_for import wait_for

from settings.config import *

import pymongo



class MasterUpdater(interactions.Extension):

    def __init__(self,client : Client) -> None:
        self.bot = client
        self.mclient = pymongo.MongoClient(DB_URL0)
        self.mdb = self.mclient["Company"]

        self.commit_button  = Button(
            label="Commit",
            custom_id="commit_btn",
            style=ButtonStyle.SUCCESS
        )
        self.discard_button  = Button(
            label="Discard",
            custom_id="discard_btn",
            style=ButtonStyle.DANGER
        )
        self.delete_button  = Button(
            label="Delete",
            custom_id="delete_btn",
            style=ButtonStyle.DANGER
        )


        return

    
    def insert_item(self,category:str,item:str,value:int) -> bool:
        """insert new item to database"""
        inserted = True
        try:
            mcoll = self.mdb["fairco"]
            mcoll.update_one({"_id":"resources"},{"$push": {category:item}})
            mcoll.update_one({"_id":"prices"},{"$set": {item:value}})
        except Exception as e:
            print(e)
            inserted = False
        
        return inserted

    def update_item(self,item:str,new_value:int) -> bool:
        """update chosen item in database with a given value"""
        updated = True
        try:
            mdb = self.mclient["Company"]
            mcoll = mdb["fairco"]
            mcoll.find_one_and_update({"_id":"prices"},{"$set":{item:new_value}})
        except Exception as e:
            print(e)
            updated = False
        
        return updated

    def delete_item(self,category:str,item:str) -> bool:
        """delete chosen item from database"""
        deleted = True
        try:
            self.mdb["fairco"].update_one({"_id":"prices"},{"$unset":{item:True}})
            self.mdb["fairco"].update_one({"_id":"resources"},{"$pull":{category:item}})
        except Exception as e :
            print(e)
            deleted = False

        return deleted

    def get_items_prices(self,category:str) -> dict:
        """view list of item-price of given category from database"""
        items_prices = {}
        mcoll = self.mdb["fairco"]

        items = mcoll.find_one({"_id":"resources"})
        prices = mcoll.find_one({"_id":"prices"})

        for resource in items[category]:
            items_prices[resource]=prices[resource]

        return items_prices
    
    def tablify(self,ip:dict) -> str:
        """turn a dict into a tabulor format"""
        longest = 0
        rsc_list = ""
        for k in ip:
            if len(k)>longest:longest=len(k)
        for rsc in ip:
            temp_rsc = rsc + " "*(longest-len(rsc)+1)+f": {'{:,}'.format(ip[rsc])}"
            rsc_list = rsc_list + temp_rsc + '\n'
        return rsc_list
    
    def make_menu(self,options_list:list[str],ph:str,id:str):
        """create SelectMenu from given parameters"""
        menu_options = []
        for option in options_list:
            menu_options.append(it.SelectOption(label=option,value=option))
        menu = it.SelectMenu(options=menu_options,
                            placeholder=ph,
                            custom_id=id
                            )
        return menu

    def make_choices(choices_list:list[str]):
        """create SelectOption from given parameters"""
        choices = []
        for choice in choices_list:
            choices.append(it.Choice(name=choice,value=choice))
        return choices

    async def insert_modal(self,ctx:CC):
        resource_name_ip = TextInput(
            label="Resource name : ",
            placeholder="Enter resource name",
            style=TextStyleType.PARAGRAPH,
            custom_id="resource_name",
            required=True
            )
        resource_price_ip = TextInput(
            label="Resource name : ",
            placeholder="Enter resource's price",
            style=TextStyleType.SHORT,
            custom_id="resource_price",
            required=True
            )
        modal = Modal(
                title="Inserting a new resource to database",
                components= [resource_name_ip,resource_price_ip],
                custom_id="insert_modal"
            )
        await ctx.popup(modal)

    def embed_maker(self,choice):
        fields = []
        sections = {"green" : [["logs","relics"],0x2A7E19],"grey":[["ores","bars"],0x838579],"blue":[["fish","magic"],0xC2DFFF]}
        section = sections[choice]
        for part in section[0]:
            _resources = self.get_items_prices(part)
            _text = self.tablify(_resources)
            _part = part.replace("_","/").capitalize()
            _field = it.EmbedField(name=f"**{_part}**",value=f"```{_text}```",inline=True)
            #False if section.index(part)==len(section)-1 else True
            fields.append(_field)
        embed = it.Embed(title="Resources' Prices",
                        description="**Prices are subject to change**",
                        fields=fields,
                        color=section[1])
        return embed 


    @interactions.extension_command(
        name="resource", 
        description="modify the resource database",
        scope = [839662151010353172,922854662141526037,712120246915301429],  
        options= [
            it.Option(
                name="update",
                description="update a resource price",
                type=it.OptionType.SUB_COMMAND,
                options=[
                    it.Option(
                        name="category",
                        description="the resource's category",
                        type=it.OptionType.STRING,
                        choices = make_choices(categories),
                        required=True)
                        ]
                    ),
            it.Option(
                name="insert",
                description="insert a new resource into database",
                type=it.OptionType.SUB_COMMAND,
                options=[
                    it.Option(
                        name="category",
                        description="the resource's category",
                        type=it.OptionType.STRING,
                        choices = make_choices(categories),
                        required=True)
                        ]
                    ),
            it.Option(
                name="delete",
                description="delete a resource from database",
                type=it.OptionType.SUB_COMMAND,
                options=[
                    it.Option(
                        name="category",
                        description="the resource's category",
                        type=it.OptionType.STRING,
                        choices = make_choices(categories),
                        required=True)
                        ]
                    ),
            it.Option(
                name="view",
                description="view resources of given category",
                type=it.OptionType.SUB_COMMAND,
                options=[
                    it.Option(
                        name="category",
                        description="the resource's category",
                        type=it.OptionType.STRING,
                        choices = [
                            it.Choice(name="Logs/Relics",value="green"),
                            it.Choice(name="Ores/Bars",value="grey"),
                            it.Choice(name="Magic/Fish",value="blue")
                        ],
                        required=True)
                        ]   
                    )
                ],
        default_member_permissions=it.Permissions.ADMINISTRATOR
            )
    async def resource(self,ctx: CC, sub_command: str, category: str):
        resource_price_ip = TextInput(
                label="Resource's price : ",
                placeholder="Enter resource's price",
                style=TextStyleType.SHORT,
                custom_id=f"{category}_resource_price",
                required=True
                )
        resource_name_ip = TextInput(
                label="Resource's name : ",
                placeholder="Enter resource name",
                style=TextStyleType.PARAGRAPH,
                custom_id=f"{category}_resource_name",
                required=True
                )

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False

        if sub_command == "insert":
            insert_modal = Modal(
                    title="Inserting a new resource to database",
                    components= [resource_name_ip,resource_price_ip],
                    custom_id="insert_modal"
                )
            await ctx.popup(insert_modal)
            modal_ctx: interactions.CommandContext = await wait_for(self.bot, name="on_modal", timeout=60)
            
        elif sub_command == "update":
            resources_list = self.mdb["fairco"].find_one({"_id":"resources"})
            prices = self.mdb["fairco"].find_one({"_id":"prices"})
            resource_menu = self.make_menu(resources_list[category],"Select resource !","rsc_menu")
            await ctx.send("Select resource : ",components= [resource_menu])
            try:
                rsc_ctx = await self.bot.wait_for_component( components=resource_menu, check=check, timeout=60) 
                selected_rsc =  rsc_ctx.data.values[0]
                selected_rsc = selected_rsc.replace(" ","-")
                resource_price_ip.custom_id=f"{category}_{selected_rsc}_resource_name"
                selected_rsc = selected_rsc.replace("-"," ")
                update_modal = Modal(
                    title=f"Updating {selected_rsc}'s price [{prices[selected_rsc]}]",
                    components=[resource_price_ip],
                    custom_id="update_modal"
                )
                await rsc_ctx.popup(update_modal)
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[]) 
            
        elif sub_command == "delete":
            resources_list = self.mdb["fairco"].find_one({"_id":"resources"})

            resource_menu = self.make_menu(resources_list[category],"Select Resource !","rsc_menu")
            self.delete_button.disabled = True
            await ctx.send("Select resource : ",components=[resource_menu])

            try:
                rsc_ctx: CC = await self.bot.wait_for_component( components=resource_menu, check=check, timeout=60) 
                selected_rsc =  rsc_ctx.data.values[0]
                deleted = self.delete_item(category,selected_rsc)
                state = "success" if deleted else "fail"
                await ctx.edit(f"deleting {selected_rsc} was a {state}",components=[])
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[]) 
            
        elif sub_command == "view":
            embed = self.embed_maker(choice=category)
            await ctx.send(embeds=embed)
            
            
      


            
    @interactions.extension_command(
        name="rates", 
        description="modify the rates database",
        scope = [839662151010353172,922854662141526037,712120246915301429],  
        options= [
            it.Option(
                name="insert",
                description="insert a new worker's rate into database",
                type=it.OptionType.SUB_COMMAND
                    ),
            it.Option(
                name="update",
                description="update a worker's rate",
                type=it.OptionType.SUB_COMMAND
                    ),
            it.Option(
                name="delete",
                description="delete a worker's rate from database",
                type=it.OptionType.SUB_COMMAND
                    ),
            it.Option(
                name="view",
                description="view worker's rates",
                type=it.OptionType.SUB_COMMAND   
                    )
                ],
        default_member_permissions=it.Permissions.ADMINISTRATOR
            )
    async def rates(self,ctx: CC, sub_command: str):
        _collection = self.mdb["fairco"]
        raw_rates:dict = _collection.find_one({"_id":"rates"})
        rates = {i:raw_rates[i] for i in raw_rates if i!='_id'}
        tier_list = list(rates.keys())

        tier_name_ip = TextInput(
                label="tier's name : ",
                placeholder="Enter tier's name",
                style=TextStyleType.PARAGRAPH,
                custom_id="tier_name_modal",

                required=True
                )
        tier_value_ip = TextInput(
                label="tier's value : ",
                placeholder="Enter tier's value",
                style=TextStyleType.PARAGRAPH,
                custom_id="tier_value_modal",
                required=True
                )

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False

        if sub_command == "insert":
            insert_modal = Modal(
                    title="Inserting a new Tier to database",
                    components= [tier_name_ip,tier_value_ip],
                    custom_id="insert_tier_modal"
                )
            await ctx.popup(insert_modal)
            modal_ctx: interactions.CommandContext = await wait_for(self.bot, name="on_modal", timeout=60)
            
        elif sub_command == "update":
            tier_menu = self.make_menu(tier_list,"Select Tier !","tiers_menu")
            await ctx.send("Select resource : ",components= [tier_menu])
            try:
                rsc_ctx = await self.bot.wait_for_component( components=tier_menu, check=check, timeout=60) 
                selected_tier =  rsc_ctx.data.values[0]
                _selected_tier = selected_tier.replace(" ","+")
                tier_value_ip.custom_id = f"{_selected_tier}_value_update"
                update_modal = Modal(
                    title=f"Updating {selected_tier}'s rate [{rates[selected_tier]}]",
                    components=[tier_value_ip],
                    custom_id="update_tier_modal"
                )
                await rsc_ctx.popup(update_modal)
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[]) 
            
        elif sub_command == "delete":
            tier_menu = self.make_menu(tier_list,"Select Tier !","tiers_menu")
            self.delete_button.disabled = True
            await ctx.send("Select a Tier to delete : ",components=[tier_menu])

            try:
                rsc_ctx: CC = await self.bot.wait_for_component( components=tier_menu, check=check, timeout=60) 
                selected_tier =  rsc_ctx.data.values[0]

                _collection = self.mdb["fairco"]
                _collection.update_one({"_id":"rates"},{"$unset":{selected_tier:True}})

                await ctx.edit(f"deleted {selected_tier} ",components=[])
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[]) 
            
        elif sub_command == "view":
            
            msg = ""
            for tier in tier_list :
                msg = msg + tier + ' : ' + str(rates[tier]) + "%" + '\n' 
            await ctx.send(msg)

                 
    @interactions.extension_modal("insert_modal")
    async def insert_response(self,ctx:CC,*args):
        
        id:str = ctx.data.components[0].components[0].custom_id
        category = id.split("_")[0]

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False

        name = args[0]
        price = "{:,}".format(int(args[1]))
        msg = f"you entered [{name} : {price}]"
        msg = msg + '\n' + "commit ?"
        await ctx.send(msg,components=[self.commit_button])
        try:
            commit_ctx: CC = await self.bot.wait_for_component( components="commit_btn", check=check, timeout=20) 
            inserted = self.insert_item(category,name,int(args[1]))
            #if inserted:
            await ctx.edit(f"input saved to database",embeds=[], components=[]) #do stuffs here
        except asyncio.TimeoutError: 
            await ctx.edit("timed out!",components=[])

    @interactions.extension_modal("update_modal")
    async def update_response(self,ctx:CC,*args):
        id:str = ctx.data.components[0].components[0].custom_id
        category = id.split("_")[0]
        name = id.split("_")[1].replace("-"," ")

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False


        price = int(args[0])
        msg = f"you entered [{name} : { '{:,}'.format(price)}]"
        msg = msg + '\n' + "commit ?"
        await ctx.send(msg,components=[self.commit_button])
        try:
            commit_ctx: CC = await self.bot.wait_for_component( components="commit_btn", check=check, timeout=20) 
            inserted = self.update_item(name,int(args[0]))
            #if inserted:
            await commit_ctx.edit(f"input updated to database",embeds=[], components=[]) #do stuffs here
        except asyncio.TimeoutError: 
            await ctx.edit("timed out!",components=[])


    

    @interactions.extension_modal("insert_tier_modal")
    async def insert_tier_response(self,ctx:CC,*args):
        new_tier = {args[0]:int(args[1])}

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False

        msg = f"you entered [{args[0]} : {args[1]}]"
        msg = msg + '\n' + "commit ?"
        await ctx.send(msg,components=[self.commit_button])
        if 0 <= int(args[1]) <= 100:
            try:
                commit_ctx: CC = await self.bot.wait_for_component( components="commit_btn", check=check, timeout=20) 
                _collection = self.mdb["fairco"]
                _collection.update_one({"_id":"rates"},{"$set": new_tier})
                await ctx.edit(f"input saved to database",embeds=[], components=[]) #do stuffs here
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[])
        else:
            await ctx.edit("Tier value must be between 100 and 0 !",components=[])

    @interactions.extension_modal("update_tier_modal")
    async def update_rate_response(self,ctx:CC,*args):
        updated_tier = ctx.data.components[0].components[0].custom_id
        updated_tier = updated_tier.split("_")[0].replace("+"," ")
        updated_rate = int(args[0])

        async def check(comp_ctx):
            if int(comp_ctx.author.user.id) == int(ctx.author.user.id):
                return True
            await ctx.send("I wasn't asking you!", ephemeral=True)
            return False

        if 0 <= updated_rate <= 100:
            msg = f"you entered [{updated_tier} : {updated_rate}]"
            msg = msg + '\n' + "commit ?"
            await ctx.send(msg,components=[self.commit_button])
            try:
                commit_ctx: CC = await self.bot.wait_for_component( components="commit_btn", check=check, timeout=20) 
                _collection = self.mdb["fairco"]
                _collection.find_one_and_update({"_id":"rates"},{"$set":{updated_tier:updated_rate}})
                await commit_ctx.edit(f"input updated to database",embeds=[], components=[]) #do stuffs here
            except asyncio.TimeoutError: 
                await ctx.edit("timed out!",components=[])
        else:
            ctx.edit("Tier value must be between 100 and 0 !")





def setup(client : Client):
    MasterUpdater(client)
    print("updater loaded")