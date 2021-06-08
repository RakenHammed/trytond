# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


from trytond.report import Report
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Button, StateAction, StateTransition, StateView, Wizard
from trytond.model import ModelView, fields


class OpenBilan(Wizard):
    'Open Bilan'
    __name__ = 'bilan.open_bilan'

    start = StateView('bilan.open_bilan.parameters',
        'account_tn.open_bilan_parameters_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'open_bilan', 'tryton-ok', default=True),
            ])
    open_bilan = StateAction('account_tn.open_bilan_report')

    def do_open_bilan(self, action):
        return action, {
            'fiscalyear_id': self.start.fiscalyear.id,
            'start_period_id': self.start.start_period.id,
            'end_period_id': self.start.end_period.id,
            'posted': self.start.posted,
        }


class OpenBilanParameters(ModelView):
    'Open Bilan Parameters'
    __name__ = 'bilan.open_bilan.parameters'

    fiscalyear = fields.Many2One('account.fiscalyear', 'Annee', required=True)
    start_period = fields.Many2One('account.period', 'Periode Debut',
            domain=[
                ('fiscalyear', '=', Eval('fiscalyear')),
                ('start_date', '<=', (Eval('end_period'), 'start_date'))
            ],
            depends=['end_period'])
    end_period = fields.Many2One('account.period', 'Periode Fin',
            domain=[
                ('fiscalyear', '=', Eval('fiscalyear')),
                ('start_date', '>=', (Eval('start_period'), 'start_date'))
            ],
            depends=['start_period'])
    posted = fields.Boolean('Mouvements postes uniquement',
                            help='Show only posted move')


