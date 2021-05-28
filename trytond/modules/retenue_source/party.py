from trytond.model import ModelSQL, ModelView, fields, Workflow
from decimal import Decimal
from trytond.pyson import Equal, Eval
import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.rpc import RPC
import json

__all__ = [
    'Party'
    ]

class Party(ModelSQL, ModelView):
    'Party'
    __name__ = 'party.party'
    code_tva = fields.Char('Code TVA', size=1)
    code_categorie = fields.Char('Code Categorie', size=1)
    etablissement = fields.Char('Etablissement Secondaire', size=3)
    retenue_type = fields.Many2One('retenue_source.retenue.type', 'Type de Retenue par defaut')
    nature_identifiant = fields.Selection([
        ('mf', 'Matricule fiscal'),
        ('cin', 'Carte d\'identité'),
        ('carte de sejour', 'Carte de séjour'),
        ('ni domoicilie ni etabli', 'Ni domoicilié ni établi'),
        ], 'Nature identifiant', required=True)
    identifiant = fields.Char('Identifiant', size=8,
            help='carte d\'identité ou carte de séjour',
            states={'invisible': Equal(Eval('nature_identifiant'), 'mf')},
            depends=['nature_identifiant'])
    activite = fields.Char('Activite', size=40)

    @classmethod
    def default_nature_identifiant(cls):
        return 'mf'