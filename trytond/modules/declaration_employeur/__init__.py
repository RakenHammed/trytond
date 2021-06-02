from trytond.pool import Pool
from . import declaration_employeur


def register():
    Pool.register(
        declaration_employeur.Annexe1Line,
        declaration_employeur.Annexe2Line,
        declaration_employeur.Annexe5Line,
        declaration_employeur.Annexe6Line,
        declaration_employeur.Declaration,
        module='declaration_employeur', type_='model'
        )

    Pool.register(
        declaration_employeur.DeclarationReport,
        module='declaration_employeur', type_='report'
        )

        
