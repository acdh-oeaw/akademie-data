import glob
import os
import shutil
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from bs4 import BeautifulSoup
from slugify import slugify

# ToDo: save processed files directly into data/editions | data/indices

temp_dir = "temp"
temp_editions = os.path.join(temp_dir, "editions")
shutil.rmtree(temp_dir, ignore_errors=True)
os.makedirs(temp_editions, exist_ok=True)

files = glob.glob("dump/phil-hist/*.xml")

print("remove duplicated ids to create well formed xmls")
tags_to_remove = ["w", "pc"]

for x in tqdm(files, total=len(files)):
    _, file_name = os.path.split(x)
    with open(x) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        for tag in tags_to_remove:
            for match in soup.findAll(tag):
                match.unwrap()
    save_path = os.path.join(temp_editions, file_name)
    with open(save_path, "w", encoding='utf-8') as file:
        file.write(str(soup))

print(temp_editions)
files = glob.glob(f"{temp_editions}/*.xml")

refs = set()
new_refs = set()
for x in tqdm(files):
    try:
        doc = TeiReader(x)
    except Exception as e:
        print(x, e)
        continue
    for ref in doc.any_xpath(".//tei:rs[@ref]"):
        ref_value = ref.attrib["ref"].split(":")[-1]
        new_ref = f"#{slugify(ref_value)}"
        refs.add(ref_value)
        new_refs.add(new_ref)
        ref.attrib["ref"] = new_ref
    for lb in doc.any_xpath(".//tei:lb"):
        lb.attrib.clear()
    doc.tree_to_file(x)


print("fix entity refs in  in listperson")
with open("dump/register/listperson.xml") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
    for element in soup.find_all("person", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        element["xml:id"] = slugify(old_id)
    for element in soup.find_all("place", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        del element["xml:id"]
        element["key"] = old_id

with open("hansi.xml", "w", encoding='utf-8') as file:
    file.write(str(soup))

doc = TeiReader("hansi.xml")
doc.tree_to_file("hansi.xml")


print("fix entity refs in  in listplace")

with open("dump/register/listplace.xml") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
    for element in soup.find_all("place", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        element["xml:id"] = slugify(old_id)
with open("sumsi.xml", "w", encoding='utf-8') as file:
    file.write(str(soup))
doc = TeiReader("sumsi.xml")
doc.tree_to_file("sumsi.xml")
