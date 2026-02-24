"""Tests for dashboard module."""

from unittest.mock import MagicMock, patch

from src.dashboard.app import get_llm_client, init_session_state


@patch("src.dashboard.app.load_config")
@patch("src.dashboard.app.OpenAIClient")
def test_get_llm_client_openai(
    mock_openai: MagicMock,
    mock_config: MagicMock,
) -> None:
    """Test creating an OpenAI LLM client."""
    mock_cfg = MagicMock()
    mock_cfg.openai_api_key = "test-key"
    mock_config.return_value = mock_cfg

    get_llm_client("OpenAI", "gpt-4")
    mock_openai.assert_called_once_with("test-key", model="gpt-4")


@patch("src.dashboard.app.load_config")
@patch("src.dashboard.app.AnthropicClient")
def test_get_llm_client_anthropic(
    mock_anthropic: MagicMock,
    mock_config: MagicMock,
) -> None:
    """Test creating an Anthropic LLM client."""
    mock_cfg = MagicMock()
    mock_cfg.anthropic_api_key = "test-ant-key"
    mock_config.return_value = mock_cfg

    get_llm_client("Anthropic", "claude-3-opus")
    mock_anthropic.assert_called_once_with("test-ant-key", model="claude-3-opus")


class FakeSessionState:
    """Fake session state that supports both attribute and 'in' checks."""

    def __init__(self) -> None:
        self._data: dict = {}

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __setattr__(self, key: str, value: object) -> None:
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __getattr__(self, key: str) -> object:
        if key == "_data":
            return super().__getattribute__(key)
        return self._data.get(key)


@patch("src.dashboard.app.st")
@patch("src.dashboard.app.CostTracker")
def test_init_session_state(
    mock_tracker_cls: MagicMock,
    mock_st: MagicMock,
) -> None:
    """Test session state initialization."""
    mock_st.session_state = FakeSessionState()
    init_session_state()
    assert mock_st.session_state.analyzed is False
    assert mock_st.session_state.cost_tracker is not None


@patch("src.dashboard.app.st")
def test_init_session_state_preserves_existing(mock_st: MagicMock) -> None:
    """Test that existing session state is not overwritten."""
    state = FakeSessionState()
    state.analyzed = True
    state.cost_tracker = "existing"
    mock_st.session_state = state
    init_session_state()
    assert mock_st.session_state.analyzed is True
    assert mock_st.session_state.cost_tracker == "existing"
