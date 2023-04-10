import asyncio
import bisect
from datetime import datetime
import math
from pprint import pprint
import interactions
import interactions as it
from interactions import Client, SelectMenu, SelectOption
from interactions import CommandContext as CC
from interactions import ComponentContext as CPC 
from pymongo import MongoClient



from settings.config import *
from data.resources_data import resources_dict
from data.generals import *
from data.xp_tabs import *


class Guide(interactions.Extension):
    def __init__(self,client: Client,default_channels) -> None:
        self.bot = client
        self.DBclient = MongoClient(DB_URL1)
        self.DB = self.DBclient["Miscs"]
        self.channel_collection = self.DB["config"]
        self.default_channels = default_channels

        return None
    def get_xp(self,curr_lvl:int,tar_lvl:int, curr_per:float=0, tar_per:float=0) -> int:
        """Calculate the xp differance between current level and target level"""
        minxp = lvltab[curr_lvl-1] + (lvldef[curr_lvl-1]*(curr_per/100))
        if tar_lvl == 120:
            bigxp = lvltab[119]
        else:
            bigxp= lvltab[tar_lvl-1] + (lvldef[tar_lvl-1]*(tar_per/100))
        XPneeded = round(bigxp - minxp)
        return XPneeded

    def last_list(self,last_value:int) -> list:
        """return a slice of the list starting from given >= given value"""
        default_lvls = [80,85,90,95,100,110,120]
        idx = bisect.bisect_right(default_lvls, last_value)
        return default_lvls[idx:]

    def create_guide_dict(self,my_dict:dict) -> dict:
        """convert given skill's dict into a guide's dict"""
        handpicked_dict = {}
        for resource in my_dict:
            handpicked_dict[resource] = my_dict[resource]["level"]
        last_key = 0
        swapped_dict = {}
        for key, value in handpicked_dict.items():
            last_key = value
            if value in swapped_dict:
                swapped_dict[value]["resource"].append(key)
                swapped_dict[value]["emoji_name"].append(my_dict[key]["emoji_name"])
                swapped_dict[value]["emoji_id"].append(my_dict[key]["emoji_id"])
            else:
                swapped_dict[value] = {}
                swapped_dict[value]["resource"] = [key] 
                swapped_dict[value]["emoji_name"] = [my_dict[key]["emoji_name"]]
                swapped_dict[value]["emoji_id"] = [my_dict[key]["emoji_id"]]
                swapped_dict[value]["xp"] = my_dict[key]["xp"]
        _list = self.last_list(last_value=last_key)
        for key in _list:
            swapped_dict[key] = swapped_dict[last_key].copy()
        final_dict = {}
        curr_lvls = list(swapped_dict.keys())
        for idx in range(len(curr_lvls)-1):
            total_xp = 0
            final_dict[f'Lv.{curr_lvls[idx]}-->Lv.{curr_lvls[idx+1]}'] = swapped_dict[curr_lvls[idx]]
            total_xp = self.get_xp(curr_lvl=curr_lvls[idx],tar_lvl=curr_lvls[idx+1])
            final_dict[f'Lv.{curr_lvls[idx]}-->Lv.{curr_lvls[idx+1]}']["total_xp"] = total_xp
            final_dict[f'Lv.{curr_lvls[idx]}-->Lv.{curr_lvls[idx+1]}']["quantity"] = math.ceil(total_xp / swapped_dict[curr_lvls[idx]]["xp"])
        return final_dict

    def split_list(self,lst):
        num_items = len(lst)
        third = num_items // 3
        
        if num_items % 3 == 0:
            first = third
            second = 2 * third
        elif num_items % 3 == 1:
            first = third + 1
            second = 2 * third + 1
        else:
            first = third + 1
            second = 2 * third + 2
    
        return lst[:first], lst[first:second], lst[second:]

    def format_field(self,guide_dict:dict,column_idx:str,boost_value:float):

        quantity = math.ceil(guide_dict[column_idx]['quantity'] / boost_value)
        rsc1 = f"[<:{guide_dict[column_idx]['emoji_name'][0]}:{guide_dict[column_idx]['emoji_id'][0]}>]{guide_dict[column_idx]['resource'][0]}" if len(guide_dict[column_idx]['resource']) == 1 else f"[<:{guide_dict[column_idx]['emoji_name'][0]}:{guide_dict[column_idx]['emoji_id'][0]}>]{guide_dict[column_idx]['resource'][0]}/\n/[<:{guide_dict[column_idx]['emoji_name'][1]}:{guide_dict[column_idx]['emoji_id'][1]}>]{guide_dict[column_idx]['resource'][1]}"
        _field = it.EmbedField(name=column_idx,value=f"{rsc1} :: {quantity:,}\n[XP: {guide_dict[column_idx]['total_xp']:,}]")
        _field.inline = True

        return _field
        
    def create_guide_fields(self,guide_dict:dict,boost_value:float) -> list:
        """convert raw guide's dict into fields's list of guide embed"""
        keys = list(guide_dict.keys())
        column1, column2, column3 = self.split_list(keys)
        fields = []
        for idx in range(len(column3)):
            _field1 = self.format_field(guide_dict=guide_dict,column_idx=column1[idx],boost_value=boost_value)
            fields.append(_field1)

            _field2 = self.format_field(guide_dict=guide_dict,column_idx=column2[idx],boost_value=boost_value)
            fields.append(_field2)

            _field3 = self.format_field(guide_dict=guide_dict,column_idx=column3[idx],boost_value=boost_value)
            fields.append(_field3)

        if len(column1)-len(column2) == 1:
            _field1 = self.format_field(guide_dict=guide_dict,column_idx=column1[-1],boost_value=boost_value)
            fields.append(_field1)

        if len(column2) - len(column3) == 1:
            _field1 = self.format_field(guide_dict=guide_dict,column_idx=column1[-1],boost_value=boost_value)
            fields.append(_field1)

            _field2 = self.format_field(guide_dict=guide_dict,column_idx=column2[-1],boost_value=boost_value)
            fields.append(_field2)

            fields.append(it.EmbedField(name="** **",value="** **",inline=True))

        return fields

    def defaultize(self,options:list[SelectOption],default_idxs:list[int]) -> list[SelectOption]:
        for idx in range(len(options)):
            options[idx].default = True if idx in default_idxs else False
        return None

    def get_default(self,options:list[SelectOption]) -> str:
        for option in options:
            if option.default :
                return option.value

    def get_multi_default(self,options:list[SelectOption]) -> list[str]:
        values:list[str] = []
        for option in options:
            if option.default :
                values.append(option.value)
        return values

    def make_boost_menu(self,skill_name:str) -> SelectMenu:
        boost_dict = {"mining": 3,"smithing": 4}
        
        temp_list:list[SelectOption] = []
        for boost  in skills_boosts[skill_name]:
            temp_list.append(it.SelectOption(
                                            label=boost,
                                            value=boost,
                                            emoji=it.Emoji(
                                                name=boosts[boost]["emoji_name"],
                                                id=boosts[boost]["emoji_id"])
                                            )
                            )
        temp_list[0].default = True
        menu = it.SelectMenu(
                            options=temp_list,
                            placeholder="Select Boost !",
                            custom_id=f"guide_boost_menu_{skill_name}"
                            )
        menu.max_values = boost_dict[skill_name] if skill_name in boost_dict else 2
        menu.min_values = 1
        return menu

    def get_total_boost_value(self,boost_list:list[str]) -> float:
        boost_value = 1.00
        for boost in boost_list:
            boost_value = boost_value * boosts[boost]['value']
        return boost_value

    def get_boosts_text(self,boosts_list:list[str]) -> str:
        _boosts_str = "Boosts Selected :\n"
        for boost in boosts_list:
            _boosts_str = _boosts_str + f"[{boosts[boost]['str_form']}] {boost}\n"
        return _boosts_str

    def update_analytics(self,skill_type:str,skill_name:str) -> None:
        try:
            _collection = self.DB["UsageData"]
            skill = f"{skill_type}_skills.{skill_name.lower()}"
            _collection.update_one({ "_id": "data" },{ "$inc": { f"{skill_type}": 1, skill: 1} })
        except Exception as e :
            print(e)
        return None

    def check_channel(self,guild_id:str,channel_id:int) -> bool:
        
        if guild_id in self.default_channels:
            if channel_id in self.default_channels[guild_id]:
                return [True]
            else:
                return [False,self.default_channels[guild_id]]
        else:
            return [None]


    @interactions.extension_command(
        name="guides",
        description="create a guide for given skill",
        options=[
            it.Option(
                name="skill",
                description="the skill of the guide",
                required=True,
                type=it.OptionType.STRING,
                choices=[
                    it.Choice(name="Mining",value="mining"),
                    it.Choice(name="Smithing",value="smithing"),
                    it.Choice(name="Woodcutting",value="woodcutting"),
                    it.Choice(name="Crafting",value="crafting"),
                    it.Choice(name="Fishing",value="fishing"),
                    it.Choice(name="Cooking",value="cooking"),
                    it.Choice(name="Tailoring",value="tailoring"),
                ]
            )
        ]
    )
    async def guides(self,ctx:CC,skill:str):
        ######################################
        channel_state = self.check_channel(guild_id=str(ctx.guild_id),channel_id=int(ctx.channel_id))

        if channel_state[0] == False:
            channel_ids = channel_state[1]
            channel_tags = [f"<#{channel_ids[_id]}>" for _id in range(len(channel_ids))]
            tags = " or ".join(channel_tags)
            await ctx.send(content=f"you can't use me here, go to {tags} please",ephemeral=True)
            return
        #####################################
        self.update_analytics(skill_type="guides",skill_name=skill)
        skill_dict = resources_dict[skill]
        _guide_dict = self.create_guide_dict(skill_dict)
        guide_embed = it.Embed()
        guide_embed.title = f"{skill}'s guide".title()
        guide_embed.description = f"Boosts Selected :\n[{boosts['NoBoost']['str_form']}] NoBoost"
        guide_embed.fields = self.create_guide_fields(guide_dict=_guide_dict,boost_value=1.0)
        guide_menu = self.make_boost_menu(skill)
        time = datetime.today()
        guide_menu.custom_id = f"guide_boost_menu_{skill}_{time}"

        await ctx.send("Guiding ...",embeds=[guide_embed],components=[guide_menu])
        

        
    @interactions.extension_listener()
    async def on_component(self,ctx:CPC,*args):
        if ctx.custom_id.startswith("guide_boost_menu_"):
            _embed = ctx.message.embeds[0]

            selected_boosts = ctx.data.values
            _boost_value = self.get_total_boost_value(selected_boosts)
            skill_name = ctx.custom_id.split("_")[3]
            
            selected_idxs = []
            for selected_boost in ctx.data.values:
                selected_idxs.append(int(skills_boosts[skill_name].index(selected_boost)))
            compos = ctx.message.components
            self.defaultize(compos[0].components[0].options,default_idxs=selected_idxs)

            _guide_dict = self.create_guide_dict(resources_dict[skill_name])
            _embed.fields = self.create_guide_fields(guide_dict=_guide_dict,boost_value=_boost_value)

            _boost_text = self.get_boosts_text(selected_boosts)
            _embed.description = _boost_text


            await ctx.edit("Guiding ...",embeds=[_embed],components=compos)

def setup(client:Client,default_channels):
    Guide(client,default_channels)
    print("compass loaded")



