import pysubs2
from nican import nican
from tqdm import tqdm

def main(sub_file):
    subs = pysubs2.load(sub_file, encoding="utf-8")
    filename = sub_file.split('.')[:-1]
    filename = "".join(filename)
    extension = sub_file.split('.')[-1]
    for line in tqdm(subs):
        line.text = nican(line.text)
        subs.save(f"{filename}_edited.{extension}")


if __name__ == '__main__':
    main(input())