import glob
from acdh_tei_pyutils.tei import TeiReader

files = glob.glob("./data/indices/*.xml")
for x in files:
    doc = TeiReader(x)
    for bad in doc.any_xpath(".//tei:listEvent"):
        bad.getparent().remove(bad)
    doc.tree_to_file(x)
