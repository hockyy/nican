import pysubs2
from nican import nican
from tqdm import tqdm
import re
import glob
from pathlib import Path


def main(sub_file):
    subs = pysubs2.load(sub_file, encoding="utf-8")
    filename = sub_file.split('.')[:-1]
    filename = ".".join(filename)
    extension = sub_file.split('.')[-1]
    extension = 'srt'
    for line in tqdm(subs):
        line.text = re.sub(r'\\N', '', line.text)
        line.text = nican(line.text)
        subs.save(f"{filename}_edited.{extension}")


if __name__ == '__main__':
    regexFiles = input("Insert location of subtitle: ")
    globFiles = sorted(glob.glob(regexFiles))
    for file in globFiles:
        print(file)
        if(not file.endswith('_edited.srt')):
            path = Path(file)
            if(path.is_file()):
                print(file)
                try:
                    main(file)
                except Exception as e:
                    print(e)
                    pass