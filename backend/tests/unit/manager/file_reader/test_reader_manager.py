import pytest
from unittest.mock import patch, MagicMock
from batch4llm.manager.file_reader.reader_manager import FileReaderManager


@pytest.fixture
def dummy_pdf(tmp_path):
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")
    return pdf_path


@patch("batch4llm.manager.file_reader.pypdf2_reader.PdfReader")
def test_manager_reads_via_registered_reader(mock_pdfreader, dummy_pdf):
    """Ensure FileReaderManager dispatches correctly to registered reader."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Text"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdfreader.return_value = mock_reader

    result = FileReaderManager.read("pypdf2_default", str(dummy_pdf))
    assert result == "Text"


def test_manager_raises_for_invalid_reader():
    """Manager should raise ValueError for unsupported readers."""
    with pytest.raises(ValueError):
        FileReaderManager.read("invalid", "file.pdf")


def test_get_supported_readers():
    """Verify registered reader names are discoverable."""
    readers = FileReaderManager.get_supported()
    assert isinstance(readers, list)
    assert "pypdf2_default" in readers
