from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.report import Report
from decimal import Decimal
from trytond.pyson import Equal, Eval
import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'RetenueType',
    'Retenue',
    'RetenueReport'
    ]

RETENUE_STATES = {
    'readonly': Equal(Eval('state'), 'open'),
}


class RetenueType(ModelSQL, ModelView):
    'RetenueType'
    __name__ = 'retenue_source.retenue.type'

    name = fields.Char('Name', required=False)
    short_name = fields.Char('Short Name', required=False)
    code = fields.Char('Code', required=False)
    active = fields.Boolean('Active')
    taux = fields.Numeric('Taux', digits=(16, 2))
    account = fields.Many2One(
        'account.account', 'Account', required=False, select=True)

    @classmethod
    def default_active(cls):
        return True

    @classmethod
    def default_taux(cls):
        return Decimal('0')


class Retenue(Workflow, ModelSQL, ModelView):
    'Retenue'
    __name__ = 'retenue_source.retenue'

    type = fields.Function(fields.Many2One('retenue_source.retenue.type', 'Type', states=RETENUE_STATES,
            required=True), 'on_change_with_type')
    journal = fields.Many2One(
        'account.journal', 'Journal', states=RETENUE_STATES, required=True)
    date = fields.Date('Date', states=RETENUE_STATES, required=True)
    party = fields.Many2One('party.party', 'Tiers', states=RETENUE_STATES,
            required=True)
    montant_brut = fields.Numeric('Montant Brut', digits=(16, 3), states=RETENUE_STATES,
            required=True)
    montant_retenue = fields.Function(fields.Numeric(
        'Montant Retenue', digits=(16, 3)), 'on_change_with_montant_retenue')
    montant_net = fields.Function(fields.Numeric('Montant Net', digits=(16, 3)),
     'on_change_with_montant_net')
    move = fields.Many2One('account.move', 'Mouvement',
                           ondelete='SET NULL', readonly=True)
    move_post_number = fields.Function(fields.Char(
        'Reference Mouvement'), 'get_move_post_number')

    state = fields.Selection([
        ('draft', 'Drafted'),
        ('open', 'Opened'),
        ('cancel', 'Canceled'),
        ('to_delete', 'Deleted')
        ], 'State', required=True, readonly=True)

    @classmethod
    def default_state(cls):
        return 'draft'

    @classmethod
    def default_date(cls):
        return datetime.date.today()

    @classmethod
    def default_journal(cls):
        retenues = cls.search([], order=[('id', 'DESC')], limit=1)
        journal_id = None
        if retenues and len(retenues) > 0:
            journal_id = retenues[0].journal.id
        return journal_id

    @classmethod
    def __setup__(cls):
        super(Retenue, cls).__setup__()
        cls._transitions |= set((
                ('draft', 'open'),
                ('open', 'cancel'),
                ('cancel', 'open'),
                ('cancel', 'to_delete'),
                ('draft', 'to_delete'),
                ))
        cls._buttons.update({
                'open': {
                    'invisible': Eval('state') != 'draft',
                    'depends': ['state'],
                    },
                'cancel': {
                    'invisible': Eval('state') != 'open',
                    'depends': ['state'],
                    },
                're_open': {
                    'invisible': Eval('state') != 'cancel',
                    'depends': ['state'],
                    },
                'to_delete': {
                    'invisible': (Eval('state') == 'open') | (Eval('state') == 'to_delete'),
                    'depends': ['state'],
                    },
                })
        cls._buttons.update({
                'create_move': {},
                })

    def get_move_post_number(self, name):
        move_post_number = '-pas de mvt-'
        if self.move:
            move_post_number = '-mvt non poste-'
            if self.move.post_number:
                move_post_number = self.move.post_number
        return move_post_number

    @fields.depends('montant_brut', 'type')
    def on_change_with_montant_retenue(self, name=None):
        if self.type and self.montant_brut:
            montant_retenue = self.type.taux * self.montant_brut / 100
        else:
            montant_retenue = 0
        return montant_retenue

    @fields.depends('montant_brut', 'type')
    def on_change_with_montant_net(self, name=None):
        if self.type and self.montant_brut:
            montant_net = self.montant_brut - self.type.taux * self.montant_brut / 100
        elif self.montant_brut and not self.type:
            montant_net = self.montant_brut
        else:
            montant_net = 0
        return montant_net

    @fields.depends('party')
    def on_change_with_type(self, name=None):
        type_id = None
        if self.party:
            type_id = self.party.retenue_type.id
        return type_id

    @classmethod
    def create_move(cls, retenue):
        Account = Pool().get('account.account')
        Move = Pool().get('account.move')
        Period = Pool().get('account.period')
        if retenue.move:
            return True
        libelle = 'RET SRC ' + retenue.party.name.upper()
        line1 = {
            'credit': retenue.montant_retenue,
            'account': retenue.type.account,
            }
        line2 = {
            'debit': retenue.montant_retenue,
            'account': retenue.party.account_payable.id,
            'party': retenue.party.id,
            }
        lines = ('create', [line1, line2])
        period_id = Period.find(Transaction().context.get('company'), date=retenue.date,
            exception=True)
        move = Move.create([{
                'number': libelle,
                'journal': retenue.journal.id,
                'period': period_id,
                'date': retenue.date,
                'lines': [lines]
                }])
        retenue.move = move[0].id
        Retenue.save([retenue])

    def delete_move(self, move):
        Move = Pool().get('account.move')
        Move.delete([move])

    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def open(cls, retenues):
        cls.create_move(retenues[0])
        return 'reload'

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, retenues):
        cls.delete_move(cls, retenues[0].move)
        return 'reload'

    @classmethod
    @ModelView.button
    @Workflow.transition('open')
    def re_open(cls, retenues):
        cls.create_move(retenues[0])
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('to_delete')
    def to_delete(cls, retenues):
        return 'delete'


