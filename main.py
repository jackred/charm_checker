from flask import Flask
from flask import request

import pandas as pd
import numpy as np
import difflib


def clean(series):
    return np.array(series[np.logical_not(np.array([series.isna(),
                                                    series.str.isspace()])
                                          .any(0))].str.lower()
                    .apply(lambda x: x.strip()))


table = pd.read_csv('./data/proper - Table.csv')
table = table.drop(0)
c = list(range(0, len(table.iloc[0]), 7))
r = list(range(4, len(table.iloc[0]), 7))
s = list(range(5, len(table.iloc[0]), 7))
name = table.columns[c]
tables = table[table.columns[r]]
tables = np.array([clean(tables[i]) for i in tables], dtype=object)
slots = table[table.columns[s]]
slots = slots.apply(lambda x: x.apply(
    lambda y: y.replace('-0', '').strip()
    if isinstance(y, str) else y)).to_numpy().transpose()
slots = np.array([slots[i][:len(tables[i])] for i in range(len(tables))],
                 dtype=object)



app = Flask(__name__)



@app.route('/')
def catch_all():
    return 'nothing to see here'


@app.route('/sequence', methods=['POST'])
def sequence():
    content = request.get_json()
    print(content['charm'])
    charms = np.array([i.strip().lower()
                       for i in content['charm'].split('|')])
    mbs = [difflib.SequenceMatcher(None, charms, t).get_matching_blocks()
           for t in tables]
    res = '\n'.join(['{} charm(s) in common with table `{}`'.format(
        sum([mbs[i][j].size
             for j in range(len(mbs[i]))]),  name[i])
                     for i in range(len(tables))])
    return res


@app.route('/charm', methods=['POST'])
def charm():
    content = request.get_json()
    print(content)
    charm = content['charm'].strip().lower()
    is_in = [t == charm for t in tables]
    is_in_any = [i.any() for i in is_in]
    if sum(is_in_any) > 0:
        slot = content['slot'].strip().replace('-0', '')
        compare = [slots[i][is_in[i]] for i in range(len(slots))]
        is_in_slot = [t == slot for t in compare]
        is_in_slot_any = [i.any() for i in is_in_slot]
        if sum(is_in_slot_any) > 0:
            name_table = name[is_in_slot_any]
            return 'Charm+slot in table{} `{}`'.format(
                    's' if len(name_table) > 1 else '', ', '.join(name_table))
        else:
            name_table = name[is_in_any]
            return "Slot doesn't match any charm. Charm without slot (in" \
                " case of error) in table{} `{}`".format(
                    's' if len(name_table) > 1 else '', ', '.join(name_table))
    else:
        return 'charm in 0 table'
