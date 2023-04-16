import asyncio
from datetime import datetime
import math
import os
import time
import interactions
import interactions as it
from interactions.ext.wait_for import setup
from interactions import Client, Embed, Button, ButtonStyle, Emoji, SelectMenu, SelectOption, ActionRow, Modal, TextInput,TextStyleType
from interactions import CommandContext as CC
from interactions import ComponentContext as CPC
from pymongo import MongoClient


from data.xp_tabs import *
from settings.config import *
from data.resources_data import resources_dict
from data.generals import *
from data.combat import *


class Calculator(interactions.Extension):
    def __init__(self,client: Client,default_channel) -> None:
        self.bot = client
        self.calc_butt = Button(style=ButtonStyle.SUCCESS,label="Calc")
        self.finish_butt = Button(style=ButtonStyle.DANGER,label="finish")
        self.skill_menu = it.SelectMenu(
                        options=[
                            it.SelectOption(
                                            label="Combat",
                                            value="combat",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Combat"]["emoji_name"],
                                                        id=skills_emoji["Combat"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Mining",
                                            value="mining",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Mining"]["emoji_name"],
                                                        id=skills_emoji["Mining"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Smithing",
                                            value="smithing",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Smithing"]["emoji_name"],
                                                        id=skills_emoji["Smithing"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Woodcutting",
                                            value="woodcutting",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Woodcutting"]["emoji_name"],
                                                        id=skills_emoji["Woodcutting"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Crafting",
                                            value="crafting",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Crafting"]["emoji_name"],
                                                        id=skills_emoji["Crafting"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Fishing",
                                            value="fishing",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Fishing"]["emoji_name"],
                                                        id=skills_emoji["Fishing"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Cooking",
                                            value="cooking",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Cooking"]["emoji_name"],
                                                        id=skills_emoji["Cooking"]["emoji_id"]
                                                            )
                                            ),
                            it.SelectOption(
                                            label="Tailoring",
                                            value="tailoring",
                                            emoji=it.Emoji(
                                                        name=skills_emoji["Tailoring"]["emoji_name"],
                                                        id=skills_emoji["Tailoring"]["emoji_id"]
                                                            )
                                            )
                        ],
                        placeholder="Select Skill !"
                            )
        self.DBclient = MongoClient(DB_URL1)
        self.DB = self.DBclient["Miscs"]
        self.default_channels = default_channel
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

    def get_menus(self,skill_name:str,user_id:int,location:str="Bright Leaf") -> list[ActionRow]:
        if skill_name == 'combat':
            loc_menu = self.make_loc_menu(user_id=user_id)
            mob_menu = self.make_mob_menu(location=location,user_id=user_id)
            boost_menu = self.make_boost_menu(skill_name=skill_name,user_id=user_id)

            return [ActionRow(components=[loc_menu]),ActionRow(components=[mob_menu]),ActionRow(components=[boost_menu])]

        else:
            rsc_menu = self.make_rsc_menu(skill_name=skill_name,user_id=user_id)
            boost_menu = self.make_boost_menu(skill_name=skill_name,user_id=user_id)

            return [ActionRow(components=[rsc_menu]),ActionRow(components=[boost_menu])]

    def make_rsc_menu(self,skill_name:str,user_id:int) -> SelectMenu:
        temp_list:list[SelectOption] = []
        for resource in resources_dict[skill_name]:
            temp_list.append(it.SelectOption(
                                            label=resource,
                                            value=resource,
                                            emoji=it.Emoji(
                                                        name=resources_dict[skill_name][resource]["emoji_name"],
                                                        id=resources_dict[skill_name][resource]["emoji_id"]
                                                            )
                                            )
                            )
        temp_list[0].default = True
        menu = it.SelectMenu(
                        options=temp_list,
                        placeholder="Select Resource !",
                        custom_id=f"rsc_menu_{skill_name}_id_{user_id}"
                            )
        return menu

    def make_boost_menu(self,skill_name:str,user_id:int) -> SelectMenu:
        boost_dict = {"combat": 3,"mining": 2,"smithing": 3}
        
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
                            custom_id=f"boost_menu_{skill_name}_id_{user_id}"
                            )
        if skill_name in boost_dict:
            max_value = boost_dict[skill_name]
            menu.max_values = max_value
            menu.min_values = 1
        return menu

    def make_loc_menu(self,user_id:int) -> SelectMenu:
        temp_list:list[SelectOption] = []
        for location in combat_dict :
            temp_list.append(it.SelectOption(
                                            label=location,
                                            value=location,
                                            emoji=it.Emoji(
                                                name = combat_dict[location]["emoji_name"],
                                                id = combat_dict[location]["emoji_id"])
                                            )
                            )
        temp_list[0].default = True
        menu = it.SelectMenu(
                        options=temp_list,
                        placeholder="Select Location !",
                        custom_id=f"loc_menu_combat_id_{user_id}"
                            )
        return menu

    def make_mob_menu(self,location:str,user_id:int) -> SelectMenu:
        temp_list:list[SelectOption] = []
        for mob in combat_dict[location]["mobs"]:
            temp_list.append(it.SelectOption(
                                            label=mob,
                                            value=mob,
                                            emoji=it.Emoji(
                                                name=combat_dict[location]["mobs"][mob]["emoji_name"],
                                                id=combat_dict[location]["mobs"][mob]["emoji_id"]
                                                            )
                                            )
                            )      
        temp_list[0].default = True
        menu = it.SelectMenu(
                        options=temp_list,
                        placeholder="Select Mob !",
                        custom_id=f"mob_menu_id_{user_id}"
                            )
        return menu

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

    def do_embed(self,skill_name:str="",rsc:str="",boost:str="",quantity:str="",lvls:list=[]) -> Embed:
        element_type = "Mob" if skill_name == "combat" else "Resource"
        embed_body = f"{element_type} ::\n{rsc}\nBoost ::\n{boost}\nQuantity ::\n{quantity}"
        if skill_name not in ["combat","mining","woodcutting"]:
            embed_body = embed_body + "\nMaterials ::\n "
        embed = Embed(
                        title=f"Skill : {skill_name.capitalize()}",
                        description = embed_body
                            )
        embed.set_footer(text=f"{lvls[0]}-{lvls[1]}% --> {lvls[2]}-{lvls[3]}%\nXP needed : {lvls[4]:,}")
        return embed

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

    def get_total_boost_value(self,boost_list:list[str]) -> float:
        boost_value = 1.00
        for boost in boost_list:
            boost_value = boost_value * boosts[boost]['value']
        return boost_value

    def get_boosts_text(self,boosts_list:list[str],quantity:int) -> str:
        _boosts_str = ""
        for boost in boosts_list:
            _charges = ""
            if boost in ["Inf Hammer","Inf Ring","Pros Neck"]:
                _charges = f' : {math.ceil(quantity/boosts[boost]["charges"]):,}'
            _boosts_str += f'[<:{boosts[boost]["emoji_name"]}:{boosts[boost]["emoji_id"]}>{boost}]{_charges}\n'
        return _boosts_str






    @interactions.extension_command(
        name="calc",
        description="Calculate the resourses needed to get from your current level to a target level",
        options=[
            it.Option(
                    name="current_lvl",
                    description="your current lvl",
                    type=it.OptionType.INTEGER,
                    required=True,
                    min_value=1,
                    max_value=120
                    ),
            it.Option(
                    name="target_lvl",
                    description="your target lvl",
                    type=it.OptionType.INTEGER,
                    required=True,
                    min_value=1,
                    max_value=120
                    ),
            it.Option(
                    name="current_perc",
                    description="your current %",
                    type=it.OptionType.NUMBER,
                    required=False,
                    min_value=0,
                    max_value=100
                    ),
            it.Option(
                    name="target_perc",
                    description="your target %",
                    type=it.OptionType.NUMBER,
                    required=False,
                    min_value=0,
                    max_value=100
                    )
                ]
    )
    async def calc(self,ctx:CC,current_lvl:int=0,target_lvl:int=0,current_perc:float=0,target_perc:float=0):
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
        
        async def check(comp_ctx: CPC):
            if int(comp_ctx.author.user.id) != int(ctx.author.user.id):
                await comp_ctx.send("I wasn't asking you!", ephemeral=True)
                return False
            return True




        xp_needed = self.get_xp(curr_lvl=current_lvl,tar_lvl=target_lvl,curr_per=current_perc,tar_per=target_perc)
        menu = self.skill_menu
        time = datetime.today()
        menu.custom_id = f"skill_menu_{time}_id_{ctx.user.id}"
        await ctx.send("select skill", components=[menu])
        try:
            skill_ctx = await self.bot.wait_for_component( components=menu, check=check, timeout=30)
            skill_name=skill_ctx.data.values[0]

            menus:list[ActionRow] = self.get_menus(skill_name=skill_name,user_id=ctx.user.id)

            calc_butt = self.calc_butt
            finish_butt = self.finish_butt
            calc_butt.custom_id = f"calc_id_{ctx.user.id}"
            finish_butt.custom_id = f"finish_id_{ctx.user.id}"
            menus.append(ActionRow(components=[calc_butt,finish_butt]))
            await skill_ctx.edit(
                                "Calculating ...",
                                embeds=[self.do_embed(skill_name=skill_name,rsc="",boost="",quantity="",lvls=[current_lvl,current_perc,target_lvl,target_perc,xp_needed])],
                                components=menus
                        )
        except asyncio.TimeoutError: 
                await ctx.edit("timed out !",components=[])

    @interactions.extension_listener()
    async def on_component(self,ctx:CPC,*args):
        if int(ctx.author.user.id) != int(ctx.custom_id.split("_id_")[1]):
                return await ctx.send("I wasn't asking you!", ephemeral=True)
                
        if ctx.custom_id.startswith("rsc_menu"):
            selected_rsc = ctx.data.values[0]
            skill_name = ctx.custom_id.split("_")[2]
            selected_idx = list(resources_dict[skill_name].keys()).index(selected_rsc)
            compos = ctx.message.components
            self.defaultize(options=compos[0].components[0].options,default_idxs=[selected_idx])
            await ctx.edit("Calculating...",components=compos)
        
        if ctx.custom_id.startswith("loc_menu"):
            location = ctx.data.values[0]
            selected_idx = list(combat_dict.keys()).index(location)
            compos = ctx.message.components
            self.defaultize(compos[0].components[0].options,default_idxs=[selected_idx])
            mob_menu = self.make_mob_menu(location=location)
            compos = ctx.message.components
            compos[1] = ActionRow(components=[mob_menu])
            await ctx.edit("calculation ...",components=compos)
        
        if ctx.custom_id.startswith("mob_menu"):
            selected_mob = ctx.data.values[0]
            selected_loc = self.get_default(ctx.message.components[0].components[0].options)
            selected_idx = list(combat_dict[selected_loc]['mobs'].keys()).index(selected_mob)
            compos = ctx.message.components
            self.defaultize(compos[1].components[0].options,default_idxs=[selected_idx])
            await ctx.edit("Calculating ...",components=compos)

        if ctx.custom_id.startswith("boost_menu"):
            selected_boosts = ctx.data.values
            skill_name = ctx.custom_id.split("_")[2]
            comp_idx = 2 if skill_name == "combat" else 1
            selected_idxs = []
            for selected_boost in selected_boosts:
                selected_idxs.append(int(skills_boosts[skill_name].index(selected_boost)))
            compos = ctx.message.components
            self.defaultize(compos[comp_idx].components[0].options,default_idxs=selected_idxs)
            await ctx.edit("Calculating ...",components=compos)

        if ctx.custom_id.startswith("calc"):
            skill_name = ctx.message.components[0].components[0].custom_id.split("_")[2]
            rsc_idx = 1 if skill_name == 'combat' else 0
            boost_idx = 2 if skill_name == 'combat' else 1

            if skill_name == "combat":
                element_type = "Mob"
                selected_loc = self.get_default(ctx.message.components[0].components[0].options)
                selected_rsc = self.get_default(ctx.message.components[1].components[0].options)
                rsc_xp = combat_dict[selected_loc]["mobs"][selected_rsc]["xp"]
                rsc_emoji_name = combat_dict[selected_loc]["mobs"][selected_rsc]["emoji_name"] 
                rsc_emoji_id = combat_dict[selected_loc]["mobs"][selected_rsc]["emoji_id"] 
                
            else:
                element_type = "Resource"
                selected_rsc = self.get_default(ctx.message.components[rsc_idx].components[0].options)
                rsc_xp = resources_dict[skill_name][selected_rsc]['xp']
                rsc_emoji_name = resources_dict[skill_name][selected_rsc]['emoji_name']
                rsc_emoji_id = resources_dict[skill_name][selected_rsc]['emoji_id']

            _selected_boosts = self.get_multi_default(ctx.message.components[boost_idx].components[0].options)
            rsc_emoji = Emoji(name=rsc_emoji_name,id=rsc_emoji_id)
                
            xp_needed = int(ctx.message.embeds[0].footer.text.split(" ")[5].replace(",",""))
            boost_value = self.get_total_boost_value(_selected_boosts)
            quantity_needed = math.ceil(xp_needed / (rsc_xp*boost_value))

            _boosts_text = self.get_boosts_text(boosts_list=_selected_boosts,quantity=quantity_needed)

            embed = ctx.message.embeds[0]
            embed.description = f"{element_type} ::\n[{rsc_emoji.format}][{selected_rsc}]\nBoost ::\n{_boosts_text}Quantity ::```{quantity_needed:,}```"
            if skill_name not in ["combat","mining","woodcutting"]:
                mats = resources_dict[skill_name][selected_rsc]["submaterials"]
                mats_txts = []
                for mat in mats:
                    _mat_quantity = quantity_needed * mats[mat]["quantity"]
                    mats_txts.append(f'[{mats[mat]["emoji_str"]}]{mat} : {_mat_quantity:,}')
                mats_txt = "\n" + "\n".join(mats_txts)
                embed.description += f'Materials ::{mats_txt}'
            compos = ctx.message.components
            await ctx.edit("Calculating ...",embeds=[embed],components=compos)
            self.update_analytics(skill_type="calc",skill_name=skill_name)

        if ctx.custom_id.startswith("finish"):
            await ctx.edit("finished", components = [])


def setup(client:Client,default_channels):
    Calculator(client,default_channels)
    print("calc loaded")

