import re 

def curation(characters):
    def curate_characters_names(raw_file, curated_file):
        curated_file.truncate()
        for line in raw_file:
                for character in characters:
                    for alias in character.aliases:
                        line = re.sub(r'\b' + alias + r'\b', character.name, line, flags=re.IGNORECASE)
                curated_file.write(line)

    with open('./corpus/PRIDPREJ_NONEWLINE_Organize_v2.txt', 'r+') as raw_file:
        with open('./corpus/curated_text.txt', 'w+') as curated_file:
            curate_characters_names(raw_file, curated_file)

    with open('./corpus/REAL_ALL_CONTENTS_PP.txt', 'r+') as raw_file:
        with open('./corpus/curated_dialogs.txt', 'w+') as curated_file:
            curate_characters_names(raw_file, curated_file)