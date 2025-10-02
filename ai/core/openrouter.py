"""OpenRouter model management for 100x agents.

This module provides sophisticated OpenRouter integration with:
- HTTP transport interceptor for proper parameter injection
- Anthropic prompt caching for cost savings
- Automatic fallback routing
- Comprehensive token cost tracking
"""

from dataclasses import dataclass, replace
from typing import Any, Literal

from pydantic import BaseModel, Field
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models.openai import OpenAIChatModel, chat
from pydantic_ai.providers.openrouter import OpenRouterProvider
import arrow
import httpx
import ujson

from ai.core.config import config
from helpers.logger import logger
from helpers.observability import logfire

# Suppress linter warnings for accessing private attributes (necessary for interceptors)
# ruff: noqa: SLF001

# Model registry with pricing and fallbacks
SUPPORTED_MODELS = {
    "anthropic/claude-opus-4.1": {
        "name": "Claude Opus 4.1",
        "description": "Most capable Claude model for complex reasoning",
        "context_window": 200_000,
        "max_output": 32_000,
        "supports_vision": True,
        "pricing": {"input_per_million": 15.0, "output_per_million": 75.0},
        "recommended_for": ["complex_analysis", "strategic_decisions"],
        "fallback_models": ["openai/o1-pro", "anthropic/claude-sonnet-4.5"],
    },
    "anthropic/claude-sonnet-4.5": {
        "name": "Claude Sonnet 4.5",
        "description": "Latest Claude model - excellent for agent operations",
        "context_window": 200_000,
        "max_output": 64_000,
        "supports_vision": True,
        "pricing": {"input_per_million": 3.0, "output_per_million": 15.0},
        "recommended_for": ["general_use", "agent_operations", "code_generation"],
        "fallback_models": ["anthropic/claude-3.5-haiku", "openai/gpt-5"],
    },
    "anthropic/claude-3.5-haiku": {
        "name": "Claude 3.5 Haiku",
        "description": "Fast, efficient Claude for simple tasks",
        "context_window": 200_000,
        "max_output": 8_192,
        "supports_vision": False,
        "pricing": {"input_per_million": 1.0, "output_per_million": 5.0},
        "recommended_for": ["quick_analysis", "high_volume"],
        "fallback_models": ["openai/gpt-5-mini"],
    },
    "openai/gpt-5": {
        "name": "GPT-5",
        "description": "OpenAI's most advanced model with superior reasoning",
        "context_window": 400_000,
        "max_output": 16_384,
        "supports_vision": True,
        "pricing": {"input_per_million": 1.25, "output_per_million": 10.0},
        "recommended_for": ["complex_analysis", "strategic_decisions"],
        "fallback_models": ["anthropic/claude-sonnet-4.5", "openai/gpt-5-mini"],
    },
    "openai/gpt-5-mini": {
        "name": "GPT-5 Mini",
        "description": "Fast, cost-effective for most tasks",
        "context_window": 128_000,
        "max_output": 16_384,
        "supports_vision": True,
        "pricing": {"input_per_million": 0.15, "output_per_million": 0.6},
        "recommended_for": ["quick_decisions", "vision_analysis"],
        "fallback_models": ["anthropic/claude-3.5-haiku"],
    },
    "openai/o1-pro": {
        "name": "O1 Pro",
        "description": "Advanced reasoning model",
        "context_window": 128_000,
        "max_output": 100_000,
        "supports_vision": False,
        "pricing": {"input_per_million": 15.0, "output_per_million": 60.0},
        "recommended_for": ["deep_reasoning", "strategy_development"],
        "fallback_models": ["anthropic/claude-opus-4.1"],
    },
}


