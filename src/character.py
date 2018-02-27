class Character:
    
    def __init__(self, name, gender, aliases, parents=[], spouses=[], children=[], siblings=[], cousins=[]):
        self.name = name
        self.gender = gender
        self.aliases = aliases
        self.parents = parents
        self.spouses = spouses
        self.children = children
        self.siblings = siblings
        self.cousins = cousins
    
    def __str__(self):
        string = ""
        if (self.name != None):
            string += 'name: ' + str(self.name)
        if (self.gender != None):
            string += '\ngender: ' + str(self.gender)
        if (self.aliases != None):
            string += '\naliases: ' + str(self.aliases)
        #if (self.parents != None):
        #    string += '\nparents: ' + str(self.parents)
        #if (self.spouses != None):
        #    string += '\nchildren: ' + str(self.children)
        #if (self.siblings != None):
        #    string += '\nsiblings: ' + str(self.siblings)
        #if (self.cousins != None):
        #    string += '\ncousins: ' + str(self.cousins)
        return string


import re


characters = []
men = []
women = []

with open('./corpus/PeopleList_Revised.txt', 'r+') as character_infos:
    for character_info in character_infos:
        character_info = re.sub('\n', '', character_info).split(';')
        aliases = []
        main_name = None
        gender = None
        for info in character_info:
            if (info in ['M', 'F']):
                gender = info
            else:
                if not main_name:
                    main_name = re.sub(r'[\W_]+' , '_', info)
                aliases.append(info)
        if gender == 'M':
            men.append(Character(main_name, gender, aliases))
        else:
            women.append(Character(main_name, gender, aliases))

# if a man and a woman have the same alias, keep only the man's alias 
# (Bennet is more likely a man than a woman)
men_aliases = sum((man.aliases for man in men), [])
for woman in women:
    for woman_alias in woman.aliases:
        if woman_alias in men_aliases:
            woman.aliases.remove(woman_alias)

# women first, because when we will replace the aliases in the text, 
# we do not want the "Bennet" in "Mrs Bennet" to be replaced by "Mr Bennet"           
characters = women + men







# TODO : delete

elizabeth = Character(
    'Elizabeth',
    'F',
    [
        'Elizabeth Bennet',
        'Miss Elizabeth Bennet',
        'Miss Elizabeth',
        'Miss Lizzy',
        'Miss Bennet',
        'Miss Eliza',
        'Eliza Bennet',
        'Elizabeth',
        'Lizzy',
        'Liz',
        'Eliza'
    ]
)

lydia = Character(
    'Lydia', 
    'F',
    ['Lydia Bennet', 'Miss Lydia', 'Miss Lydia', 'Lydia']
)

jane = Character(
    'Jane', 
    'F',
    ['Jane Bennet', 'Jane']
)

kitty = Character(
    'Kitty', 
    'F',
    ['Kitty Bennet','Catherine Bennet','Kitty']
)

mary = Character(
    'Mary',
    'F',
    ['Mary Bennet','Mary']
)

darcy = Character(
    'Darcy', 
    'M',
    ['Mr. Darcy','Mr. Fitzwilliam Darcy','Fitzwilliam Darcy','Darcy']
)

georgiana = Character(
    'Georgiana', 
    'F',
    ['Georgiana Darcy','Georgiana','Miss Darcy']
)

mr_bennet = Character(
    'Bennet',
    'M',
    ['Mr. Bennet', 'Bennet']
)

mrs_bennet = Character(
    'MrsBennet',
    'F',
    ['Mrs. Bennet']
)

charlotte = Character(
    'Charlotte',
    'F',
    ['Charlotte','Charlotte Lucas','Mrs. Collins','Miss Lucas']
)

mr_collins = Character(
    'MrCollins',
    'M',
    ['Mr. Collins','William Collins'],
)

miss_bingley = Character(
    'MissBingley',
    'F',
    ['Caroline Bingley','Caroline','Miss Bingley']
)

mr_bingley = Character(
    'Bingley',
    'M',
    ['Mr. Bingley','Bingley']
)


elizabeth.parents = [mr_bennet, mrs_bennet]
elizabeth.siblings = [kitty, jane, mary, lydia]
kitty.parents = [mr_bennet, mrs_bennet]
kitty.siblings = [elizabeth, jane, mary, lydia]
mary.parents = [mr_bennet, mrs_bennet]
mary.siblings = [kitty, jane, elizabeth, lydia]
jane.parents = [mr_bennet, mrs_bennet],
jane.siblings = [kitty, elizabeth, mary, lydia]
lydia.parents = [mr_bennet, mrs_bennet],
lydia.siblings = [kitty, jane, mary, elizabeth]

mr_bennet.spouses = [mrs_bennet]
mr_bennet.children = [kitty, elizabeth, mary, lydia, jane]
mr_bennet.siblings = [mr_collins]

mrs_bennet.spouses = [mr_bennet]
mrs_bennet.children = [kitty, elizabeth, mary, lydia, jane]

charlotte.spouses = [mr_collins] 
mr_collins.spouses = [charlotte]
mr_collins.siblings = [mr_bennet]

mr_bingley.siblings = [miss_bingley]
miss_bingley.siblings = [mr_bingley]