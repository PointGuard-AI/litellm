from typing import Literal

from pydantic import Field

from .base import GuardrailConfigModel


class PointGuardAIGuardrailConfigModel(GuardrailConfigModel):  # pyright: ignore[reportMissingTypeArgument]  # parameterizing adds an optional_params field to the UI form
    """Configuration parameters for the PointGuardAI v2 guardrail"""

    org_code: str | None = Field(
        default=None,
        description="Organization code for PointGuardAI. Reads from POINTGUARD_ORG_CODE when unset.",
    )
    api_base: str | None = Field(
        default=None,
        description=(
            "Base URL for PointGuardAI. Reads from POINTGUARD_API_BASE when unset, "
            "then defaults to https://api.appsoc.com."
        ),
    )
    api_key: str | None = Field(
        default=None,
        description="API key for PointGuardAI. Reads from POINTGUARD_API_KEY when unset.",
    )
    policy_config_name: str | None = Field(
        default=None,
        description="PointGuardAI policy name. Reads from POINTGUARD_POLICY_NAME when unset.",
    )
    unreachable_fallback: Literal["fail_closed", "fail_open"] = Field(
        default="fail_closed",
        description=(
            "Behavior when PointGuardAI is unreachable. 'fail_closed' raises an error "
            "(default); 'fail_open' logs a critical error and allows the request."
        ),
    )
    max_turns: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Most recent conversation turns sent to PointGuardAI for input inspection, where a turn is a user "
            "message and the messages after it. PointGuardAI inspects the last message and reads the earlier "
            "ones as context. Defaults to 20 when unset."
        ),
    )

    @staticmethod
    def ui_friendly_name() -> str:
        return "PointGuard AI"
