import spacy
from typing import List, Dict, Any
import re
from services.validator import postprocess_tasks, normalize_date
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    raise RuntimeError("O modelo 'pt_core_news_lg' do spaCy não está instalado. Rode: python -m spacy download pt_core_news_lg")

# Padrões e listas globais
NOMES_EQUIPE = [
    "Eduardo", "João", "Alessandra", "Alê", "Vinícius", "Vini", "Isabela", "Isa", "Caio", "Marcela", "Leonardo", "Leozão", "Ana", "Renata"
]
APELIDOS = {"Alê": "Alessandra", "Vini": "Vinícius", "Isa": "Isabela", "Leozão": "Leonardo"}
PRONOMES = ["ele", "ela", "dele", "dela"]
NEGATIVOS = [
    "não consegui", "não terminei", "não deu tempo", "não consegui finalizar", "não consegui entregar", "não consegui implementar", "não consegui corrigir"
]
PAIRING = ["pairing com", "parear com", "fazer pairing com", "em dupla com"]
REUNIAO = ["reunião com", "call com", "encontro com"]
BLOQUEIO = ["bloqueado por", "impedido por", "dependendo de", "aguardando"]
VERBOS_PASSADO = [
    "corrigir", "fazer", "concluir", "finalizar", "terminar", "realizar", "entregar", "implementar", "testar", "revisar", "desenvolver", "validar", "aprovar", "ajustar", "refatorar", "subir", "atualizar", "alinhar", "criar", "preparar", "marcar", "rever"
]
VERBOS_FUTURO = VERBOS_PASSADO + [
    "precisar", "dever", "planejar", "pretender"
]

# EntityRuler para prazos e tarefas
ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
ruler.add_patterns([
    {"label": "PRAZO", "pattern": "amanhã"},
    {"label": "PRAZO", "pattern": "hoje"},
    {"label": "PRAZO", "pattern": "depois de amanhã"},
    {"label": "PRAZO", "pattern": "próxima semana"},
    {"label": "PRAZO", "pattern": {"REGEX": r"\\b(segunda|terça|quarta|quinta|sexta|sábado|domingo)(-feira)?\\b"}},
    {"label": "PRAZO", "pattern": {"REGEX": r"\\b(\d{1,2}/\d{1,2}|\d{1,2}-\d{1,2}|\d{1,2} de [a-zç]+)\\b"}},
    {"label": "PRAZO", "pattern": {"REGEX": r"\\b(at[eé] [a-zç]+|em [0-9]+ dias?|no pr[oó]ximo m[eê]s)\\b"}},
] + [
    {"label": "TAREFA", "pattern": [{"LEMMA": verbo}]} for verbo in VERBOS_PASSADO
])

def normalize_nome(nome: str) -> str:
    """Normaliza nomes e apelidos para nomes completos e capitalizados."""
    nome = nome.strip()
    return APELIDOS.get(nome, " ".join([n.capitalize() for n in nome.split()]))

def split_subfrases(frase: str) -> List[str]:
    """Divide frases por conjunções, pontuação e marcadores temporais."""
    return [s.strip() for s in re.split(r"\b(e|mas|ou|;|,|\.|hoje|ontem|amanhã)\b", frase) if s and s.strip() not in ["e", "mas", "ou", ";", ",", ".", "hoje", "ontem", "amanhã"]]

def is_passado(doc) -> bool:
    """Detecta se a subfrase (spaCy doc) está no passado com base em lemas e morfologia."""
    for token in doc:
        if token.lemma_ in VERBOS_PASSADO and "Past" in token.morph.get("Tense"):
            return True
        if re.search(r"\b({})\b".format("|".join([v+"u" for v in VERBOS_PASSADO])), token.text, re.IGNORECASE):
            return True
    if any(neg in doc.text.lower() for neg in NEGATIVOS):
        return False
    return False

def is_futuro(doc) -> bool:
    """Detecta se a subfrase (spaCy doc) está no futuro ou intenção."""
    for token in doc:
        if token.lemma_ in VERBOS_FUTURO and ("Fut" in token.morph.get("Tense") or token.text.lower() in ["vai", "irá", "deverá", "precisará"]):
            return True
        if re.search(r"\b(vai|irá|deverá|precisa|precisará|deve|fará|fazer|começar|começará|iniciar|iniciará|planeja|planejar|pretende|pretender|a fazer|pendente|ficou de|vai entregar|deveriam|deverá|deveriam)\b", token.text, re.IGNORECASE):
            return True
    if any(neg in doc.text.lower() for neg in NEGATIVOS):
        return True
    return False

