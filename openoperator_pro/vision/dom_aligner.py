from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

embedder = SentenceTransformer("intfloat/e5-large-v2")


def match_bbox_to_dom(text: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    nodes = [n.get_text(" ", strip=True) for n in soup.find_all()]
    node_emb = embedder.encode(nodes, convert_to_tensor=True)
    query_emb = embedder.encode(text, convert_to_tensor=True)
    scores = util.cos_sim(query_emb, node_emb)[0].cpu().numpy()
    idx = scores.argmax()
    return nodes[idx]
