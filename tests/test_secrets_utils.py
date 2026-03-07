from lakeops.core.secrets.utils import redact_secret


def test_redact_secret_empty_value():
    assert redact_secret("") == ""
    assert redact_secret("", show_chars=2) == ""


def test_redact_secret_short_value():
    # When the value length is <= show_chars, everything should be masked
    assert redact_secret("abcd", show_chars=4) == "****"
    assert redact_secret("abc", show_chars=4) == "***"


def test_redact_secret_long_value():
    value = "supersecrettoken"
    redacted = redact_secret(value, show_chars=5)
    # Length stays the same
    assert len(redacted) == len(value)
    # Last N characters are preserved
    assert redacted.endswith("token")
    # The prefix is masked
    assert set(redacted[:-5]) == {"*"}

