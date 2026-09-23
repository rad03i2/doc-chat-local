from pathlib import Path
import pytest
from doc_chat_local.core import DocumentIndex, chunk_text, tokenize
from doc_chat_local.cli import collect, main


def test_tokenize_arabic_english():
    assert "privacy" in tokenize("Privacy محلي") and "محلي" in tokenize("Privacy محلي")

def test_chunk_validation():
    with pytest.raises(ValueError): chunk_text("x", "a", 99, 0)

def test_search_ranks_relevant_passage(tmp_path: Path):
    a=tmp_path/"a.txt"; b=tmp_path/"b.md"
    a.write_text("Python supports readable automation scripts and local tools.", encoding="utf-8")
    b.write_text("Gardening needs water and sunlight.", encoding="utf-8")
    idx=DocumentIndex.from_paths([a,b], size=100, overlap=10)
    hits=idx.search("Python automation")
    assert hits and hits[0].source.endswith("a.txt") and hits[0].score > 0

def test_answer_has_source(tmp_path: Path):
    p=tmp_path/"ar.txt"; p.write_text("الخصوصية مهمة والبيانات تبقى محليا على الجهاز.", encoding="utf-8")
    answer=DocumentIndex.from_paths([p], size=100, overlap=10).answer("الخصوصية البيانات")
    assert "Source:" in answer and "chunk-0" in answer

def test_roundtrip_index(tmp_path: Path):
    p=tmp_path/"x.txt"; p.write_text("alpha beta gamma", encoding="utf-8")
    idx=DocumentIndex.from_paths([p], size=100, overlap=10); target=tmp_path/"i.json"; idx.save(target)
    assert DocumentIndex.load(target).search("beta")[0].text == "alpha beta gamma"

def test_directory_collection_filters_and_sorts(tmp_path: Path):
    (tmp_path/"b.md").write_text("b"); (tmp_path/"a.txt").write_text("a"); (tmp_path/"x.bin").write_bytes(b"x")
    assert [p.name for p in collect([str(tmp_path)])] == ["a.txt","b.md"]

def test_cli_end_to_end(tmp_path: Path, capsys):
    p=tmp_path/"doc.txt"; p.write_text("Local search keeps documents private.", encoding="utf-8"); index=tmp_path/"idx.json"
    assert main(["build",str(p),"-o",str(index),"--chunk-size","100","--overlap","10"]) == 0
    assert main(["ask",str(index),"documents private"]) == 0
    assert "Source:" in capsys.readouterr().out

def test_no_match():
    assert DocumentIndex([]).answer("anything").startswith("No relevant")
