# app/core/logging_config.py

import logging
import sys

def configure_logging():
    """
    Configure logging with proper formatting that includes stack traces.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Ensure exceptions are logged with full tracebacks
    logging.getLogger().setLevel(logging.INFO)
