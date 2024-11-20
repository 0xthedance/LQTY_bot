
import pytest

from lib.logging import configure_logging
from silverback import SilverbackBot


@pytest.fixture
def silverback_bot():
    app = SilverbackBot()
    return app

logger = configure_logging()
