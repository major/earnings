import pytest

from earnings.retrieve import build_queue, get_page


@pytest.mark.vcr()
def test_get_page():
    """Test get_page function."""
    messages = get_page()
    assert len(messages) == 30
    assert messages[0]["id"] > messages[1]["id"]


@pytest.mark.vcr()
def test_build_queue():
    """Test build_queue function."""
    queue = build_queue(562556223)
    assert len(queue) == 14
    assert queue[0]["id"] > queue[1]["id"]
    assert 562556223 not in [x["id"] for x in queue]
