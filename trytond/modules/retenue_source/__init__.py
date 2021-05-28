from trytond.pool import Pool
from . import retenue_source
from . import party


def register():
    Pool.register(
        retenue_source.RetenueType,
        retenue_source.Retenue,
        party.Party,
        module='retenue_source', type_='model'
        )

    Pool.register(
        retenue_source.RetenueReport,
        module='retenue_source',
        type_='report'
        )
