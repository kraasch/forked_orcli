# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from pathlib import Path
import tempfile

from orcli import Refine


# Configure logging for this example.
#
# The library uses logging.getLogger(__name__) in client.py,
# so the logger name is "orcli.client".
logger = logging.getLogger("orcli.client")

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        "%(levelname)s: %(message)s"
    )
)

logger.addHandler(handler)
logger.propagate = False


def run_successful_workflow(level: int, level_name: str) -> None:
    """Run a successful workflow at the specified log level."""

    print()
    print("=" * 60)
    print(f"Logging level: {level_name}")
    print("=" * 60)

    logger.setLevel(level)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S-%f"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_file = (
            Path(tmp_dir)
            / f"logging_example_{timestamp}.csv"
        )

        csv_file.write_text(
            "name,age\n"
            "Alice,30\n"
            "Bob,25\n",
            encoding="utf-8",
        )

        project_name = (
            f"Project Name Test Example 05 "
            f"{level_name} {timestamp}"
        )

        refine = Refine()

        try:
            project_id = refine.create_project(
                project_file=str(csv_file),
                project_name=project_name,
            )

            refine.get_models(project_id)

        finally:
            if refine.project_id:
                refine.delete_project(refine.project_id)


def run_error_workflow() -> None:
    """Demonstrate ERROR logging."""

    print()
    print("=" * 60)
    print("Logging level: ERROR")
    print("=" * 60)

    logger.setLevel(logging.ERROR)

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S-%f"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        missing_file = (
            Path(tmp_dir)
            / f"does_not_exist_{timestamp}.csv"
        )

        refine = Refine()

        try:
            refine.create_project(
                project_file=str(missing_file),
                project_name=f"Logging ERROR {timestamp}",
            )
        except FileNotFoundError:
            print("Expected FileNotFoundError was raised.")


def main() -> None:
    """Run the logging example for the different log levels."""

    try:
        # DEBUG:
        # Shows DEBUG, INFO, WARNING, ERROR and CRITICAL messages.
        run_successful_workflow(
            logging.DEBUG,
            "DEBUG",
        )

        # INFO:
        # Shows INFO, WARNING, ERROR and CRITICAL messages.
        # DEBUG messages are suppressed.
        run_successful_workflow(
            logging.INFO,
            "INFO",
        )

        # WARNING:
        # Shows WARNING, ERROR and CRITICAL messages.
        # The successful Refine workflow currently produces
        # no WARNING messages.
        run_successful_workflow(
            logging.WARNING,
            "WARNING",
        )

        # ERROR:
        # The successful workflow produces no ERROR messages,
        # so run a deliberate failure to demonstrate ERROR logging.
        run_error_workflow()

    finally:
        # Restore the logger configuration so this example does
        # not leave global logger state behind.
        logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)
        logger.propagate = True


if __name__ == "__main__":
    main()

