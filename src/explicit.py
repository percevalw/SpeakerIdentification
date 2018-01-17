import re

regex_utterance = r'\`\`(.+?)\'\''
regex_narration_begin = r'(?!.*\'\').+\`\`'
regex_narration_inbetween = r'\'\'(.+?)\`\`'
regex_narration_end = r'\'\'(?!.*\'\').+$'
verbs = ['said', 'spoke', 'talked', 'asked', 'replied', 'answered', 'added', 'continued', 'went on', 'cried', 'sighed', 'thought']

def get_annotated_lines(parser, dep_parser):
    annotated_lines = []

    for line in open('./corpus/curated_text.txt', 'r+'):
        utterances = re.findall(regex_utterance, line)
        if utterances != []:
            speaker_name = None
            speaker_gender = None
            narrations = [] + list(re.findall(regex_narration_begin, line)) + list(re.findall(regex_narration_inbetween, line)) + list(re.findall(regex_narration_end, line))
            
            if narrations != []:
                
                # replace narrations with '[X]'
                line = re.sub(regex_narration_begin, ' [X] \`\`', line)
                line = re.sub(regex_narration_inbetween, ' [X] ', line)
                line = re.sub(regex_narration_end, '\'\' [X] ', line)
                print(narrations)
                dependencies = [list(parse.triples()) for parse in dep_parser.raw_parse(narrations[0])]
                trees = list(parser.raw_parse(narrations[0]))
                print(trees)
                #dependencies = sum([[list(parse.triples()) for parse in dep_graphs] for dep_graphs in dep_parser.tagged_parse_sents([tagged])],[])
                print(dependencies)
                for ((word1,tag1),dep,(word2,tag2)) in dependencies[0]:
                    if tag1.startswith('VB') and dep == 'nsubj':
                        if tag2.startswith('NNP'):
                            speaker_name = word2
                        if word2 in ['he', 'husband', 'man']:
                            speaker_gender = 'M'
                        if word2 in ['she', 'wife', 'lady']:
                            speaker_gender = 'F'
                        print((word1,tag1),dep,(word2,tag2))
                #speaker = " ".join(word for (word, tag) in tagged if tag.startswith('NNP'))
                #entities = nltk.chunk.ne_chunk(tagged)
                #print(entities)
            annotated_line = (speaker_name, speaker_gender, line)
            print(annotated_line)
            print('----------------------')
            annotated_lines.append(annotated_line)
    return annotated_lines