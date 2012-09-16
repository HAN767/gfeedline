import os
import json
from gi.repository import Gtk

from ..constants import CONFIG_HOME


class ListStoreBase(Gtk.ListStore):

    def append(self, entry, iter=None):
        new_iter = self.insert_before(iter, entry)
        return new_iter

    def update(self, entry, iter):
        new_iter = self.append(entry, iter)
        self.remove(iter)
        return new_iter

    def save_settings(self):
        self.save.save(self)

class SaveListStoreBase(object):

    def __init__(self):
        self.save_file = os.path.join(CONFIG_HOME, self.SAVE_FILE)

    def load(self):
        if not self.has_save_file():
            return []

        with open(self.save_file, 'r') as f:
            entry = json.load(f)

        source_list = self._parse_entry(entry)
        return source_list

    def save_to_json(self, save_data):
        "for defaultsource.py"
        with open(self.save_file, mode='w') as f:
            json.dump(save_data, f)

    def has_save_file(self):
        "for defaultsource.py"
        return os.path.exists(self.save_file)
