import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pymongo import MongoClient

from settings.config import *





class visualizator():

    COLORS = [
        "#d40000",
        "#838383",
        "#F07800",
        "#00c400",
        "#a76906",
        "#004aff",
        "#ecec00",
        "#6a329f"
    ]
    def __init__(self) -> None:
        self.data = {}
        pass
        
    def get_data(self) -> dict:
        _data = MongoClient(CALC_DB_URL)["Miscs"]["UsageData"].find_one({"_id":"data"})
        self.data = _data
    
    def format_perc(self,pct, allvalues):
        absolute = round(pct / 100.*np.sum(allvalues))
        return "{:.1f}%\n({:d} calcs)".format(pct, absolute)

    def create_chart(self,skills_type:str,skills_names:list[str],skills_values:list[str],file_name:str) -> str:
        fig, ax = plt.subplots(figsize =(10, 7))
        wp = { 'linewidth' : 1, 'edgecolor' : "green" ,"alpha": 0.9}
        wedges, texts, autotexts = ax.pie(skills_values,
                                        autopct = lambda pct: self.format_perc(pct, skills_values),
                                        startangle = 90,
                                        wedgeprops = wp,
                                        colors=self.COLORS,
                                        textprops = dict(color ="black")
                                        )

        ax.legend(wedges, skills_names,
                title ="Skills",
                loc ="center left",
                bbox_to_anchor =(1, 0, 0, 1),
                borderpad=2, labelspacing=2)
        placeholder = "Skill Calculations" if skills_type == "calc" else "Guides Skills"
        plt.setp(autotexts, size = 8, weight ="bold")
        ax.set_title(f"{placeholder} Distribution")
        fig.savefig(f"{file_name}.png",transparent=True)
        return f"{file_name}"

    def create_image(self,skills_type:str) -> str:
        self.get_data()
        _file_name = self.create_chart(skills_type=skills_type,skills_names=list(self.data[f"{skills_type}_skills"].keys()),skills_values=list(self.data[f"{skills_type}_skills"].values()),file_name="stats")
        im1 = Image.open('tools/bg.png')
        im2 = Image.open(f"{_file_name}.png")

        im = im1.copy()
        im.paste(im=im2,box=(-200,-20),mask=im2)
        im.save(f"{_file_name}_done.png")
        return f"{_file_name}_done.png"







