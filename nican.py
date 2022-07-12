import subprocess
import sys
import MeCab
import re
import random

# https://github.com/loretoparisi/kakasi (KAKASI for Romaji)
# https://qiita.com/ekzemplaro/items/c98c7f6698f130b55d53 (Mecab with ipadic-neologd dictionary for separation)
# https://github.com/melissaboiko/myougiden (Myougiden for translation)

mt = MeCab.Tagger("mecabrc")

def runAndGetOutput(cmd: str):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = res.stdout.decode("utf-8").strip()
    return result

def toRomaji(s: str):
    # Add -Ka to change katakana too
    cmd = f'echo "{s}" | iconv -f utf8 -t eucjp | kakasi -i euc -Ha -Ja -Ka -Ea -ka  | iconv -f eucjp -t utf8'
    return runAndGetOutput(cmd)

def toHiragana(s: str):
    cmd = f'echo "{s}" | iconv -f utf8 -t eucjp | kakasi -JH -KH -Ea | iconv -f eucjp -t utf8'
    return runAndGetOutput(cmd)

def separate(s: str):
    parsed = mt.parse(s).strip().split('\n')
    res = []
    typeOfWord = []
    for token in parsed:
        current = token.split('\t')
        if(len(current) == 1): break
        # print(current)
        res.append(current[0])
        typeOfWord.append(current[1].split(',')[0])
    return res, typeOfWord

def translate(s: str):
    cmd = f'~/.local/bin/myougiden -W -k --color no {s}'
    res = runAndGetOutput(cmd).strip()
    if(not res): return
    res = res.split('\t')[2].split(' ', 1)[1]
    if('|' in res):
        res = res.split('|')[0]
    # Replace explanations
    res = re.sub(pattern=r'\(.+\)',repl='', string=res).strip()
    res = re.sub(pattern=r'\[.+\]',repl='', string=res).strip()
    res = re.sub(pattern=r'\{.+\}',repl='', string=res).strip()
    res = re.sub(pattern=r'〔.+〕',repl='', string=res).strip()
    return res


def getTranslation(res, typeOfWord, romaji, minTranslate = 100):
    indexes = [i for i in range(len(res))]
    random.shuffle(indexes)
    blacklisted = ["記号", "助詞", "助動詞"]
    meaning = ["" for _ in range (len(res))]

    for idx in indexes:
        if(minTranslate == 0): break
        if(typeOfWord[idx] in blacklisted): continue
        tmpMeaning = translate(res[idx])
        if(not tmpMeaning):
            continue
        if(tmpMeaning.lower() == romaji[idx]):
            continue
        meaning[idx] = tmpMeaning
        minTranslate -= 1
    return meaning

def addTranslation(romaji, meaning, kanji):
    res = ""
    for i in range(len(romaji)):
        if(res != ""): res += " "
        res += romaji[i]
        if(meaning[i] != ""): res += f" ({kanji[i]}={meaning[i]})"
    return res

def nican(query: str):
    # query = "特急はくたかで富山に向かいます。それから、金沢に行って、兼六園に行きます。"
    # Replace weird whitespace with single space
    query = re.sub(r'\s', ' ', query)
    res, typeOfWord = separate(query)
    romaji = toRomaji(" ".join(res)).split()
    meaning = getTranslation(res, typeOfWord, romaji)

    # print(res)
    # print(typeOfWord)
    # print(romaji)
    # print(meaning)

    embedded = addTranslation(romaji, meaning, res)

    # Remove whitespace before symbols:
    embedded = re.sub(pattern=r' ([^a-zA-Z\d\(\[\{])', repl='\\1',string=embedded)
    # Remove whitespace after opening brackets:
    embedded = re.sub(pattern=r'([\(\[\{<]) ', repl='\\1',string=embedded)

    return embedded
    # print(embedded)

#

if __name__ == '__main__':
    nican(input())