def extrair_prazo(doc) -> str:
    """Extrai prazos de uma subfrase (spaCy doc) usando entidades e regex."""
    for ent in doc.ents:
        if ent.label_ == "PRAZO":
            return ent.text
    m = re.search(r"(amanhã|hoje|depois de amanhã|próxima semana|[0-9]{1,2}/[0-9]{1,2}|[0-9]{1,2}-[0-9]{1,2}|[0-9]{1,2} de [a-zç]+|segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo|até [a-zç]+|em [0-9]+ dias?|no próximo mês)", doc.text, re.IGNORECASE)
    if m:
        return m.group(0)
    return ""

def normalizar_data_prazo(prazo: str) -> str:
    """Normaliza prazos relativos para data absoluta."""
    return normalize_date(prazo) if prazo else ""

def identificar_padrao(subfrase: str, padroes: List[str]) -> bool:
    """Verifica se algum padrão está presente na subfrase."""
    return any(p in subfrase.lower() for p in padroes)

def coreferencia_simples(subfrase: str, ultimo_nome: str) -> str:
    """Se subfrase começa com pronome, retorna último nome citado."""
    for pron in PRONOMES:
        if subfrase.lower().startswith(pron):
            return ultimo_nome
    return ""

def separar_falas(texto: str) -> List[Dict[str, str]]:
    """Separa o texto em blocos de fala por participante."""
    blocos = re.split(r'(?m)^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+):', texto)
    falas = []
    i = 1
    while i < len(blocos):
        nome = blocos[i].strip()
        fala = blocos[i+1].strip() if i+1 < len(blocos) else ""
        falas.append({"responsavel": normalize_nome(nome), "fala": fala})
        i += 2
    return falas

def agrupar_por_pessoa(lista_falas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agrupa tarefas feitas e a fazer por responsável."""
    agrupado = defaultdict(lambda: {"responsavel": "", "feitas": [], "a_fazer": []})
    for item in lista_falas:
        nome = item["responsavel"]
        agrupado[nome]["responsavel"] = nome
        agrupado[nome]["feitas"].extend(item["feitas"])
        agrupado[nome]["a_fazer"].extend(item["a_fazer"])
    return list(agrupado.values())

def extract_tasks_with_spacy(texto: str) -> List[Dict[str, Any]]:
    """
    Extrai tarefas feitas e a fazer de um texto de daily/reunião, agrupando por responsável.
    Usa heurísticas de NLP, padrões e regras para identificar tarefas, prazos, pairing, reuniões, bloqueios e impedimentos.
    """
    falas = separar_falas(texto)
    resultado = []
    ultimo_nome = ""
    for bloco in falas:
        pessoa = bloco["responsavel"]
        fala = bloco["fala"]
        feitas = []
        a_fazer = []
        frases = [sent.text.strip() for sent in nlp(fala).sents]
        for frase in frases:
            subfrases = split_subfrases(frase)
            for sub in subfrases:
                doc_sub = nlp(sub)
                responsavel = coreferencia_simples(sub, ultimo_nome) or pessoa
                if identificar_padrao(sub, PAIRING):
                    a_fazer.append({"task": sub, "prazo": "", "data_prazo": "", "descricao": "pairing"})
                    continue
                if identificar_padrao(sub, REUNIAO):
                    a_fazer.append({"task": sub, "prazo": "", "data_prazo": "", "descricao": "reunião"})
                    continue
                if identificar_padrao(sub, BLOQUEIO):
                    a_fazer.append({"task": sub, "prazo": "", "data_prazo": "", "descricao": "bloqueio"})
                    continue
                if identificar_padrao(sub, NEGATIVOS):
                    a_fazer.append({"task": sub, "prazo": "", "data_prazo": "", "descricao": "pendente/impedimento"})
                    continue
                if is_passado(doc_sub):
                    feitas.append(sub)
                elif is_futuro(doc_sub):
                    prazo = extrair_prazo(doc_sub)
                    data_prazo = normalizar_data_prazo(prazo)
                    a_fazer.append({"task": sub, "prazo": prazo, "data_prazo": data_prazo, "descricao": ""})
        resultado.append({"responsavel": pessoa, "feitas": feitas, "a_fazer": a_fazer})
        ultimo_nome = pessoa
    agrupado = agrupar_por_pessoa(resultado)
    if not any(p["feitas"] or p["a_fazer"] for p in agrupado):
        logger.warning(f"NENHUMA TAREFA extraída para o texto: {texto}")
    return postprocess_tasks(agrupado) 