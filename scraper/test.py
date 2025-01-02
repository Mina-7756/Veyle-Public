import Webscraper

import weapon
import json
import skill_scrape

obj = {}

file =  './sk.json'


#skill_scrape.upgrade_sp('Brutal Shell+')
#skill_scrape.upgrade_passive('Worldbreaker+')

with open(file, 'w') as fp:
    json.dump(obj, fp)
    


units = [
    "Heiðrún: Sisters of Healing",
    "Hræsvelgr: Wings of Healing",
    "Níðhöggr: Daze of Healing",
    "Tana: Soaring New Year"
]



alts = ["New Year", "New Years", "NY"]  # 'None' (as in null) uses defaults such as "normal" and "regular". use [] for no alts. maybe this is unintuitive.
#alts = ["Winter", "Christmas", "W"]

version = None  # will calculate the book & chapter the game is currently on when this is run
#version = "9.0"

for i in range(0, len(units)):
    Webscraper.scrape_page(f"/wiki/{units[i]}", alts=alts, version=version)
    

#with open(file, 'w') as fp:
    #json.dump(obj, fp)





    
  



