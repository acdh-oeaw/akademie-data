import glob
import os
import shutil
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from bs4 import BeautifulSoup
from slugify import slugify


data_dir = "data"
editions = os.path.join(data_dir, "editions")
indices = os.path.join(data_dir, "indices")

shutil.rmtree(data_dir, ignore_errors=True)
os.makedirs(editions, exist_ok=True)
os.makedirs(indices, exist_ok=True)

files = glob.glob("dump/phil-hist/*.xml")

print("remove duplicated ids to create well formed xmls")
tags_to_remove = ["w", "pc"]

for x in tqdm(files, total=len(files)):
    _, file_name = os.path.split(x)
    with open(x) as fp:
        soup = BeautifulSoup(fp, "xml")
        for tag in tags_to_remove:
            for match in soup.findAll(tag):
                match.unwrap()
    save_path = os.path.join(editions, file_name)
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

print(editions)
files = glob.glob(f"{editions}/*.xml")

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
    soup = BeautifulSoup(fp, "xml")
    for element in soup.find_all("person", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        element["xml:id"] = slugify(old_id)
    for element in soup.find_all("place", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        del element["xml:id"]
        element["key"] = old_id
listperson = os.path.join(indices, "listperson.xml")
with open(listperson, "w", encoding="utf-8") as file:
    file.write(str(soup))

doc = TeiReader(listperson)
doc.tree_to_file(listperson)


print("fix entity refs in  in listplace")

with open("dump/register/listplace.xml") as fp:
    soup = BeautifulSoup(fp, "xml")
    for element in soup.find_all("place", attrs={"xml:id": True}):
        old_id = element["xml:id"]
        element["xml:id"] = slugify(old_id)
listplace = os.path.join(indices, "listplace.xml")
with open(listplace, "w", encoding="utf-8") as file:
    file.write(str(soup))
    
doc = TeiReader(listplace)
doc.tree_to_file(listplace)
