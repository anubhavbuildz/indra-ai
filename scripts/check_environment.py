"""Check local tool/configuration readiness without printing secrets."""

import shutil

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    terraform_available = shutil.which(settings.terraform_bin) is not None
    nvidia_configured = bool(
        settings.nvidia_api_key
        and settings.nvidia_base_url
        and settings.nvidia_model
        and settings.nvidia_api_format
    )
    print(f"Python application settings: loaded ({settings.app_env})")
    print(f"Terraform executable: {'available' if terraform_available else 'not found'}")
    print(f"NVIDIA inference: {'configured' if nvidia_configured else 'not configured'}")
    print("AWS credentials: checked only when /api/v1/aws/identity is called")
    print("FAISS index: configured" if settings.faiss_index_path.exists() else "FAISS index: not built")


if __name__ == "__main__":
    main()
