# encoding: utf-8
"""
Tools to work with DVM paramater list.
"""

from __future__ import absolute_import

from collections import namedtuple

import json

from pydicti import dicti
from madqt.core import unit
from .util import csv_unicode_reader


DVM_Parameter = namedtuple('DVM_Parameter', [
    'name',
    'ui_name',
    'ui_hint',
    'ui_prec',
    'unit',
    'ui_unit',
    'ui_conv',
    'example',
])


#----------------------------------------
# CSV column types
#----------------------------------------

def CsvStr(s):
    return s


def CsvBool(s):
    return s == 'ja' if s else None


def CsvInt(s):
    return int(s) if s else None


def CsvFloat(s):
    return float(s) if s else None


def CsvUnit(s):
    if s == '%':
        return 0.01
    s = s.replace(u'grad', u'degree')
    s = s.replace(u'Ohm', u'ohm')
    s = s.replace(u'part.', u'count')   # used for particle count
    return unit.from_config(s)


def load_csv(filename, encoding='utf-8', delimiter=';'):
    """
    Parse DVM parameters from CSV file exported from XLS documentation
    spreadsheet (e.g. DVM-Parameter_v2.10.0-10-HIT.xls)
    """
    csv_data = csv_unicode_reader(filename,
                                  encoding=encoding,
                                  delimiter=delimiter)
    return load_csv_data(csv_data)


def load_csv_data(rows):
    return dicti(_parse_csv_data(rows))


def _parse_csv_data(rows):
    parse_row = lambda row: DVM_Parameter(**{
        n: _csv_column_types[n](row[i].strip())
        for n, i in _csv_column_index.items()
    })
    cluster_name = ''
    cluster_items = []
    for row in rows:
        item = parse_row(row)
        # detect cluster header lines:
        link = row[0]
        if link and not link.isdigit() and not item.name:
            # yield previous element/context
            if cluster_items:
                yield (cluster_name, cluster_items)
            cluster_name = link
            cluster_items = []
        elif item.name:
            cluster_items.append(item)
    if cluster_items:
        yield (cluster_name, cluster_items)

# all columns in csv file:
_csv_column_names = [
    '',                 # Nr. für Link
    'name',             # Code Param (GSI-Nomenklatur)
    '',                 # Code Gerät (GSI- NomenkLatur) entspr. DCU!
    '',                 # Code Gruppe (=Kalkulationsgruppe); möglichst GSI-NomenkLatur
    'ui_name',          # GUI Beschriftung Parameter (ohne Einheit)
    'ui_hint',          # GUI Beschriftung Hint
    '',                 # Position ExpertGrids
    '',                 # DVM liest Parameter
    '',                 # DVM ändert Parameter
    '',                 # DVM Datensatz spezifisch
    '',                 # Rein temporär
    '',                 # MEFI-Abhängigkeit
    '',                 # Input Param wird Output Param bei MEFI
    '',                 # In Gui Init änderbar
    '',                 # Daten-typ
    'ui_prec',          # Präzision (Anz. Nachkomma im GUI)
    'unit',             # Einheit Parameter
    'ui_unit',          # Einheit Anzeige im GUI
    'ui_conv',          # Umrechnungsfaktor Einheit--> Einheit GUI
    'example',          # Beispielwert für Test in Einheit GUI
    '',                 # Referenz auf DCU /MDE
    '',                 # (nicht verwendet)
    '',                 # Zugriffscode / editierbarkeit
    '',                 # Versions-  Relevanz
    '',                 # Detail Ansicht verfügbar (ja/nein)
    '',                 # Link auf Maximalwert
    '',                 # Link auf Minimalwert
    '',                 # Code Min/Max- Rechen-vorschrift
    '',                 # Master-gruppe
    '',                 # Defaultwert Änderung pro Pfeiltasten-druck/Maus-radsegment in Einheit GUI
    '',                 # Im laufenden Betrieb änderbar (ja/ nein)
    '',                 # Link auf zugehörigen sekundären Wert
]

_csv_column_types = {
    'name': CsvStr,
    'ui_name': CsvStr,
    'ui_hint': CsvStr,
    'ui_prec': CsvInt,
    'unit': CsvUnit,
    'ui_unit': CsvUnit,
    'ui_conv': CsvFloat,
    'example': CsvFloat,
}

# inverse map of _csv_columns[i] (used columns)
_csv_column_index = {
    name: index
    for index, name in enumerate(_csv_column_names)
    if name
}