class Bilan(Report):
    __name__ = 'bilan.bilan'

    @classmethod
    def get_period_ids(cls, fiscalyear, data):
        pool = Pool()
        Period = pool.get('account.period')

        start_period_ids = []
        if data['start_period_id']:
            start_period = Period.browse([data['start_period_id']])[0]
            start_period_ids = Period.search([
                ('fiscalyear', '=', fiscalyear.id),
                ('end_date', '<=', start_period.start_date),
                ])

        end_period_ids = []
        if data['end_period_id']:
            end_period = Period.browse([data['end_period_id']])[0]
            end_period_ids = Period.search([
                ('fiscalyear', '=', fiscalyear.id),
                ('end_date', '<=', end_period.start_date),
                ])
            end_period_ids = list(set(end_period_ids).difference(
                set(start_period_ids)))
            if data['end_period_id'] not in end_period_ids:
                end_period_ids.append(data['end_period_id'])
        else:
            end_period_ids = Period.search([
                ('fiscalyear', '=', fiscalyear.id),
                ])
            end_period_ids = list(set(end_period_ids).difference(
                set(start_period_ids)))
        return end_period_ids

    @classmethod
    def execute(cls, ids, data):
        pool = Pool()
        Account = pool.get('account.account')
        FiscalYear = pool.get('account.fiscalyear')
        fiscalyear = FiscalYear.browse([data['fiscalyear_id']])[0]
        User = pool.get('res.user')
        user = User.browse([Transaction().user])[0]
        period_ids = cls.get_period_ids(fiscalyear, data)
        with Transaction().set_context(
                posted = data['posted'],
                fiscalyear=fiscalyear,
                periods=period_ids,
                ):
            accounts = Account.search([
                ('company', '=', user.company.id),
                ])

        account_ids = [account.id for account in accounts]
        data = {
                'model': 'account.account',
                'model_context': None,
                'id': account_ids[0],
                'ids': account_ids,
                'paths': None,
                'action_id': data['action_id'],
                'fiscalyear_id': data['fiscalyear_id'],
                'start_period_id': data['start_period_id'],
                'end_period_id': data['end_period_id'],
                'posted': data['posted'],
                }
        return super(Bilan, cls).execute(account_ids, data)

    @classmethod
    def get_context(cls, records, header, data):
        pool = Pool()
        Period = pool.get('account.period')
        User = pool.get('res.user')
        context = super().get_context(records, header, data)
        user = User.browse([Transaction().user])[0]

        accounts = records
        actif = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        passif = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        cdr = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for account in accounts:
            solde = account.debit - account.credit
            if account.code and solde != 0:
                if account.code[:3] in ['210', '211', '212', '213', '214', '215', '216', '217', '218', '219', '231', '237']:
                    actif[1] += solde
                elif account.code[:3] in ['281', '291']:
                    actif[2] += solde
                elif account.code[:3] in ['220', '221', '222', '223', '224', '225', '226', '227', '228', '229', '232', '238', '240', '241', '242', '243', '244', '245', '246', '247', '248', '249']:
                    actif[3] += solde
                elif account.code[:3] in ['282', '283', '284', '292', '293', '294']:
                    actif[4] += solde
                elif account.code[:2] in ['25', '26']:
                    actif[5] += solde
                elif account.code[:3] in ['295', '296']:
                    actif[6] += solde
                elif account.code[:2] in ['27']:
                    actif[7] += solde
                elif account.code[:2] in ['30', '31', '32', '33', '34', '35', '37']:
                    actif[8] += solde
                elif account.code[:2] in ['39']:
                    actif[9] += solde
                elif account.code[:2] in ['41']:
                    if solde > 0:
                        actif[10] += solde
                    else:
                        passif[10] += solde
                elif account.code[:2] in ['49']:
                    actif[11] += solde
                elif account.code[:3] in ['421', '434', '436', '471'] or account.code[:2] in ['44']:
                    if solde > 0:
                        actif[12] += solde
                    else:
                        passif[10] += solde
                elif account.code[:2] in ['50', '51', '52', '58']:
                    if solde > 0:
                        actif[13] += solde
                    else:
                        passif[11] += solde
                elif account.code[:2] in ['53', '54', '55', '59']:
                    if solde > 0:
                        actif[14] += solde
                    else:
                        passif[11] += solde
                elif account.code[:2] in ['10']:
                    passif[1] += solde
                elif account.code[:2] in ['11'] or account.code[:3] in ['142', '143', '144']:
                    passif[2] += solde
                elif account.code[:3] in ['141', '145']:
                    passif[3] += solde
                elif account.code[:2] in ['12', '13']:
                    passif[4] += solde
                elif account.code[:3] in ['161', '162', '163', '164', '164', '165']:
                    passif[6] += solde
                elif account.code[:3] in ['167', '168'] or account.code[:2] in ['18']:
                    passif[7] += solde
                elif account.code[:2] in ['15']:
                    passif[8] += solde
                elif account.code[:2] in ['40']:
                    if solde < 0:
                        passif[9] += solde
                    else:
                        actif[12] += solde
                elif account.code[:2] in ['17', '42', '43', '44', '45', '46', '47', '48']:
                    if solde < 0:
                        passif[10] += solde
                    else:
                        actif[12] += solde
                elif account.code[:2] in ['70']:
                    cdr[1] += solde
                elif account.code[:2] in ['72']:
                    cdr[2] += solde
                elif account.code[:2] in ['71']:
                    cdr[3] += solde
                elif account.code[:3] in ['603']:
                    cdr[4] += solde
                elif account.code[:3] in ['607']:
                    cdr[5] += solde
                elif account.code[:2] in ['60']:
                    cdr[6] += solde
                elif account.code[:2] in ['64']:
                    cdr[7] += solde
                elif account.code[:2] in ['68'] or account.code[:3] in ['780', '781']:
                    cdr[8] += solde
                elif account.code[:2] in ['61', '62', '66']:
                    cdr[9] += solde
                elif account.code[:2] in ['65'] or account.code[:3] in ['686']:
                    cdr[10] += solde
                elif account.code[:2] in ['75']:
                    cdr[11] += solde
                elif account.code[:2] in ['73', '74']:
                    cdr[12] += solde
                elif account.code[:2] in ['63']:
                    cdr[13] += solde
                elif account.code[:2] in ['69']:
                    cdr[14] += solde
                elif account.code[:2] in ['67', '77']:
                    cdr[15] += solde
                else:
                    cdr[16] += solde
        for i in range(1, 17):
            context['actif' + str(i)] = actif[i]
            context['passif' + str(i)] = passif[i]
            context['cdr' + str(i)] = cdr[i]
        return context
