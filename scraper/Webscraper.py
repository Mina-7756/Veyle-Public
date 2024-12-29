import requests
import maps
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
import json
import portrait
import utility


obj = {}

def determine_key(name): 
    ref = []
    with open('../database/feh/char.json', 'r') as f:
        char = json.load(f)
    try_key = name.lower()
    try_key = utility.compress(try_key)
    all_keys = char.keys()
    obj_keys = obj.keys()
    all_keys = list(all_keys) + list(obj_keys)
    if try_key not in all_keys:
        return try_key, ref
    i = 2
    while try_key in all_keys: 
        ref.append(try_key)
        try_key = name.lower() + str(i)
        i = i+1

    return try_key, ref

def scrape_page(page_name, alts=None):
    if alts is None:
        alts = ["Base, Normal, Regular"]

    maindis = ""

    with open('templates/blank.json', 'r') as f:
        template = json.load(f)
    blank = template
    # Follow the same steps for feheroes.fandom
    fandom = requests.get(f'https://feheroes.fandom.com{page_name}')
    soup = BeautifulSoup(fandom.text, 'html.parser')

    # The information we want on the page is stored under '<div role="document" class="page">
    document = soup.find(class_="mw-parser-output")

    # get the name and title of the unit and append both to the wiki_info
    wiki_info = document.find(class_="wikitable hero-infobox").find_all('tr')

    blank['name'] = list(wiki_info[0].stripped_strings)[0]
    mainkey, blank['reference'] = determine_key(blank['name'])
    ogname = list(wiki_info[0].stripped_strings)[0]
    blank['title'] = list(wiki_info[0].stripped_strings)[1]

    art = list(wiki_info[1].stripped_strings)  # art
    art_full = wiki_info[1]
    atags = art_full.find_all('a')

    blank['images']['portrait'] = atags[0]['href']
    blank['images']['attack'] = atags[1]['href']
    blank['images']['special'] = atags[2]['href']
    blank['images']['damage'] = atags[3]['href']

    blank['artist'] = art[5]
    blank['description'] = list(wiki_info[2].stripped_strings)[1]

    if "Female units" in soup.text:
        blank['gender'] = 'F'
    if "Male units" in soup.text:
        if blank['gender']:
            # We got both? Duo maybe? Dunno what the protocol is, marking blank.
            blank['gender'] = ''
        else:
            blank['gender'] = 'M'

    rarity = list(wiki_info[3].stripped_strings)

    if 'Rearmed' in rarity:
        blank['type'] = 'rearmed'
        blank['pool'] = 'focus'
        maindis = 'Rearmed '
        alts.append('Rearmed')
        alts.append('Rearm')
        alts.append('Arm')
        blank['rarity'] = 5
    if 'Attuned' in rarity:
        blank['type'] = 'attuned'
        blank['pool'] = 'focus'
        maindis = 'Attuned '
        alts.append('Attuned')
        blank['rarity'] = 5
    if 'Aided' in rarity:
        blank['type'] = 'aided'
        blank['pool'] = 'focus'
        maindis = 'Aided '
        alts.append('Aided')
        alts.append('Aid')
        blank['rarity'] = 5
    if 'Ascended' in rarity:
        blank['type'] = 'ascended'
        blank['pool'] = 'global'
        alts.append('Ascended')
        alts.append('Ascendant')
        alts.append('Ascendent')
        maindis = 'Ascended '
        blank['rarity'] = 5
    if 'Legendary' in rarity or 'Mythic' in rarity:
        blank['type'] = 'legendary'
        blank['pool'] = 'legend'
        blank['rarity'] = 5
    if 'Emblem' in rarity:
        blank['type'] = 'emblem'
        blank['pool'] = 'legend'
        alts.append('Emblem')
        alts.append('Engage')
        alts.append('E')
        maindis = 'Emblem '
        blank['rarity'] = 5
    if 'Special' in rarity:
        blank['pool'] = 'seasonal'
    if 'SR' in rarity:
        blank['pool'] = 'special'
    if 'Grand Hero Battle' in rarity:
        blank['pool'] = 'grail'
        blank['rarity'] = 3
    if 'Tempest Trials' in rarity:
        blank['pool'] = 'grail'
        blank['rarity'] = 4

    # Next up, find the weapon type. Start by finding the release date
    for i in wiki_info:
        if "Weapon Type" in i.text:
            strings = list(i.stripped_strings)
            blank['weapon'] = strings[1]
        if "Move Type" in i.text:
            strings = list(i.stripped_strings)
            blank['move'] = strings[1]
        if "EN" in i.text and "INTELLIGENT SYSTEMS" not in i.text:
            strings = list(i.stripped_strings)
            if len(strings) >= 5:
                blank['voice'] = (strings[2] + ' ' + strings[3] + ' ' + strings[4])
            else:
                try:
                    blank['voice'] = strings[2]
                except IndexError:
                    blank['voice'] = "Not yet recorded."
        if "Entry" in i.text:
            strings = list(i.stripped_strings)
            blank['origin'] = strings[1]
        if "Entries" in i.text:
            strings = list(i.stripped_strings)
            strings.pop(0)
            blank['origin'] = ' + '.join(strings)
        if "Version" in i.text:
            strings = list(i.stripped_strings)
            ver = strings[1].split('.')[0]

            month = datetime.now().month
            if (month == 12):
                month = 0
            
            blank['version'] = ver + '.' + str(month)
        if "Internal" in i.text and 'Enemy' not in i.text:
            strings = list(i.stripped_strings)
            blank['internal_id'] = strings[1]
            blank['id'] = strings[2][1:-1]
        if "Legendary Effect" in i.text:
            strings = list(i.stripped_strings)
            blank['blessing'] = strings[1]
        if "Mythic Effect" in i.text and '2' not in i.text:
            strings = list(i.stripped_strings)
            blank['blessing'] = strings[1]

        if "Ally Boost" in i.text:
            strings = list(i.stripped_strings)
            boosts = strings[1].split(',')
            temp = {}
            for j in boosts:
                parts = j.split('+')
                temp[parts[0].lower()] = int(parts[1])
            blank['boost'] = temp
        if 'Duo Skill' in i.text:
            strings = list(i.stripped_strings)

            strings.pop(0)
            strings.pop(0)
            strings = utility.removeDuplicates(strings)
            temp = '\n'.join(strings)
            temp.replace('\nPair Up\n.)', ' Pair Up.)')
            blank['duo'] = temp
        if 'Harmonized Skill' in i.text:
            strings = list(i.stripped_strings)

            strings.pop(0)
            strings.pop(0)
            strings = utility.removeDuplicates(strings)
            temp = '\n'.join(strings)
            temp.replace('\nPair Up\n.)', ' Pair Up.)')
            
            blank['harmonized'] = temp

        if 'Emblem Effect 1' in i.text:
            strings = list(i.stripped_strings)
            strings.pop(0)
            temp = '\n'.join(strings)
            blank['emblem'] = temp

    wep = blank['weapon']
    if wep == 'Lance' or 'Blue' in wep:
        color = 'Blue'
    if wep == 'Sword' or 'Red' in wep:
        color = 'Red'
    if wep == 'Axe' or 'Green' in wep:
        color = 'Green'
    if wep == 'Staff' or 'Colorless' in wep:
        color = 'Colorless'
    blank['color'] = color

    wepsplit = wep.split(' ')

    if len(wepsplit) == 2:
        blank['weapon'] = wepsplit[1].capitalize()

    # Next are the stats. Go through and find the BST, individual stats, and then look for superboon/banes
    tables = document.find_all(class_="wikitable default")

    # table 0: lvl 1 stats
    keys = ['hp', 'atk', 'spd', 'def', 'res']
    lvl1_table = tables[0].find_all('tr')
    lvl1_raw = lvl1_table[5].find_all('td')
    lvl1 = []
    for i in range(1, 6):
        stat = str(lvl1_raw[i])[4:-5].split("/")
        lvl1.append(int(stat[1]))
        blank['base'][keys[int(i)-1]] = lvl1[i-1]

    # table 1: lvl 40 stats
    lvl40_table = tables[1].find_all('tr')
    lvl40_raw = lvl40_table[5].find_all('td')
    lvl40 = []
    
    blank['superbane'] = []
    blank['superboon'] = []
    for i in range(1, 6):
        stat = str(lvl40_raw[i])[4:-5].split("/")
        bane_diff = int(stat[1]) - int(stat[0])
        boon_diff = int(stat[2]) - int(stat[1])
        lvl40.append(int(stat[1]))
        if boon_diff == 4:
            blank['superboon'].append(keys[i-1])
        if bane_diff == 4:
            blank['superbane'].append(keys[i-1])


    # table 2: growths
    growths_table = tables[2].find_all('tr')[1].find_all('td')

    growths = []
    for i in range(1, 6):
        gr = str(growths_table[i])[4:-6]
        growths.append(int(gr))
        blank['growth'][keys[i-1]] = growths[i-1]

    
    """

    for i in range(0, len(keys)):
        
        diff = lvl40[i] - lvl1[i]
        if diff == 13 or diff == 22 or diff == 33:
            blank['superbane'].append(keys[i])
        if diff == 10 or diff == 19 or diff == 30:
            blank['superboon'].append(keys[i])
    """
        
        

    skill_tables = document.find_all(class_="wikitable default unsortable skills-table")
    blank['weapons'] = {}
    wep_table = skill_tables[0].find_all('tr')
    for i in range(1, len(wep_table)):
        cols = wep_table[i].find_all('td')
        wep = list(cols[0].stripped_strings)[0]
        unlock = list(cols[6].stripped_strings)[0]
        blank['weapons'][wep] = unlock

    key = 'assist'
    table2 = skill_tables[1].find_all('tr')
    headers = list(table2[0].stripped_strings)

    if 'Cooldown' in headers:
        key = 'special'

    blank['special'] = {}
    blank['assist'] = {}
    for i in range(1, len(table2)):
        cols = table2[i].find_all('td')
        skill = list(cols[0].stripped_strings)[0]
        unlock = list(cols[5].stripped_strings)[0]
        blank[key][skill] = unlock

    if len(skill_tables) > 2:
        key = 'special'
        table2 = skill_tables[2].find_all('tr')
        for i in range(1, len(table2)):
            cols = table2[i].find_all('td')
            skill = list(cols[0].stripped_strings)[0]
            unlock = list(cols[5].stripped_strings)[0]
            blank[key][skill] = unlock

    passive_table = document.find_all(class_="wikitable default skills-table")

    ptable = passive_table[0].find_all('tr')
    headers = list(ptable[0].stripped_strings)
    slot = 'A'
    from collections import defaultdict
    skills = defaultdict(dict)
    skills['A'] = {}
    skills['B'] = {}
    skills['C'] = {}
    skills['X'] = {}
    for i in range(1, len(ptable)):
        cols = list(ptable[i].stripped_strings)

        if cols[0] == 'A' or cols[0] == 'B' or cols[0] == 'C' or cols[0] == 'X':
            slot = cols[0]
            name = cols[1]
            unlock = cols[len(cols) - 1]

        else:
            name = cols[0]
            unlock = cols[len(cols) - 1]
        skills[slot][name] = unlock
    blank['passive'] = skills

    fandomquote = requests.get(f'https://feheroes.fandom.com{page_name}/Quotes')
    soupquote = BeautifulSoup(fandomquote.text, 'html.parser')
    # The information we want on the page is stored under '<div role="document" class="page">
    documentquote = soupquote.find(class_="mw-parser-output")

    quotes = documentquote.find_all('blockquote')

    blank['quotes']['Summon'] = []
    blank['quotes']['Level'] = []
    blank['quotes']['Castle Hall'] = []
    blank['quotes']['Visit'] = []
    blank['quotes']['Learn Skill'] = []
    blank['quotes']['Confession'] = []
    blank['quotes']['Special'] = []
    blank['quotes']['Status'] = []
    blank['quotes']['Map Select'] = []

    # print(quotes)

    # Check for 'Movie' quotes. If found, remove them. Only 8 units even have them
    if len(quotes) > 25:
        del (quotes[3])
        del (quotes[2])

    odd = []
    for i in range(0, len(quotes)):
        if i % 2:
            continue
        else:
            odd.append(quotes[i])


    for i in range(0, len(odd)):
        q = list(odd[i].stripped_strings)
        if len(q) > 1:
            q = '\n'.join(q)
            odd[i] = bold_names(q.replace("\n\u3010Friend\u3011\n", " [F]").replace("\n\u3010Summoner\u3011\n", " [S]"))

            
        else:
            odd[i] = bold_names(q[0].replace("\n\u3010Friend\u3011\n", " [F]").replace("\n\u3010Summoner\u3011\n", " [S]"))

    blank['quotes']['Summon'].append(odd[0])


    blank['quotes']['Castle Hall'].append(odd[1])
    blank['quotes']['Castle Hall'].append(odd[2])
    blank['quotes']['Castle Hall'].append(odd[3])
    blank['quotes']['Castle Hall'].append(odd[4])
    blank['quotes']['Castle Hall'].append(odd[5])

    blank['quotes']['Visit'].append(odd[6])

    blank['quotes']['Level'].append(odd[7])
    blank['quotes']['Level'].append(odd[8])
    blank['quotes']['Level'].append(odd[9])

    blank['quotes']['Learn Skill'].append(odd[10])

    blank['quotes']['Confession'].append(odd[11])

    q_table = documentquote.find_all(class_="wikitable")

    # print(len(q_table))
    spc = q_table[4].find_all('td')
    spc_clean = []
    for i in range(0, len(spc)):
        spc_clean.append(bold_names(spc[i].text).strip())

    blank['quotes']['Special'].append(spc_clean[1])
    blank['quotes']['Special'].append(spc_clean[3])
    blank['quotes']['Special'].append(spc_clean[5])
    blank['quotes']['Special'].append(spc_clean[7])

    spc = q_table[8].find_all('td')
    # print(spc)
    spc_clean = []
    for i in range(0, len(spc)):
        if i == ((len(spc_clean)) * 3 + 1):
            spc_clean.append(bold_names(spc[i].text).strip())

    for i in spc_clean:
        blank['quotes']['Status'].append(i)

    spc = q_table[10].find_all('td')

    spc_clean = []
    for i in range(0, len(spc)):
        if i % 2 == 1:
            blank['quotes']['Map Select'].append(bold_names(spc[i].text).strip())

    # Look for table 12. If it exists, check if the text includes "SUPPORT".
    if len(q_table) > 12:
        if "SUPPORT" in q_table[12].text:
            # This unit is a Duo of some kind. Fill out the Conversation, Duo Skill & Back unit Supporting fields
            blank['quotes']['Conversation'] = []
            blank['quotes']['Duo Skill'] = []
            blank['quotes']['Back Unit Supporting'] = []

            # Starting with Back Unit Supporting quotes
            spc = q_table[12].find_all('td')
            for i in range(0, len(spc)):
                if i % 2 != 0:
                    blank['quotes']['Back Unit Supporting'].append(bold_names(spc[i].text).strip())

            # Next, Duo Skill quotes
            spc = q_table[14].find_all('td')
            for i in range(0, len(spc)):
                if i % 2 != 0:
                    blank['quotes']['Duo Skill'].append(bold_names(spc[i].text).strip())

            # Last, Duo Conversations
            spc = q_table[16].find_all('td')
            for i in range(0, len(spc)):
                if i % 2 != 0:
                    blank['quotes']['Conversation'].append(bold_names(spc[i].text).strip())

    # using those freaking maps
    if ('+' in blank['origin']):
        origin = blank['origin'].split(' + ')[0]
    else:
        origin = blank['origin']
    blank['chibi'] = maps.entrymap[origin]['chibi']
    blank['RANDOM_POOL'].append(maps.entrymap[origin]['pool'])

    blank['short_name'] = maindis + ogname

    blank['SEARCH_NAME'] = maindis + ogname

    wepid = maps.wepmap[blank['color'] + ' ' + blank['weapon']]

    blank['DISPLAY_NAME'] = '<:' + blank['color'] + '_' + blank['weapon'] + ':' + wepid + '>' + blank['short_name']

    blank['ALT_NAME'].append(blank['title'])
    blank['ALT_NAME'].append(ogname + ': ' + blank['title'])

    for i in alts:
        blank['ALT_NAME'].append(i + ' ' + ogname)

    blank['HARD_ALT_NAME'] = blank['ALT_NAME']
    blank['HARD_ALT_NAME'].append(mainkey)

    wepkeys = list(blank['weapons'].keys())

    wepcond = wepkeys[len(wepkeys) - 1]
    wepcond = utility.compress(wepcond)
    blank['prf'][''] = wepcond
    blank['prf']['eff'] = wepcond
    blank['prf']['atk'] = wepcond
    blank['prf']['spd'] = wepcond
    blank['prf']['def'] = wepcond
    blank['prf']['res'] = wepcond

    
    obj[mainkey] = blank
    portrait.portrait(mainkey, blank)

    with open('./update.json',  'w', encoding='utf8',) as fp:
        json.dump(obj, fp, indent=2)
    # print(blank)
    return blank


# Helper function that checks if the string has a name, and adds asterisks to make it bold
def bold_names(input_string):
    if ":" in input_string:
        input_string = input_string.replace("\n:", ":").replace(":", ":**")
        input_string = input_string.splitlines()
        output_string = ""

        for i in input_string:
            if ":**" in i:
                j = "**" + i
                if i != input_string[0]:
                    output_string = output_string + "\n" + j
                else:
                    output_string = j
            else:
                output_string = output_string + "\n" + i
    else:
        output_string = input_string
    return output_string


#print(scrape_page('/wiki/Lucina:_Future_Witness'))
# print(scrape_page('/wiki/Camilla:_Bewitching_Beauty'))
# print(scrape_page('/wiki/Corrin:_Nightfall_Ninja_Act'))
