from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Final, Protocol

from litellm.secret_managers.main import get_secret_str
from litellm.types.guardrails import (
    GuardrailEventHooks,
    Mode,
    SupportedGuardrailIntegrations,
)

from .pointguardai import PointGuardAIGuardrail

if TYPE_CHECKING:
    from litellm.types.guardrails import Guardrail, LitellmParams

_NO_EXTRAS: Final[Mapping[str, object]] = MappingProxyType({})


class _CallbackRegistrar(Protocol):
    def add_litellm_callback(self, callback: PointGuardAIGuardrail) -> None: ...


def _resolve_secret_reference(value: object) -> str | None:
    if value is None:
        return None
    text: Final = str(value)
    return get_secret_str(text) if text.startswith("os.environ/") else text


def _optional_int(value: object) -> int | None:
    """``value`` as an int, or None when unset: the dashboard may send numbers as strings."""
    if value is None or value == "":
        return None
    return int(str(value))


def _coerce_event_hook(
    mode: str | list[str] | Mode,  # mutable-ok: mirrors the LiteLLM mode configuration contract
) -> GuardrailEventHooks | list[GuardrailEventHooks] | Mode:  # mutable-ok: inherited hook API requires a list
    if isinstance(mode, Mode):
        return mode
    if isinstance(mode, list):
        return [GuardrailEventHooks(item) for item in mode]
    return GuardrailEventHooks(mode)


def initialize_guardrail(
    litellm_params: "LitellmParams",
    guardrail: "Guardrail",
    callback_manager: _CallbackRegistrar | None = None,
) -> PointGuardAIGuardrail:
    import litellm

    extras: Final = litellm_params.model_extra or _NO_EXTRAS
    pointguardai_guardrail: Final = PointGuardAIGuardrail(
        guardrail_name=guardrail["guardrail_name"],
        api_key=litellm_params.api_key,
        api_base=litellm_params.api_base,
        org_code=_resolve_secret_reference(extras.get("org_code")),
        policy_config_name=_resolve_secret_reference(extras.get("policy_config_name")),
        unreachable_fallback=litellm_params.unreachable_fallback,
        max_turns=_optional_int(extras.get("max_turns")),
        default_on=litellm_params.default_on or False,
        event_hook=_coerce_event_hook(litellm_params.mode),
    )

    if callback_manager is None:
        litellm.logging_callback_manager.add_litellm_callback(pointguardai_guardrail)
    else:
        callback_manager.add_litellm_callback(pointguardai_guardrail)
    return pointguardai_guardrail


guardrail_initializer_registry: Final = {
    SupportedGuardrailIntegrations.POINTGUARDAI.value: initialize_guardrail,
}


guardrail_class_registry: Final = {
    SupportedGuardrailIntegrations.POINTGUARDAI.value: PointGuardAIGuardrail,
}


__all__: Final = (
    "PointGuardAIGuardrail",
    "guardrail_class_registry",
    "guardrail_initializer_registry",
    "initialize_guardrail",
)
