import sys, os
sys.path.append(os.path.abspath('.'))

import app.mongo_worker as mg


def assign_state(user_id, state):
    mg.update_one('users', 'tg_id', user_id, **{'state': state})


def select_user_attribute(user_id, attribute):
    return mg.select_one('users', attribute, **{'tg_id': int(user_id)})
