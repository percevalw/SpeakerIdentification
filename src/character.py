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

characters = {
                elizabeth,
                lydia,
                jane,
                mary,
                kitty,
                darcy,
                mr_bennet,
                mrs_bennet,
                charlotte,
                mr_collins,
                mr_bingley,
                miss_bingley
            }
