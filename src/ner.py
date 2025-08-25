from typing import List, Dict
import spacy

NLP = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> List[Dict]:
    """
    Run NER and return a list of entities with text/label/char spans.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    doc = NLP(text)
    return [
        {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
        for ent in doc.ents
    ]
