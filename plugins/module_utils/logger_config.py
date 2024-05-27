# Copyright 2024 Cisco Systems, Inc. and its affiliates
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
from pathlib import Path


def configure_logger(name, logfile_dir: str = "", loglevel: logging = logging.INFO) -> logging.Logger:
    if not logfile_dir:
        logfile_dir = os.getcwd()
    logs_results_path = Path(logfile_dir)
    logfile_path = Path(logs_results_path / f"{name}.log")  # Include datatime timestamps in the future

    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    file_handler = logging.FileHandler(logfile_path, mode="a")
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(threadName)-10s] %(message)s",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
