from app.rag import retrieve, split_into_chunks
from app.schemas import Document


def test_chunks_overlap_and_cover_text():
    doc = Document(name="a", text="x" * 1000)
    chunks = split_into_chunks(doc, size=400, overlap=80)
    assert all(len(c.text) <= 400 for c in chunks)
    assert len(chunks) == 3  # starts at 0, 320, 640


def test_retrieve_finds_relevant_english_chunk():
    docs = [
        Document(name="resume", text="I built a React and TypeScript web app for my lab."),
        Document(name="hobby", text="I enjoy cooking curry and hiking on weekends."),
    ]
    top = retrieve("Frontend engineer, React TypeScript", docs, top_k=1, size=400, overlap=80)
    assert top[0].source == "resume"


def test_retrieve_works_with_japanese():
    docs = [
        Document(name="es", text="研究室でPythonを使った機械学習モデルの開発に取り組みました。"),
        Document(name="other", text="週末はカフェでアルバイトをしています。"),
    ]
    top = retrieve("機械学習エンジニア募集。Pythonの経験歓迎。", docs, top_k=1, size=400, overlap=80)
    assert top[0].source == "es"
