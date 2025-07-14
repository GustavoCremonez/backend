import spacy
import re

nlp = spacy.load("pt_core_news_md")

PRAZO_REGEX = re.compile(r"até [\w\s]+|amanhã|hoje|na próxima semana|semana que vem|mês que vem", re.IGNORECASE)

def extract_tasks(texto: str):
    doc = nlp(texto)
    tarefas = []

    for sent in doc.sents:
        sent_text = sent.text
        sent_doc = nlp(sent_text)
        pessoas = [ent.text for ent in sent_doc.ents if ent.label_ == "PER"]
        verbos = [token.text for token in sent_doc if token.pos_ == "VERB"]
        prazo = PRAZO_REGEX.search(sent_text)

        for pessoa in pessoas:
            if verbos:
                tarefas.append({
                    "responsavel": pessoa,
                    "tarefa": f"{verbos[0]} {extract_complement(sent_doc, verbos[0])}",
                    "prazo": prazo.group(0) if prazo else None
                })

    return tarefas

def extract_complement(doc, verbo):
    for token in doc:
        if token.text == verbo:
            complement = " ".join([child.text for child in token.children if child.dep_ in ["obj", "xcomp", "advmod"]])
            return complement
    return ""