#!/usr/bin/env python
# coding: utf-8

import errno
import os
import yaml

from utils import dict_merge

ROOT_PATH = os.path.dirname(os.path.realpath(__file__)) + os.sep + '..' + os.sep

class Config():
    def __init__(self):
        self.conf = self._load()

    def _load(self):
        f_path_tmpl = ROOT_PATH + "config_template.yml"
        f_path_user = ROOT_PATH + "config.yml"

        # Create config.yml if it doesn't exist
        try:
            with open(f_path_user, 'x') as f_user:
                pass
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Parse files "config_template.yml" and "config.yml"
        with open(f_path_tmpl, "r") as f_tmpl, open(f_path_user, "r") as f_user:
            # Load template config and override with user values
            conf = yaml.load(f_tmpl)
            dict_merge(conf, yaml.load(f_user) or {})

            conf_final = conf.copy()

            # Add path to filenames
            conf_final['db']['uri'] = 'sqlite:///' + ROOT_PATH + conf_final['db']['name']

            return conf_final
