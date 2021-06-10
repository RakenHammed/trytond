from trytond.pool import Pool
from . import ouverture

def register():
    Pool.register(
        ouverture.Ouverture,
        module='ouverture', type_='model'
        )
