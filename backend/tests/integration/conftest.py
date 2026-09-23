from pathlib import Path

from dotenv import load_dotenv

# Fills in API keys from a local .env for developers running these tests
# outside of CI. In CI the keys already come from GitHub Secrets via the
# workflow's `env:` block, so override=False leaves them untouched and this
# becomes a no-op when the file doesn't exist.
load_dotenv(Path(__file__).parent / ".env", override=False)
