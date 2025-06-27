from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

embedder = SentenceTransformer("intfloat/e5-large-v2")


def match_bbox_to_dom(text: str, html: str) -> str:
    """Mapowanie tekstu OCR do elementu DOM"""
    soup = BeautifulSoup(html, "html.parser")
    nodes = [el.get_text(" ", strip=True) for el in soup.find_all()]
    dom_emb = embedder.encode(nodes, convert_to_tensor=True)
    text_emb = embedder.encode(text, convert_to_tensor=True)
    sims = util.cos_sim(text_emb, dom_emb)[0].cpu().tolist()
    idx = sims.index(max(sims))
    return str(soup.find_all()[idx])
