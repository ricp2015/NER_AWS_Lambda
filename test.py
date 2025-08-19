from src.ner import extract_entities
from pprint import pprint

samples = [
    "Tim Cook met Elon Musk in Rome on Monday.",
    "Amazon acquired Whole Foods for $13.7 billion in 2017.",
    "The conference will be held at Stanford University in California."
]

for s in samples:
    print("\nINPUT:", s)
    pprint(extract_entities(s))
