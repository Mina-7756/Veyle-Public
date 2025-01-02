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
    "Hector: Steel Warrior",
    "Leila: Superb Shadow",
    "Rune: Source of Wisdom",
    "Uther: Frugal Militarist"
]



alts = None     # uses defaults such as "normal" and "regular", use [] for no alts, maybe this is unintuitive.
#version = None  # will calculate the book & chapter the game is currently on when this is run
#alts = ["Winter", "Christmas", "W"]
version = "9.0"
for i in range(0, len(units)):
    Webscraper.scrape_page(f"/wiki/{units[i]}", alts=alts, version=version)
    

#with open(file, 'w') as fp:
    #json.dump(obj, fp)





    
  



