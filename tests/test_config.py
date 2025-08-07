import argparse
import pytest
from chapito.config import DEFAULT_BROWSER_PROFILE_PATH, DEFAULT_USE_BROWSER_PROFILE, Config
from unittest.mock import patch


@pytest.mark.parametrize(
    "cli_config, cli_use_browser_profile, cli_profile_path, "
    "file_use_browser_profile, file_profile_path, "
    "expected_config_path, expected_use_browser_profile, expected_profile_path",
    [
        # Happy path tests
        (
            "config_test.ini",
            True,
            "cli_profile",
            True,
            "file_profile",
            "config_test.ini",
            True,
            "cli_profile",
        ),  # id: cli_overrides_file
        (
            None,
            None,
            None,
            False,
            None,
            "config.ini",
            DEFAULT_USE_BROWSER_PROFILE,
            DEFAULT_BROWSER_PROFILE_PATH,
        ),  # id: default_values_used
        # Edge cases
        (
            None,
            True,
            None,
            False,
            None,
            "config.ini",
            True,
            DEFAULT_BROWSER_PROFILE_PATH,
        ),  # id: cli_use_browser_profile_true_no_path
        (
            None,
            False,
            "cli_profile",
            False,
            None,
            "config.ini",
            False,
            "cli_profile",
        ),  # id: cli_profile_path_without_use_browser_profile
        # Error cases - invalid config file
        (
            "invalid_config.ini",
                None,
            None,
            False,
            None,
            "invalid_config.ini",
                True,
            DEFAULT_BROWSER_PROFILE_PATH,
        ),  # id: invalid_config_file
    ],
)
def test_config_initialization(
    cli_config,
    cli_use_browser_profile,
    cli_profile_path,
    file_use_browser_profile,
    file_profile_path,
    expected_config_path,
    expected_use_browser_profile,
    expected_profile_path,
    tmp_path,
):
    # Arrange
    config_file_content = f"""
[DEFAULT]
use_browser_profile = {str(file_use_browser_profile)}
browser_profile_path = {file_profile_path}
"""
    config_file = tmp_path / "config_test.ini"
    config_file.write_text(config_file_content)

    invalid_config_file = tmp_path / "invalid_config.ini"
    invalid_config_file.write_text("invalid config")

    cli_args = []
    if cli_config:
        cli_args.extend(["--config", str(cli_config)])
    if cli_use_browser_profile is not None:
        cli_args.append("--use-browser-profile") if cli_use_browser_profile else None
    if cli_profile_path:
        cli_args.extend(["--profile-path", cli_profile_path])

    with patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            **{
                "config": cli_config or "config.ini",
                "chatbot": None,
                "stream": False,
                "no_stream": False,
                "use_browser_profile": cli_use_browser_profile,
                "profile_path": cli_profile_path,
                "user_agent": "",
                "verbosity": None,
                "host": None,
                "port": None,
            }
        ),
    ):

        # Act
        config = Config()

        # Assert
        assert config.config_path == (cli_config if cli_config == "config_test.ini" else expected_config_path)
        assert config.use_browser_profile == expected_use_browser_profile
        assert config.browser_profile_path == expected_profile_path