class RetenueReport(Report):
    __name__ = 'retenue_source.retenue'

    @classmethod
    def get_company_address_formatted(cls, address):
        street = address.street or ''
        city = f' {address.city}' or ''
        subdivision = address.subdivision.name or ''
        postal_code = address.postal_code or ''
        address_formatted = f'{street} -{city} {subdivision} {postal_code}'
        return address_formatted.upper()

    @classmethod
    def get_context(cls, records, header, data):
        pool = Pool()
        Date = pool.get('ir.date')
        User = pool.get('res.user')
        user = User.browse([Transaction().user])
        context = super().get_context(records, header, data)
        payer_address = cls.get_company_address_formatted(
            user[0].company.party.addresses[0])
        beneficiary_address = cls.get_company_address_formatted(
            records[0].party.addresses[0])
        montant_brut = context['format_currency'](
            records[0].montant_brut, user[0].language, user[0].company.currency)
        montant_net = context['format_currency'](
            records[0].montant_net, user[0].language, user[0].company.currency)
        montant_retenue = context['format_currency'](
                records[0].montant_retenue, user[0].language, user[0].company.currency)
        context['report_data'] = {
            'payer_name': user[0].company.party.name,
            'payer_address': payer_address,
            'payer_vat_number': user[0].company.party.identifiers[0].code,
            'payer_code_tva': user[0].company.party.code_tva,
            'payer_code_categorie': user[0].company.party.code_categorie,
            'payer_etablissement': user[0].company.party.etablissement,
            'beneficiary_name': records[0].party.name,
            'beneficiary_address': beneficiary_address,
            'beneficiary_identifiant': records[0].party.code_tva or '',
            'beneficiary_vat_number': records[0].party.identifiers[0].code,
            'beneficiary_code_tva': records[0].party.code_tva,
            'beneficiary_code_categorie': records[0].party.code_categorie,
            'beneficiary_etablissement': records[0].party.etablissement,
            'retenue_type_short_name': records[0].type.short_name,
            'retenue_taux': context['format_number'](records[0].type.taux, user[0].language),
            'montant_brut': montant_brut,
            'montant_retenue': montant_retenue,
            'montant_net': montant_net,
            'date': context['format_date'](records[0].date, user[0].language)

        }
        context['retenue'] = context['record']
        context['today'] = Date.today()
        return context
