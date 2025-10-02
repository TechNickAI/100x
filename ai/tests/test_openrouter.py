"""Tests for OpenRouter model creation and configuration."""

from unittest.mock import MagicMock

import pytest

from ai.core.config import config
from ai.core.openrouter import (
    SUPPORTED_MODELS,
    CachingSettings,
    OpenRouterSettings,
    create_openrouter_model,
    estimate_token_cost,
    get_builtin_models,
    get_fallback_models,
    get_model_info,
    list_supported_models,
)


class TestOpenRouterModels:
    """Test suite for OpenRouter model management."""

    def test_get_model_info_valid_model(self):
        """Test getting info for supported model."""
        info = get_model_info("anthropic/claude-sonnet-4.5")

        assert info["name"] == "Claude Sonnet 4.5"
        assert "pricing" in info
        assert "fallback_models" in info
        assert info["pricing"]["input_per_million"] == 3.0

    def test_get_model_info_invalid_model(self):
        """Test getting info for unsupported model."""
        with pytest.raises(ValueError, match="Model 'fake/model' not supported"):
            get_model_info("fake/model")

    def test_get_fallback_models(self):
        """Test getting fallback models for a model."""
        fallbacks = get_fallback_models("anthropic/claude-sonnet-4.5")

        assert isinstance(fallbacks, list)
        assert "anthropic/claude-3.5-haiku" in fallbacks
        assert "openai/gpt-5" in fallbacks

    def test_estimate_token_cost(self):
        """Test token cost estimation."""
        cost = estimate_token_cost("anthropic/claude-sonnet-4.5", 1000, 500)

        # Should be (1000/1M * 3.0) + (500/1M * 15.0) = 0.003 + 0.0075 = 0.0105
        assert cost == pytest.approx(0.0105)

    def test_estimate_token_cost_invalid_model(self):
        """Test cost estimation for invalid model."""
        with pytest.raises(ValueError, match="Model 'fake/model' not supported"):
            estimate_token_cost("fake/model", 100, 50)

    def test_list_supported_models(self):
        """Test listing all supported models."""
        models = list_supported_models()

        assert isinstance(models, list)
        assert "anthropic/claude-sonnet-4.5" in models
        assert "anthropic/claude-opus-4.1" in models
        assert "openai/gpt-5" in models
        assert len(models) == len(SUPPORTED_MODELS)

    def test_get_builtin_models(self):
        """Test getting builtin model registry."""
        models = get_builtin_models()

        assert isinstance(models, dict)
        assert models == SUPPORTED_MODELS

    def test_create_openrouter_model_valid(self, mocker):
        """Test creating valid OpenRouter model."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        # Mock the OpenRouter dependencies to avoid network calls
        mock_provider = MagicMock()
        mock_profile = MagicMock()
        mock_profile.supports_json_schema_output = True
        mock_provider.model_profile.return_value = mock_profile

        mocker.patch("ai.core.openrouter.OpenRouterProvider", return_value=mock_provider)
        mocker.patch("ai.core.openrouter.OpenRouterModel")
        mocker.patch("httpx.AsyncClient")

        model = create_openrouter_model(
            "anthropic/claude-sonnet-4.5",
            agent_name="TestAgent",
            settings={"temperature": 0.3},
        )

        # Test that our model creation logic was called
        assert model is not None

    def test_create_openrouter_model_invalid(self):
        """Test creating model with invalid name."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        with pytest.raises(ValueError, match="Model 'fake/model' not supported"):
            create_openrouter_model("fake/model")

    def test_create_openrouter_model_requires_api_key(self, monkeypatch):
        """Test that model creation requires API key."""
        monkeypatch.setattr(config, "openrouter_api_key", "")

        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            create_openrouter_model("anthropic/claude-sonnet-4.5")

    def test_create_openrouter_model_with_fallbacks(self, mocker):
        """Test that fallback models are configured."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        mock_provider = MagicMock()
        mock_profile = MagicMock()
        mock_profile.supports_json_schema_output = True
        mock_provider.model_profile.return_value = mock_profile

        mocker.patch("ai.core.openrouter.OpenRouterProvider", return_value=mock_provider)
        mock_model_class = mocker.patch("ai.core.openrouter.OpenRouterModel")
        mocker.patch("httpx.AsyncClient")

        model = create_openrouter_model("anthropic/claude-sonnet-4.5")

        # Test that fallback models were configured
        call_args = mock_model_class.call_args
        assert "settings" in call_args.kwargs
        extra_body = call_args.kwargs["settings"]["extra_body"]
        assert "models" in extra_body  # Fallback models should be set

    def test_create_openrouter_model_anthropic_caching(self, mocker):
        """Test that Anthropic models get caching enabled."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        mock_provider = MagicMock()
        mock_profile = MagicMock()
        mock_profile.supports_json_schema_output = True
        mock_provider.model_profile.return_value = mock_profile

        mocker.patch("ai.core.openrouter.OpenRouterProvider", return_value=mock_provider)
        mock_model_class = mocker.patch("ai.core.openrouter.OpenRouterModel")
        mocker.patch("httpx.AsyncClient")

        model = create_openrouter_model("anthropic/claude-sonnet-4.5")

        # Test that caching was enabled for Anthropic model
        call_args = mock_model_class.call_args
        extra_body = call_args.kwargs["settings"]["extra_body"]
        assert "caching" in extra_body
        assert extra_body["caching"]["enabled"] is True

    def test_create_openrouter_model_non_anthropic_no_caching(self, mocker):
        """Test that non-Anthropic models don't get caching."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        mock_provider = MagicMock()
        mock_profile = MagicMock()
        mock_profile.supports_json_schema_output = True
        mock_provider.model_profile.return_value = mock_profile

        mocker.patch("ai.core.openrouter.OpenRouterProvider", return_value=mock_provider)
        mock_model_class = mocker.patch("ai.core.openrouter.OpenRouterModel")
        mocker.patch("httpx.AsyncClient")

        model = create_openrouter_model("openai/gpt-5")

        # Test that caching was NOT enabled for non-Anthropic model
        call_args = mock_model_class.call_args
        extra_body = call_args.kwargs["settings"]["extra_body"]
        assert "caching" not in extra_body

    def test_create_openrouter_model_profile_override(self, mocker):
        """Test profile override for broken model profiles."""
        if not config.openrouter_api_key:
            pytest.skip("No API key configured")

        mock_provider = MagicMock()
        mock_profile = MagicMock()
        mock_profile.supports_json_schema_output = False  # Broken profile
        mock_provider.model_profile.return_value = mock_profile

        mocker.patch("ai.core.openrouter.OpenRouterProvider", return_value=mock_provider)
        mock_model_class = mocker.patch("ai.core.openrouter.OpenRouterModel")
        mocker.patch("httpx.AsyncClient")
        mock_replace = mocker.patch("ai.core.openrouter.replace")

        model = create_openrouter_model("anthropic/claude-sonnet-4.5")

        # Test that profile was overridden to fix JSON schema support
        mock_replace.assert_called_once()
        call_args = mock_model_class.call_args
        assert call_args.kwargs["profile"] is not None


class TestOpenRouterSettings:
    """Test suite for OpenRouter settings."""

    def test_openrouter_settings_basic(self):
        """Test basic OpenRouter settings creation."""
        settings = OpenRouterSettings(
            reasoning_effort="high", fallback_models=["anthropic/claude-3.5-haiku"]
        )

        assert settings.reasoning_effort == "high"
        assert settings.fallback_models == ["anthropic/claude-3.5-haiku"]
        assert settings.include_reasoning_tokens is True

    def test_openrouter_settings_to_request_body(self):
        """Test conversion to request body format."""
        settings = OpenRouterSettings(
            reasoning_effort="medium", fallback_models=["model1", "model2"]
        )

        body = settings.to_request_body()

        assert "reasoning" in body
        assert body["reasoning"]["effort"] == "medium"
        assert body["reasoning"]["enabled"] is True
        assert body["models"] == ["model1", "model2"]

    def test_openrouter_settings_no_reasoning(self):
        """Test settings without reasoning effort."""
        settings = OpenRouterSettings(fallback_models=["model1"])

        body = settings.to_request_body()

        assert "reasoning" not in body
        assert body["models"] == ["model1"]


class TestCachingSettings:
    """Test suite for caching settings."""

    def test_caching_settings_defaults(self):
        """Test default caching settings."""
        settings = CachingSettings()

        assert settings.enabled is True
        assert settings.cache_system_messages is True
        assert settings.cache_tools is True
        assert settings.cache_user_messages is False

    def test_caching_settings_custom(self):
        """Test custom caching settings."""
        settings = CachingSettings(enabled=False, cache_user_messages=True)

        assert settings.enabled is False
        assert settings.cache_user_messages is True
        assert settings.cache_system_messages is True  # Default
