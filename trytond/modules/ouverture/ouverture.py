from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.pyson import Eval
import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'Ouverture',
    ]

class Ouverture(Workflow, ModelSQL, ModelView):
    'Ouverture'
    __name__ = 'ouverture.ouverture'

    annee1 = fields.Many2One('account.fiscalyear', 'Année Clôture', required=True)
    annee2 = fields.Many2One('account.fiscalyear', 'Année Ouverture', required=True)
    journal = fields.Many2One('account.journal', 'Journal Ouverture', required=True)
    period = fields.Many2One('account.period', 'Period', required=True)
    date = fields.Date('Date', required=True)
    move = fields.Many2One('account.move', 'Move', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Opened'),
        ], 'State', required=True, readonly=True)

    @classmethod
    def default_annee2(cls):
        pool = Pool()
        Fiscalyear = pool.get('account.fiscalyear')
        return Fiscalyear.find(Transaction().context.get('company') or False,
                exception=False)

    @classmethod
    def default_state(cls):
        return 'draft'

    @classmethod
    def default_date(cls):
        return datetime.date.today()

    @classmethod
    def __setup__(cls):
        super(Ouverture, cls).__setup__()
        cls._transitions |= set((
                ('draft', 'open'),
                ('open', 'cancel'),
                ))
        cls._buttons.update({
                'open': {
                    'invisible': Eval('state') == 'draft',
                    'depends': ['state'],
                    },
                'draft': {
                    'invisible': Eval('state') == 'open',
                    'depends': ['state'],
                    },
                })

    def create_move(self, ouverture):
        pool = Pool()
        Fiscalyear = pool.get('account.fiscalyear')
        Account = pool.get('account.account')
        Currency = pool.get('currency.currency')
        Move = pool.get('account.move')
        Period = pool.get('account.period')   
        
        fiscalyear1 = Fiscalyear.browse([ouverture.annee1.id])
        fiscalyear2 = Fiscalyear.browse([ouverture.annee2.id])
        libelle = 'OUVERTURE ' + fiscalyear2.name
        
        accounts = Account.search([
            ('company', '=', ouverture.annee1.company.id),
            ('code', 'not like', '6%'),
            ('code', 'not like', '7%')
            ])
        accounts_ids = [account.id for account in accounts]
        with Transaction().set_context(fiscalyear=fiscalyear1):
            accounts = Account.browse(accounts_ids)
        
        move_lines = []
       
        for account in accounts:
            if not (Currency.is_zero(fiscalyear1.company.currency,
                    account.debit) and Currency.is_zero(fiscalyear1.company.currency,
                    account.credit)):
                        debit = account.debit
                        credit = account.credit
                        if debit < credit:
                            solde = credit-debit
                            line = {'name': libelle, 'credit': solde, 'account': account}
                            move_lines.append(line)
                        elif credit < debit:
                            solde = debit-credit
                            line = {'name': libelle, 'debit': solde, 'account': account}
                            move_lines.append(line)
          
        move = Move.create({
            'name': libelle,
            'journal': ouverture.journal.id,
            'period': ouverture.period.id,
            'date': ouverture.date,
            'lines': [('create', x) for x in move_lines],
            })[0]
        self.write(ouverture, {
            'move': move.id,
            })

        return move.id

    def delete_move(self, move):
        Move = Pool().get('account.move')
        Move.delete([move])
    
    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def open(cls, ouvertures):
        cls.create_move(ouvertures[0])
        return 'reload'

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, ouvertures):
        cls.delete_move(cls, ouvertures[0].move)
        return 'reload'
