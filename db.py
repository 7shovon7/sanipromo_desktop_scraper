import json
import os
from typing import Any
from constants import DB_FILE

if not os.path.exists(DB_FILE):
    db_dir, _ = os.path.split(DB_FILE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    with open(DB_FILE, 'w') as f:
        f.write(json.dumps({}))


class DBAction:
    def __init__(self):
        self.data = None

    def read_all_data(self):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                self.data = data
        except Exception as e:
            print("Reading data from database failed!")
            print(e)
        return self.data
    
    def update_db(self):
        try:
            if self.data is not None:
                with open(DB_FILE, 'w') as f:
                    f.write(json.dumps(self.data, indent=4))
                    return True
            else:
                print('Can not save empty data!')
        except Exception as e:
            print("Writing data in database failed!")
            print(e)
        return False
    
    def save_data(self, key: str, value: Any):
        if self.data is None:
            self.data = self.read_all_data()
        self.data[key] = value
        self.update_db()

    def get_data(self, key: str):
        if self.data is None:
            self.data = self.read_all_data()
        return self.data.get(key)
    

DB_ACTION = DBAction()