# HTTP Transport Interceptor
class OpenRouterTransport(httpx.AsyncHTTPTransport):
    """Custom HTTP transport that intercepts OpenRouter requests and properly
    injects reasoning/routing parameters at the top level of the JSON body.
    """

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Intercept and modify OpenRouter chat completion requests."""
        if (
            "/chat/completions" in request.url.path
            and request.method == "POST"
            and request.content
        ):
            # Parse the JSON request body
            body = ujson.loads(request.content)

            # Extract OpenRouter parameters from extra_body if present
            extra_body = body.get("extra_body", {})

            if extra_body and isinstance(extra_body, dict):
                # Extract reasoning and fallback_models parameters
                openrouter_reasoning = extra_body.pop("reasoning", None)
                openrouter_fallback_models = extra_body.pop("models", None)

                # Inject at top level of request body
                if openrouter_reasoning:
                    body["reasoning"] = openrouter_reasoning

                if openrouter_fallback_models:
                    body["models"] = openrouter_fallback_models

                # Clean up extra_body - remove it entirely if now empty
                if not extra_body:
                    body.pop("extra_body", None)
                else:
                    body["extra_body"] = extra_body

                # Update the request with modified body
                request._content = ujson.dumps(body).encode()
                request.content = request._content
                request.headers["content-length"] = str(len(request._content))

                logger.debug(
                    f"🔧 Modified OpenRouter request: reasoning={bool(openrouter_reasoning)}, "
                    f"fallbacks={len(openrouter_fallback_models) if openrouter_fallback_models else 0}"
                )

            # Log the request to Logfire
            logfire.info(
                "📝 Sending OpenRouter LLM request",
                endpoint=str(request.url),
                request_body=body,
                operation="llm_request",
            )

        # Continue with the (possibly modified) request
        return await super().handle_async_request(request)


# OpenRouter Settings
class OpenRouterSettings(BaseModel):
    """OpenRouter-specific settings for advanced features."""

    model_config = {"extra": "forbid"}

    reasoning_effort: Literal["low", "medium", "high"] | None = Field(
        default=None, description="Reasoning effort level for compatible models"
    )
    include_reasoning_tokens: bool = Field(
        default=True, description="Include reasoning tokens in the response"
    )
    fallback_models: list[str] | None = Field(
        default=None, description="List of fallback models for routing"
    )

    def to_request_body(self) -> dict[str, Any]:
        """Convert OpenRouter settings to request body format."""
        request_additions = {}

        # Handle reasoning parameters
        reasoning_config = {}

        if self.reasoning_effort:
            reasoning_config["effort"] = self.reasoning_effort

        if self.reasoning_effort or not self.include_reasoning_tokens:
            reasoning_config["exclude"] = not self.include_reasoning_tokens

        if reasoning_config:
            reasoning_config["enabled"] = True
            request_additions["reasoning"] = reasoning_config

        # Handle model routing
        if self.fallback_models:
            request_additions["models"] = self.fallback_models

        return request_additions

    def to_openrouter_body(self) -> dict[str, Any]:
        """Convert OpenRouter settings to openrouter_body format for HTTP transport."""
        return self.to_request_body()


# Caching Settings
class CachingSettings(BaseModel):
    """Settings for Anthropic prompt caching support."""

    model_config = {"extra": "forbid"}

    enabled: bool = Field(default=True, description="Enable Anthropic prompt caching")
    cache_system_messages: bool = Field(
        default=True, description="Cache system messages"
    )
    cache_tools: bool = Field(default=True, description="Cache tool definitions")
    cache_user_messages: bool = Field(default=False, description="Cache user messages")


# Enhanced OpenRouter Model
@dataclass(init=False)
class OpenRouterModel(OpenAIChatModel):
    """Enhanced OpenRouter model with HTTP transport interceptor and caching."""

    def __post_init__(self):
        """Initialize with custom OpenRouter transport."""
        super().__post_init__()

        # Replace the HTTP transport with our custom interceptor
        if hasattr(self.client, "_client") and hasattr(
            self.client._client, "_transport"
        ):
            old_transport = self.client._client._transport

            self.client._client._transport = OpenRouterTransport(
                verify=old_transport._verify,
                cert=old_transport._cert,
                trust_env=old_transport._trust_env,
                http2=old_transport._http2,
                limits=old_transport._limits,
                proxy=old_transport._proxy,
                socket_options=old_transport._socket_options,
                uds=old_transport._uds,
            )
        else:
            logger.error(
                "❌ Failed to install OpenRouter transport - client structure unexpected"
            )

    async def _map_messages(self, messages: list[Any]) -> list[dict[str, Any]]:
        """Override message mapping to inject Anthropic cache_control."""
        mapped_messages = await super()._map_messages(messages)

        # Check if caching is enabled in settings
        caching_settings = self._settings.get("extra_body", {}).get("caching")
        if not caching_settings or not caching_settings["enabled"]:
            return mapped_messages

        # Process each message for caching
        for mapped in mapped_messages:
            should_cache = False
            message_role = mapped["role"]

            if (
                message_role == "system" and caching_settings["cache_system_messages"]
            ) or (message_role == "user" and caching_settings["cache_user_messages"]):
                should_cache = True

            if should_cache:
                # Convert string content to multipart format for cache_control
                content = mapped["content"]
                if isinstance(content, str):
                    mapped["content"] = [
                        {
                            "type": "text",
                            "text": content,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ]
                    logger.info(f"💾 Added cache_control to {message_role} message")
                elif isinstance(content, list) and len(content) > 0:
                    # Add cache_control to the last text block
                    for i in range(len(content) - 1, -1, -1):
                        if content[i]["type"] == "text":
                            content[i]["cache_control"] = {"type": "ephemeral"}
                            logger.info(
                                f"💾 Added cache_control to {message_role} message"
                            )
                            break

        return mapped_messages

    def _map_tool_definition(self, f: Any) -> dict[str, Any]:
        """Override tool definition mapping to inject Anthropic cache_control."""
        mapped_tool = super()._map_tool_definition(f)

        # Check if caching is enabled
        caching_settings = self._settings.get("extra_body", {}).get("caching")
        if not caching_settings or not caching_settings["enabled"]:
            return mapped_tool

        # Add cache_control to tool definitions if enabled
        if caching_settings["cache_tools"]:
            mapped_tool["cache_control"] = {"type": "ephemeral"}
            logger.info(
                f"💾 Added cache_control to tool: {mapped_tool['function']['name']}"
            )

        return mapped_tool

    def _process_response(self, response: chat.ChatCompletion) -> ModelResponse:
        """Set created timestamp if missing and handle OpenRouter-specific responses."""
        # Handle None response
        if response is None:
            logger.error("Received None response from OpenRouter")
            raise ModelHTTPError(
                status_code=502,
                model_name=self.model_name,
                body={"error": "Received None response from OpenRouter"},
            )

        # OpenRouter might not set the created field
        if not hasattr(response, "created") or response.created is None:
            response.created = int(arrow.now().timestamp())

        # OpenRouter might return None for choices array
        if not hasattr(response, "choices") or response.choices is None:
            logger.error("🚨 OpenRouter returned response with no choices")
            raise ModelHTTPError(
                status_code=502,
                model_name=self.model_name,
                body={"error": "OpenRouter returned response with no choices"},
            )

        # Check if OpenRouter responded with a different model (fallback occurred)
        if (
            hasattr(response, "model")
            and response.model
            and response.model != self.model_name
        ):
            logger.warning(
                f"⚠️ OpenRouter fallback: requested {self.model_name} → received {response.model}"
            )
            logfire.warning(
                "OpenRouter model fallback",
                requested_model=self.model_name,
                received_model=response.model,
                operation="model_fallback",
            )

        return super()._process_response(response)


# Main Functions
def create_openrouter_model(
    model_name: str,
    timeout: float = 60.0,
    agent_name: str = "Agent",
    settings: dict[str, Any] | None = None,
    enable_prompt_caching: bool = True,
) -> OpenAIChatModel:
    """Create a model configured for OpenRouter with advanced features.

    Args:
        model_name: Full model name (e.g., 'anthropic/claude-sonnet-4')
        timeout: Request timeout in seconds
        agent_name: Name for OpenRouter tracking headers
        settings: Optional model settings (temperature, etc.)
        enable_prompt_caching: Enable Anthropic prompt caching (Anthropic models only)

    Returns:
        Configured OpenRouter model with all enhancements

    Raises:
        ValueError: If model not supported or API key not configured
    """
    if not config.openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not configured. Add it to your .env file to make LLM calls."
        )

    # Validate model exists
    if model_name not in SUPPORTED_MODELS:
        available = ", ".join(SUPPORTED_MODELS.keys())
        raise ValueError(
            f"Model '{model_name}' not supported. Available models: {available}"
        )

    # Get fallback models from registry
    model_specs = SUPPORTED_MODELS[model_name]
    fallback_models = model_specs["fallback_models"]

    # Prepare settings with OpenRouter routing
    final_settings = settings.copy() if settings else {}

    # Always ensure extra_body exists
    if "extra_body" not in final_settings:
        final_settings["extra_body"] = {}

    # Set up model routing
    final_settings["extra_body"]["models"] = fallback_models

    # Set up caching configuration - Only for Anthropic models
    if enable_prompt_caching and model_name.startswith("anthropic/"):
        final_settings["extra_body"]["caching"] = {
            "enabled": True,
            "cache_system_messages": True,
            "cache_tools": True,
            "cache_user_messages": False,
        }

    # Create HTTP client with timeout and headers
    http_client = httpx.AsyncClient(
        timeout=timeout,
        headers={
            "HTTP-Referer": "https://100x.ai/",
            "X-Title": f"100x - {agent_name}",
        },
        http2=False,  # Disable HTTP/2
    )

    # Create provider
    provider = OpenRouterProvider(
        api_key=config.openrouter_api_key, http_client=http_client
    )

    # Enable JSON schema output for all models (universal fix)
    profile_override = None
    original_profile = provider.model_profile(model_name)

    if original_profile and not original_profile.supports_json_schema_output:
        corrected_profile = replace(original_profile, supports_json_schema_output=True)
        profile_override = corrected_profile
        logger.debug(f"Enabled native JSON schema output for {model_name}")

    # Create model with OpenRouter enhancements
    model = OpenRouterModel(
        model_name=model_name,
        provider=provider,
        profile=profile_override,
        settings=final_settings,
    )

    # Log setup info
    extra_body = final_settings["extra_body"]
    reasoning_config = extra_body.get("reasoning", {})
    reasoning_level = (
        reasoning_config.get("effort") if isinstance(reasoning_config, dict) else None
    )

    # Build log message
    log_parts = [f"🏗️ Created OpenRouter model: {model_name}"]

    if fallback_models:
        log_parts.append(f"fallbacks: {fallback_models}")

    if reasoning_level:
        log_parts.append(f"reasoning: {reasoning_level}")

    if enable_prompt_caching and model_name.startswith("anthropic/"):
        log_parts.append("💾 caching: enabled")

    if settings:
        interesting_settings = {k: v for k, v in settings.items() if k != "extra_body"}
        if interesting_settings:
            log_parts.append(f"settings: {interesting_settings}")

    log_parts.append(f"agent: {agent_name}")

    logger.info(" | ".join(log_parts))

    return model


def get_model_info(model_name: str) -> dict[str, Any]:
    """Get information about a supported model."""
    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Model '{model_name}' not supported")
    return SUPPORTED_MODELS[model_name]


def get_fallback_models(model_name: str) -> list[str]:
    """Get fallback models for a given model."""
    model_info = get_model_info(model_name)
    return model_info["fallback_models"]


def estimate_token_cost(
    model_name: str, input_tokens: int, output_tokens: int
) -> float:
    """Estimate the cost of a model invocation."""
    model_info = get_model_info(model_name)
    pricing = model_info["pricing"]

    input_cost = (input_tokens / 1_000_000) * pricing["input_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_million"]

    return input_cost + output_cost


def list_supported_models() -> list[str]:
    """Get a list of all supported model identifiers."""
    return list(SUPPORTED_MODELS.keys())


def get_builtin_models() -> dict[str, Any]:
    """Get the built-in model registry."""
    return SUPPORTED_MODELS
