from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    llm_model: str = "claude-opus-5-5"
    database_url: str = "sqlite:///./hvac_agent.db"
    checklist_dir: Path = ROOT / "config" / "checklists"
    syntess_mode: str = "mock"
    exact_mode: str = "mock"


settings = Settings()
