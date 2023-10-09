#  logging.py

import os
import sys
import json
import logging.config
import getpass
import threading


class ColoredFormatter(logging.Formatter):
	grey = "\\x1b[38;21m"
	yellow = "\\x1b[33;21m"
	red = "\\x1b[31;21m"
	bold_red = "\\x1b[31;1m"
	reset = "\\x1b[0m"
	format = "%(asctime)s - %(name)s - %(levelname)8s - %(message)s"
	datefmt = "%m/%d/%Y %I:%M:%S %p"

	FORMATS = {
		logging.DEBUG: grey + format + reset,
		logging.INFO: grey + format + reset,
		logging.WARNING: yellow + format + reset,
		logging.ERROR: red + format + reset,
		logging.CRITICAL: bold_red + format + reset
	}

	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)


default_config = {
	"version": 1,
	"disable_existing_loggers": False,

	"formatters": {
		"basic": {
			'()': 'utils.log_config.ColoredFormatter'
		},
		"log_format": {
			"format": "%(asctime)s - %(name)s - %(levelname)8s : %(message)s",
			"datefmt": "%m/%d/%Y %I:%M:%S %p"
        },
		"json": {
			"format": "name: %(name)s, level: %(levelname)s, time: %(asctime)s, message: %(message)s"
		},
	},

	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"level": "INFO",
			"formatter": "basic",
			"stream": "ext://sys.stdout"
		},
		"local_file_handler": {
			"class": "logging.handlers.RotatingFileHandler",
			"level": "DEBUG",
			"formatter": "log_format",
			"filename": "debug.log",
			"maxBytes": 1048576,
			"backupCount": 20,
			"encoding": "utf8",
			"delay" : True
		},
	},

	"loggers": {
		"classes": {
			"level": "INFO",
			"propagate": True
		},
		"message": {
			"level": "INFO",
			"propagate": True,
			"handlers": ["console"]
		}
	},

	"root": {
		"level": "INFO",
		"handlers": ["console","local_file_handler"],
	}
}


class ThreadContextFilter(logging.Filter):
	"""A logging context filter to add thread name and ID."""
	def filter(self, record):
		record.thread_id = str(threading.current_thread().ident)
		record.thread_name = str(threading.current_thread().name)
		return True


def setup_logging(
		default_log_config=None,
		default_level=logging.INFO,
		env_key='LOG_CFG'
		):
	dict_config = None
	logconfig_filename = default_log_config
	env_var_value = os.getenv(env_key, None)

	if env_var_value is not None:
		logconfig_filename = env_var_value

	if default_config is not None:
		dict_config = default_config

	if logconfig_filename is not None and os.path.exists(logconfig_filename):
		with open(logconfig_filename, 'rt') as f:
			file_config = json.load(f)
		if file_config is not None:
			dict_config = file_config

	if dict_config is not None:
		logging.config.dictConfig(dict_config)
	else:
		logging.basicConfig(level=default_level)


