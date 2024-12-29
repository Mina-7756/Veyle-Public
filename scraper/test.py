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
    "Fomortiis:_Dark_of_Night",
    "Alear:_Gifted_Dragons",
    "Eikþyrnir:_Blessed_Strength",
    "Shez:_Snowfield_Envoy",
    "Hortensia:_Winter's_Dearest"
]



#alts = None
alts = ["Winter", "Christmas", "W"]
for i in range(0, len(units)):
    Webscraper.scrape_page(f"/wiki/{units[i]}", alts=alts)
    

#with open(file, 'w') as fp:
    #json.dump(obj, fp)





    
  



