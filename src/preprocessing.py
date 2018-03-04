import re
import pickle
import tqdm

def make_name_code(name):
    return "{}".format("_".join(name.replace('.', '').split(" ")))

def replace_names_with_codes(sentence, people):
    codes = {}
    replacements = []
    for code_i, p in enumerate(people):
        code = "@{}@".format(str(code_i))
        codes[code] = p["main"]
        for a in p['aliases']:
            replacements.append((a, code))
    for a, code in sorted(replacements, key=lambda x: len(x[0]), reverse=True):
        sentence = re.sub(a, code, sentence)
    for code, main in codes.items():
        sentence = re.sub(code, main, sentence)
    return sentence

def strip_equal(a, b, l):
    return re.sub(r'(\[X\])|\s', '', a)[:l] == re.sub(r'(\[X\])|\s', '', b)[:l]

def build_dataset(text_file, people):
    with open(text_file, 'r+') as raw_text_file:
        # go through all lines in the book
        text = raw_text_file.read()

    utterances = []
    is_utterance = False
    processed = ""
    source = ""
    sample_parts = []
    text = re.sub('[_]', '', text)
    text = replace_names_with_codes(text, people)
    text = re.sub(' +', ' ', " "+text)
    parts = list(p for p in re.split("(``)|('')", text) if p is not None)
    i = 0
    discussion_index = 0
    index = 0
    while i < len(parts):
        part = parts[i]
        if part == '``' or part == "''":
            is_utterance = part == '``'
            source += part
            i += 1
            continue
        if not is_utterance:
            if next(re.finditer('\n\n', part), None) is not None: # before or after an utterance
                lines = [s for s in re.split("\n\n\.?", part)]
                end_index = index + len(source) + len(part)
                if processed != "":
                    if len(lines)>0 and re.sub('\s+|--', '', lines[0]) != "":
                        sample_parts.append({"text": lines[0], "utterance": False})
                        source += lines[0]
                    if processed[-5:] == " [X] ":
                        processed = processed[:-5]
                    if processed != "":
                        utterances.append({
                            "only_utterance_us": processed,
                            "source": source,
                            "parts": sample_parts,
                            "discussion_index": discussion_index,
                            "begin": index,
                            "end": index + len(source)
                        })
                    if len(re.findall('\n\n', part)) > 3:
                        discussion_index += 1
                    index = end_index
                processed = ""
                if len(lines) > 1 and re.sub('\s+|--', '', lines[-1]) != "":
                    sample_parts = [({"text": lines[-1], "utterance": False})]
                else:
                    sample_parts = []
                source = lines[-1] if len(lines) > 1 else ''
            else: # in the middle of an utterance
                if re.sub('\s+|--', '', part) != "":
                    sample_parts.append({"text": part, "utterance": False})
                source += part
                if part != " -- ":
                    if processed[-5:] != " [X] ":
                        processed += " [X] "
                else:
                    processed += " "
        else:
            sample_parts.append({"text": part, "utterance": True})
            monoline = " ".join(part.split("\n\n"))
            processed += monoline
            source += part
        i += 1

    return utterances
    
def match_with_annoted_file(path, utterances, people):    
    processed_to_index = {annotation["only_utterance_us"]: i for i, annotation in reversed(list(enumerate(utterances)))}    
        
    # annotation matching part
    with open(path) as annoted_text_file:
        annotated_text_lines = annoted_text_file.readlines()

    annoted_utterances = []
        
    for annoted_line in annotated_text_lines:
        annotation_i, label, utterance_text = annoted_line.split('\t')
        utterance_text = re.sub('_', '', utterance_text)
        utterance_text = re.sub('\s+', ' ', utterance_text)
        utterance_text = utterance_text.strip()
        utterance_text = replace_names_with_codes(utterance_text, people)
        
        for speaker in label.split(' and '):
            speaker = replace_names_with_codes(speaker, people)
            if utterance_text in processed_to_index and "target" not in utterances[processed_to_index[utterance_text]]:
                utterance = utterances[processed_to_index[utterance_text]]
            else:
                utterance = next((a for a in utterances if strip_equal(a['only_utterance_us'], utterance_text, 100) and "target" not in a), None)
                if utterance is None:
                    print("No match :")
                    print(utterance_text)
                    print("--")
                if utterance['only_utterance_us'] != utterance_text:
                    print("Almost match :")
                    print(utterance['only_utterance_us'])
                    print(utterance_text)
                    print("--")
            assert "target" not in utterance
            annoted_utterance = utterance.copy()
            annoted_utterance["only_utterance_article"] = utterance_text
            annoted_utterance["target"] = speaker
            annoted_utterances.append(annoted_utterance)

    return annoted_utterances