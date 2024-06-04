import glob
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from bs4 import BeautifulSoup
from slugify import slugify


files = glob.glob("play/phil-hist/*.xml")

print("remove duplicated ids to create well formed xmls")
tags_to_remove = ["w", "pc"]

# for x in tqdm(files, total=len(files)):
#     with open(x) as fp:
#         soup = BeautifulSoup(fp, 'html.parser')
#         for tag in tags_to_remove:
#             for match in soup.findAll(tag):
#                 match.unwrap()
#     with open(x, "w", encoding='utf-8') as file:
#         file.write(str(soup))

files = glob.glob("play/phil-hist/*.xml")

refs = set()
new_refs = set()
for x in files:
    try:
        doc = TeiReader(x)
    except Exception as e:
        print(x, e)
    for ref in doc.any_xpath(".//tei:rs[@ref]"):
        ref_value = ref.attrib["ref"].split(":")[-1]
        new_ref = slugify(ref_value)
        refs.add(ref_value)
        new_refs.add(new_ref)
        ref.attrib["ref"] = new_ref
print(len(refs), len(new_refs))
