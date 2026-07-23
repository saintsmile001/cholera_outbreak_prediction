import importlib

import app.core.config as config_module


def test_settings_reads_smtp_values_from_repo_root_env():
    reloaded = importlib.reload(config_module)

    assert reloaded.settings.SMTP_HOST == "smtp.gmail.com"
    assert reloaded.settings.SMTP_PORT == 587
    assert reloaded.settings.SENDER_NAME == "CholeraGuard AI Surveillance System"
