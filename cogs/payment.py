import interactions
import interactions as it
from interactions import Client
from interactions import CommandContext as CC
from interactions import ComponentContext as CPC

import asyncio
import interactions.ext.wait_for
from interactions.ext.wait_for import wait_for_component, wait_for

from settings.config import *

import pymongo



class ATM(interactions.Extension):

    def __init__(self,client : Client) -> None:
        self.bot = client
        self.mclient = pymongo.MongoClient(DB_URL0)
        self.mdb = self.mclient["Company"]



    def calc(self,tier:str,items:dict[str,int]) -> dict[str,int]:
        """calculate the payment of given list of resources for given worker's tier"""
        payment = {}
        prices_list = self.mdb["fairco"].find_one({"_id":"prices"})
        _rates = self.mdb["fairco"].find_one({"_id":"rates"})
        rate = _rates[tier]
        for item in items:
            price = prices_list[item.lower()]
            payment[item] = int(items[item] * price * rate / 100)
        return payment







    # /pay [worker_tier] [item1] [quantity1] [item2]* [quantity2]* [item3]* [quantity3]*

    @interactions.extension_command(   
                    name="pay", 
                    description="calculate worker's payment", 
                    scope = [839662151010353172,922854662141526037,712120246915301429 ],
                    options=[
                        it.Option(
                            name="worker_tier",
                            description="the tier of the worker payed",
                            type=it.OptionType.STRING,
                            required=True,
                            autocomplete=True
                        ),
                        it.Option(
                            name='item1',
                            description="1st item",
                            type=it.OptionType.STRING,
                            required=True,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity1",
                            description="1st item's quantity",
                            type=it.OptionType.INTEGER,
                            required=True,
                        ),
                        it.Option(
                            name='item2',
                            description="2nd item",
                            type=it.OptionType.STRING,
                            required=False,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity2",
                            description="2nd item's quantity",
                            type=it.OptionType.INTEGER,
                            required=False,
                        ),
                        it.Option(
                            name='item3',
                            description="3rd item",
                            type=it.OptionType.STRING,
                            required=False,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity3",
                            description="3rd item's quantity",
                            type=it.OptionType.INTEGER,
                            required=False,
                        ),
                        it.Option(
                            name='item4',
                            description="4th item",
                            type=it.OptionType.STRING,
                            required=False,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity4",
                            description="4th item's quantity",
                            type=it.OptionType.INTEGER,
                            required=False,
                        ),
                        it.Option(
                            name='item5',
                            description="5th item",
                            type=it.OptionType.STRING,
                            required=False,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity5",
                            description="5th item's quantity",
                            type=it.OptionType.INTEGER,
                            required=False,
                        ),
                        it.Option(
                            name='item6',
                            description="6th item",
                            type=it.OptionType.STRING,
                            required=False,
                            autocomplete=True
                        ),
                        it.Option(
                            name="quantity6",
                            description="6th item's quantity",
                            type=it.OptionType.INTEGER,
                            required=False,
                        ),
                            ],
                    default_member_permissions=it.Permissions.ADMINISTRATOR
                )
    async def pay(self,ctx:CC,worker_tier:str,item1:str,quantity1:int,**kwargs):
        await ctx.defer()
        items_count = (len(kwargs)//2) + 1
        items = {kwargs[f'item{idx}'] : kwargs[f'quantity{idx}'] for idx in range(2,items_count+1)}
        items[item1] = quantity1
        payment = self.calc(tier=worker_tier,items=items)
        payment_txt = ""
        for item in payment:
            payment_txt = payment_txt + f"Payment for {items[item]:,} {item.title()} for {worker_tier.title()} is {payment[item]:,}\n"
        total_payment = sum(list(payment.values()))
        payment_txt = payment_txt + f"Total payment is : {total_payment:,}"

        await ctx.send(payment_txt)




    @pay.autocomplete("worker_tier")
    async def place_order_autocomplete(self,ctx: CC, user_input: str = ""):
        items = list(self.mdb["fairco"].find_one({"_id":"rates"}).keys())
        items.remove("_id")
        choices = [
            it.Choice(name=item.title(), value=item) for item in items if user_input in item 
        ] 
        await ctx.populate(choices)


    @pay.autocomplete("item1")
    @pay.autocomplete("item2")
    @pay.autocomplete("item3")
    @pay.autocomplete("item4")
    @pay.autocomplete("item5")
    @pay.autocomplete("item6")
    async def place_order_autocomplete(self,ctx: CC, user_input: str = ""):
        items = list(self.mdb["fairco"].find_one({"_id":"prices"}).keys())
        items.remove("_id")
        choices = [
            interactions.Choice(name=item.title(), value=item) for item in items if user_input in item 
        ] 
        await ctx.populate(choices)




def setup(client : Client):
    ATM(client)
    print("payment loaded")
    