"""Application configuration and runtime settings."""
from functools import lru_cache
from typing import Optional

from pydantic import AliasChoices, AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=(".env",), env_file_encoding="utf-8", extra="ignore", populate_by_name=True
    )

    # Model endpoints
    oss_model_endpoint: AnyHttpUrl = Field(..., alias="OSS_MODEL_ENDPOINT")
    oss_model_api_key: Optional[str] = Field(default=None, alias="OSS_MODEL_API_KEY")
    oss_model_id: str = Field(default="openai/gpt-oss-20b", alias="OSS_MODEL_ID")
    codex_api_key: str = Field(..., validation_alias=AliasChoices("CODEX_API_KEY", "OPENAI_API_KEY"))

    # Agent framework
    agent_framework_devui_enabled: bool = Field(default=True, alias="AGENT_FRAMEWORK_DEVUI_ENABLED")
    agent_framework_agui_enabled: bool = Field(default=True, alias="AGENT_FRAMEWORK_AGUI_ENABLED")
    agui_requested_by: str = Field(default="agui-user", alias="AGUI_REQUESTED_BY")

    # Terraform / infrastructure
    tf_cli_path: str = Field(default="terraform", alias="TF_CLI_PATH")
    tf_backend_rg: Optional[str] = Field(default=None, alias="TF_BACKEND_RG")
    tf_backend_account: Optional[str] = Field(default=None, alias="TF_BACKEND_ACCOUNT")
    tf_backend_container: Optional[str] = Field(default=None, alias="TF_BACKEND_CONTAINER")

    # Git
    gitops_repo_path: str = Field(default="./gitops", alias="GITOPS_REPO_PATH")
    default_project_id: Optional[str] = Field(default=None, alias="DEFAULT_PROJECT_ID")
    default_repo_url: Optional[AnyHttpUrl] = Field(default=None, alias="DEFAULT_REPO_URL")
    default_workspace_dir: Optional[str] = Field(default=None, alias="DEFAULT_WORKSPACE_DIR")
    default_terraform_workspace: Optional[str] = Field(default=None, alias="DEFAULT_TERRAFORM_WORKSPACE")
    default_branch: str = Field(default="main", alias="DEFAULT_BRANCH")
    default_environment: str = Field(default="dev", alias="DEFAULT_ENVIRONMENT")

    # Projects / onboarding
    projects_root: str = Field(default="./projects", alias="PROJECTS_ROOT")

    # Misc env
    database_url: str = Field(default="sqlite+aiosqlite:///./agent.db", alias="DATABASE_URL")
    environment: str = Field(default="dev", alias="ENVIRONMENT")
    tools_install_dir: str = Field(default=".tools/bin", alias="TOOLS_INSTALL_DIR")
    tools_auto_install: bool = Field(default=True, alias="TOOLS_AUTO_INSTALL")


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
