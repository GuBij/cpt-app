from collections import namedtuple

QUANTITIES: tuple[str,str,str] = ('depth','qc','fs')
COLORS: dict[str,str] = dict(zip(QUANTITIES, ('silver','lime','red'), strict = True))
UNITS: dict[str, str] = dict(zip(QUANTITIES, ('m','MPa','kPa'), strict = True))
Measurement = namedtuple('Measurement', QUANTITIES)
