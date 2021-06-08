# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import bilan


def register():
    Pool.register(
        bilan.OpenBilanParameters,
        module='account_tn', type_='model')
    Pool.register(
        bilan.OpenBilan,
        module='account_tn', type_='wizard')
    Pool.register(
            bilan.Bilan,
            module='account_tn', type_='report')
