from app.ingest import list_pdfs


def test_list_pdfs_missing_dir(tmp_path):
    assert list_pdfs(tmp_path / "missing") == []
