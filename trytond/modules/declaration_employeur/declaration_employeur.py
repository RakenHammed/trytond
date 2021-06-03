from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.report import Report
from decimal import Decimal
from trytond.pyson import Equal, Eval
import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.wizard import Wizard, Button, StateAction, StateTransition, StateView
from trytond.exceptions import UserError
import time

__all__ = [
    'Annexe1Line',
    'Annexe2Line',
    'Annexe5Line',
    'Annexe6Line',
    'Declaration',
    'DeclarationReport',
    ]


class Declaration(ModelSQL, ModelView):
    'Declaration'
    __name__ = 'declaration_employeur.declaration'

    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
            required=True)
    annexe1_lines = fields.One2Many(
        'declaration_employeur.annexe1.line', 'declaration', 'Lignes annexe 1')
    annexe2_lines = fields.One2Many(
        'declaration_employeur.annexe2.line', 'declaration', 'Lignes annexe 2')
    annexe5_lines = fields.One2Many(
        'declaration_employeur.annexe5.line', 'declaration', 'Lignes annexe 5')
    annexe6_lines = fields.One2Many(
        'declaration_employeur.annexe6.line', 'declaration', 'Lignes annexe 6')
    code_acte = fields.Selection([
        ('0', '0- Spontané'),
        ('1', '1- Régularisation'),
        ('2', '2- Redressement'),
        ], 'Code Acte', required=True)
    description = fields.Char('Description', size=None)
    presence_anx1 = fields.Boolean('Annexe 1')
    presence_anx2 = fields.Boolean('Annexe 2')
    presence_anx3 = fields.Boolean('Annexe 3')
    presence_anx4 = fields.Boolean('Annexe 4')
    presence_anx5 = fields.Boolean('Annexe 5')
    presence_anx6 = fields.Boolean('Annexe 6')
    presence_anx7 = fields.Boolean('Annexe 7')
    assiette_010 = fields.Numeric('1- Traitements, Salaires, Pensions'
            + ' et Rentes Viageres Regime Commun', digits=(16, 3))
    retenue_010 = fields.Numeric('Retenue Traitements, Salaires, Pensions'
            + ' et Rentes Viageres Regime Commun', digits=(16, 3))
    assiette_170 = fields.Numeric('2- Traitements, Salaires, Pensions'
            + ' et Rentes Viageres Taux 20', digits=(16, 3))
    retenue_170 = fields.Numeric('Retenue Traitements, Salaires, Pensions'
            + ' et Rentes Viageres Taux 20', digits=(16, 3))
    retenue_300 = fields.Numeric('Contribution de solidarité', digits=(16, 3))
    retenue_400 = fields.Numeric('Contribution 2020', digits=(16, 3))
    assiette_021 = fields.Numeric('3a- honoraires, commissions, courtages,'
            + 'loyers et remunerations au titre des activites non commerciales,'
            + 'servis aux P etablies et domiciliees', digits=(16, 3))
    retenue_021 = fields.Numeric(
        'Retenue Honoraires P etablies', digits=(16, 3))
    assiette_023 = fields.Numeric('3b- honoraires, commissions, courtages,'
            + 'loyers et remunerations au titre des activites non commerciales,'
            + 'servis aux P non etablies et non domiciliees', digits=(16, 3))
    retenue_023 = fields.Numeric(
        'Retenue Honoraires P non etablies', digits=(16, 3))
    assiette_025 = fields.Numeric('3c- honoraires, commissions, courtages,'
            + 'et remunerations au titre des activites non commerciales,'
            + 'provenant des exportations', digits=(16, 3))
    retenue_025 = fields.Numeric(
        'Retenue Honoraires exportations', digits=(16, 3))
    assiette_030 = fields.Numeric('4-  Honoraires payes aux P.M '
            + 'et aux P.P soumises au Regime Reel et remunerations artistes', digits=(16, 3))
    retenue_030 = fields.Numeric(
        'Retenue Honoraires Regime Reel', digits=(16, 3))
    assiette_180 = fields.Numeric('5- Honoraires bureaux detudes'
            + ' exportateurs', digits=(16, 3))
    retenue_180 = fields.Numeric('Retenue Honoraires bureaux detudes'
            + ' exportateurs', digits=(16, 3))
    assiette_040 = fields.Numeric('6- Loyers des Hotels', digits=(16, 3))
    retenue_040 = fields.Numeric('Retenue Loyers Hotels', digits=(16, 3))
    assiette_260 = fields.Numeric(
        'x- Contrepartie de la performance', digits=(16, 3))
    retenue_260 = fields.Numeric(
        'Retenue Contrepartie de la performance', digits=(16, 3))
    assiette_060 = fields.Numeric('7- Interets des comptes speciaux '
            + 'epargne ouverts aupres des banques et de la CENT', digits=(16, 3))
    retenue_060 = fields.Numeric(
        'Retenue Interets cptes speciaux', digits=(16, 3))
    assiette_071 = fields.Numeric('8a- Revenus des autres capitaux '
            + 'mobiliers servis aux residents', digits=(16, 3))
    retenue_071 = fields.Numeric(
        'Retenue Autres capitaux mobiliers residents', digits=(16, 3))
    assiette_073 = fields.Numeric('8b- Revenus des autres capitaux '
            + 'mobiliers revenant aux non residents', digits=(16, 3))
    retenue_073 = fields.Numeric(
        'Retenue Autres capitaux mobiliers non residents', digits=(16, 3))
    assiette_080 = fields.Numeric('9- Valeurs Mobilieres revenant aux'
            + ' non residents', digits=(16, 3))
    retenue_080 = fields.Numeric(
        'Retenue Valeurs Mobilieres non residents', digits=(16, 3))
    assiette_241 = fields.Numeric('10a- Actions et Parts Sociales servies'
            + ' aux PP residentes', digits=(16, 3))
    retenue_241 = fields.Numeric('Actions residents', digits=(16, 3))
    assiette_242 = fields.Numeric('10b- Actions et Parts Sociales servies'
            + ' aux PP et PM non residentes', digits=(16, 3))
    retenue_242 = fields.Numeric('Actions non residents', digits=(16, 3))
    assiette_091 = fields.Numeric('11a- Jetons de presence payes a des'
            + ' residents', digits=(16, 3))
    retenue_091 = fields.Numeric(
        'Retenue Jetons de presence residents', digits=(16, 3))
    assiette_093 = fields.Numeric('11b- Jetons de presence payes a des'
            + ' non residents', digits=(16, 3))
    retenue_093 = fields.Numeric(
        'Retenue Jetons de presence non residents', digits=(16, 3))
    assiette_100 = fields.Numeric('12- Remunerations payees aux salaries'
            + ' et aux non salaries en contrepartie dun travail occasionnel'
            + ' ou accidentel en dehors de leur activite principale', digits=(16, 3))
    retenue_100 = fields.Numeric('Retenue Travail Occasionnel', digits=(16, 3))
    assiette_110 = fields.Numeric('13- Interets des prets payes aux '
            + 'etablissements bancaires non etablis en Tunisie', digits=(16, 3))
    retenue_110 = fields.Numeric(
        'Retenue Interets banques non etablies', digits=(16, 3))
    assiette_121 = fields.Numeric('14a- prix de cession declare dans lacte '
            + '(Plus-Value Immobiliere) pour les residents', digits=(16, 3))
    retenue_121 = fields.Numeric(
        'Retenue Plus-Value Immobiliere residents', digits=(16, 3))
    assiette_122 = fields.Numeric('14b1- prix de cession declare dans lacte '
            + '(Plus-Value Immobiliere) pour les non residents', digits=(16, 3))
    retenue_122 = fields.Numeric(
        'Retenue Plus-Value Immobiliere non residents', digits=(16, 3))
    assiette_123 = fields.Numeric('14b2- prix de cession declare dans lacte '
            + '(Plus-Value Immobiliere) pour les PM non etablies au titre des biens fonciers uniquement', digits=(16, 3))
    retenue_123 = fields.Numeric(
        'Retenue Plus-Value Immobiliere PM non etablies biens fonciers', digits=(16, 3))
    assiette_131 = fields.Numeric('15a- Montants depassant 1000 D TTC, '
            + 'provenant des operations d export et des operations de ventes '
            + 'des operations de vente des PM soumises a IS10', digits=(16, 3))
    retenue_131 = fields.Numeric(
        'Montants depassant 1000 D TTC export ou IS10', digits=(16, 3))
    assiette_132 = fields.Numeric('15b- Montants depassant 1000 D TTC, '
            + 'provenant des autres operations', digits=(16, 3))
    retenue_132 = fields.Numeric(
        'Autres montants depassant 1000 D TTC', digits=(16, 3))
    assiette_140 = fields.Numeric('16- TVA au titre des montants depassant '
            + '1000 D TTC, payes par les services de letat, les collectivites '
            + 'locales et les entreprises et les etablissements publics', digits=(16, 3))
    retenue_140 = fields.Numeric(
        'Retenue TVA etablissements publics', digits=(16, 3))
    assiette_150 = fields.Numeric('17- TVA au titre des '
            + 'operations effectuees avec des personnes qui nont pas '
            + 'detablissement en Tunisie', digits=(16, 3))
    retenue_150 = fields.Numeric('Retenue TVA non etablis', digits=(16, 3))
    assiette_160 = fields.Numeric('18- Remunerations aux non residents '
            + 'qui effectuent des services et travaux dont '
            + 'la periode ne depasse pas 6 mois', digits=(16, 3))
    retenue_160 = fields.Numeric(
        'Retenue non residents 6 mois', digits=(16, 3))
    assiette_270 = fields.Numeric('xx- Montants servis aux non residents etablis '
            + 'et qui ne procedent pas au depot de la declaration d’existence '
            + 'avant d entamer leur activite CAT1', digits=(16, 3))
    retenue_270 = fields.Numeric(
        'Retenue montants servis aux non residents etablis CAT1', digits=(16, 3))
    assiette_271 = fields.Numeric('xx- Montants servis aux non residents etablis '
            + 'et qui ne procedent pas au depot de la declaration d’existence '
            + 'avant d entamer leur activite CAT2', digits=(16, 3))
    retenue_271 = fields.Numeric(
        'Retenue montants servis aux non residents etablis CAT2', digits=(16, 3))
    assiette_200 = fields.Numeric('19- Avances sur les ventes des entreprises '
            + 'aux P.P soumises au regime forfaitaire', digits=(16, 3))
    retenue_200 = fields.Numeric(
        'Avance sur ventes aux P.P regime forfaitaire', digits=(16, 3))
    assiette_191 = fields.Numeric('20a- plus valus de cession etablies'
            + ' par les P.P non etablies et non residentes', digits=(16, 3))
    retenue_191 = fields.Numeric(
        'Retenue plus valus PP non etablies', digits=(16, 3))
    assiette_192 = fields.Numeric('20b- plus valus de cession etablies'
            + ' par les P.M non etablies et non residentes', digits=(16, 3))
    retenue_192 = fields.Numeric(
        'Retenue plus valus PM non etablies', digits=(16, 3))
    assiette_051 = fields.Numeric('21- autres revenus servis'
            + ' a des personnes non etablies et non domiciliees', digits=(16, 3))
    retenue_051 = fields.Numeric(
        'Autres revenus P non etablies', digits=(16, 3))
    # 210 is not used since 2016
    assiette_210 = fields.Numeric('22- Subvention de la caisse generale '
            + 'de conpensation', digits=(16, 3))
    retenue_210 = fields.Numeric(
        'Subvention caisse de conpensation', digits=(16, 3))
    assiette_220 = fields.Numeric('23- Remunerations ou revenus servis a '
            + 'des personnes etablies dans des paradis fiscaux', digits=(16, 3))
    retenue_220 = fields.Numeric('Paradis fiscaux', digits=(16, 3))
    assiette_250 = fields.Numeric('24- Commissions des distributeurs agrees '
            + 'des operateurs telephoniques', digits=(16, 3))
    retenue_250 = fields.Numeric(
        'Commissions distributeurs telephoniques', digits=(16, 3))
    assiette_280 = fields.Numeric('xx- Revenus jeux de hasard', digits=(16, 3))
    retenue_280 = fields.Numeric('Retenues jeux de hasard', digits=(16, 3))
    assiette_290 = fields.Numeric(
        'xx- Ventes distribution 20md', digits=(16, 3))
    retenue_290 = fields.Numeric('Ventes distribution 20md', digits=(16, 3))
    assiettes_total = fields.Function(fields.Numeric('assiette totale', digits=(16, 3)),
            'get_assiettes_total', 'set_assiettes_total')
    retenues_total = fields.Function(fields.Numeric('retenue', digits=(16, 3)),
            'get_retenues_total', 'set_retenues_total')
    
    @classmethod
    def __setup__(cls):
        super(Declaration, cls).__setup__()
        cls._order.insert(0, ('description', 'DESC'))

    @classmethod
    def default_description(cls):
        return time.strftime('%d-%m-%Y %H:%M', time.localtime())
    
    @classmethod
    def default_assiette_010(cls):
        return 0

    @classmethod
    def default_retenue_010(cls):
        return 0

    @classmethod
    def default_assiette_170(cls):
        return 0

    @classmethod
    def default_retenue_170(cls):
        return 0

    @classmethod
    def default_assiette_021(cls):
        return 0

    @classmethod
    def default_retenue_021(cls):
        return 0

    @classmethod
    def default_assiette_023(cls):
        return 0

    @classmethod
    def default_retenue_023(cls):
        return 0

    @classmethod
    def default_assiette_025(cls):
        return 0

    @classmethod
    def default_retenue_025(cls):
        return 0

    @classmethod
    def default_assiette_030(cls):
        return 0

    @classmethod
    def default_retenue_030(cls):
        return 0

    @classmethod
    def default_assiette_180(cls):
        return 0

    @classmethod
    def default_retenue_180(cls):
        return 0

    @classmethod
    def default_assiette_040(cls):
        return 0

    @classmethod
    def default_retenue_040(cls):
        return 0

    @classmethod
    def default_assiette_260(cls):
        return 0

    @classmethod
    def default_retenue_260(cls):
        return 0

    @classmethod
    def default_assiette_060(cls):
        return 0

    @classmethod
    def default_retenue_060(cls):
        return 0

    @classmethod
    def default_assiette_071(cls):
        return 0

    @classmethod
    def default_retenue_071(cls):
        return 0

    @classmethod
    def default_assiette_073(cls):
        return 0

    @classmethod
    def default_retenue_073(cls):
        return 0

    @classmethod
    def default_assiette_080(cls):
        return 0

    @classmethod
    def default_retenue_080(cls):
        return 0

    @classmethod
    def default_assiette_241(cls):
        return 0

    @classmethod
    def default_retenue_241(cls):
        return 0

    @classmethod
    def default_assiette_242(cls):
        return 0

    @classmethod
    def default_retenue_242(cls):
        return 0

    @classmethod
    def default_assiette_091(cls):
        return 0

    @classmethod
    def default_retenue_091(cls):
        return 0

    @classmethod
    def default_assiette_093(cls):
        return 0

    @classmethod
    def default_retenue_093(cls):
        return 0

    @classmethod
    def default_assiette_100(cls):
        return 0

    @classmethod
    def default_retenue_100(cls):
        return 0

    @classmethod
    def default_assiette_110(cls):
        return 0

    @classmethod
    def default_retenue_110(cls):
        return 0

    @classmethod
    def default_assiette_121(cls):
        return 0

    @classmethod
    def default_retenue_121(cls):
        return 0

    @classmethod
    def default_assiette_122(cls):
        return 0

    @classmethod
    def default_retenue_122(cls):
        return 0

    @classmethod
    def default_assiette_123(cls):
        return 0

    @classmethod
    def default_retenue_123(cls):
        return 0

    @classmethod
    def default_assiette_131(cls):
        return 0

    @classmethod
    def default_retenue_131(cls):
        return 0

    @classmethod
    def default_assiette_132(cls):
        return 0

    @classmethod
    def default_retenue_132(cls):
        return 0

    @classmethod
    def default_assiette_140(cls):
        return 0

    @classmethod
    def default_retenue_140(cls):
        return 0

    @classmethod
    def default_assiette_150(cls):
        return 0

    @classmethod
    def default_retenue_150(cls):
        return 0

    @classmethod
    def default_assiette_160(cls):
        return 0

    @classmethod
    def default_retenue_160(cls):
        return 0

    @classmethod
    def default_assiette_270(cls):
        return 0

    @classmethod
    def default_retenue_270(cls):
        return 0

    @classmethod
    def default_assiette_271(cls):
        return 0

    @classmethod
    def default_retenue_271(cls):
        return 0

    @classmethod
    def default_assiette_200(cls):
        return 0

    @classmethod
    def default_retenue_200(cls):
        return 0

    @classmethod
    def default_assiette_191(cls):
        return 0

    @classmethod
    def default_retenue_191(cls):
        return 0

    @classmethod
    def default_assiette_192(cls):
        return 0

    @classmethod
    def default_retenue_192(cls):
        return 0

    @classmethod
    def default_assiette_051(cls):
        return 0

    @classmethod
    def default_retenue_051(cls):
        return 0

    @classmethod
    def default_assiette_210(cls):
        return 0

    @classmethod
    def default_retenue_210(cls):
        return 0

    @classmethod
    def default_assiette_220(cls):
        return 0

    @classmethod
    def default_retenue_220(cls):
        return 0

    @classmethod
    def default_assiette_250(cls):
        return 0

    @classmethod
    def default_retenue_250(cls):
        return 0

    @classmethod
    def default_assiette_280(cls):
        return 0

    @classmethod
    def default_retenue_280(cls):
        return 0

    @classmethod
    def default_assiette_290(cls):
        return 0

    @classmethod
    def default_retenue_290(cls):
        return 0

    @classmethod
    def default_retenue_300(cls):
        return 0

    @classmethod
    def default_retenue_400(cls):
        return 0

    @classmethod
    def get_assiettes_total(cls, declarations, name):
        assiettes_total = {}
        for declaration in declarations:
            assiettes_total.setdefault(declaration.id, Decimal('0.0'))
            assiettes_total[declaration.id] = declaration.assiette_010 + \
                declaration.assiette_170 + \
                declaration.assiette_021 + declaration.assiette_023 + declaration.assiette_025 + \
                declaration.assiette_030 + declaration.assiette_180 + \
                declaration.assiette_040 + \
                declaration.assiette_260 + \
                declaration.assiette_060 + \
                declaration.assiette_071 + declaration.assiette_073 + \
                declaration.assiette_080 + \
                declaration.assiette_091 + declaration.assiette_093 + \
                declaration.assiette_100 + declaration.assiette_110 + \
                declaration.assiette_121 + declaration.assiette_122 + declaration.assiette_123 + \
                declaration.assiette_131 + declaration.assiette_132 + \
                declaration.assiette_140 + \
                declaration.assiette_150 + \
                declaration.assiette_160 + \
                declaration.assiette_270 + \
                declaration.assiette_271 + \
                declaration.assiette_200 + \
                declaration.assiette_191 + declaration.assiette_192 + \
                declaration.assiette_210 + \
                declaration.assiette_220 + \
                declaration.assiette_250 + \
                declaration.assiette_280 + \
                declaration.assiette_290
        return assiettes_total

    @classmethod
    def get_retenues_total(cls, declarations, name):
        retenues_total = {}
        for declaration in declarations:
            retenues_total.setdefault(declaration.id, Decimal('0.0'))
            retenues_total[declaration.id] = declaration.retenue_010 + \
                declaration.retenue_170 + \
                declaration.retenue_300 + \
                declaration.retenue_400 + \
                declaration.retenue_021 + declaration.retenue_023 + declaration.retenue_025 + \
                declaration.retenue_030 + declaration.retenue_180 + \
                declaration.retenue_040 + \
                declaration.retenue_260 + \
                declaration.retenue_060 + \
                declaration.retenue_071 + declaration.retenue_073 + \
                declaration.retenue_080 + \
                declaration.retenue_091 + declaration.retenue_093 + \
                declaration.retenue_100 + declaration.retenue_110 + \
                declaration.retenue_121 + declaration.retenue_122 + declaration.retenue_123 + \
                declaration.retenue_131 + declaration.retenue_132 + \
                declaration.retenue_140 + \
                declaration.retenue_150 + \
                declaration.retenue_160 + \
                declaration.retenue_270 + \
                declaration.retenue_271 + \
                declaration.retenue_200 + \
                declaration.retenue_191 + declaration.retenue_192 + \
                declaration.retenue_210 + \
                declaration.retenue_220 + \
                declaration.retenue_250 + \
                declaration.retenue_280 + \
                declaration.retenue_290
        return retenues_total

    def get_company_address_formatted(self, address):
        street = address.street or ''
        city = f' {address.city}' or ''
        subdivision = address.subdivision.name or ''
        postal_code = address.postal_code or ''
        address_formatted = f'{street} -{city} {subdivision} {postal_code}'
        return address_formatted

    # TODO do we need this ?
    # def texte_recap(self, id):
    #     pool = Pool()
    #     User = pool.get('res.user')
    #     user = User.browse([Transaction().user])[0]
    #     print(user.id)
    #     company = user.company
    #     print(company.party.name)
    #     company_address = self.get_company_address_formatted(
    #         company.party.addresses[0])
    #     declaration = self.browse([id])[0]
    #     print(company_address)
    #     print(company.party.identifiers[0].code.zfill(8))
    #     print(company.party.identifiers[0].code_categorie or '')
    #     print(company.party.identifiers[0].etablissement or '' )
    #     print(declaration.fiscalyear.name)
    #     position_4_to_19 = company.party.identifiers[0].code.zfill(8) +\
    #         (company.party.identifiers[0].code_categorie or '') + \
    #         (company.party.identifiers[0].etablissement or '') + \
    #         declaration.fiscalyear.name
    #     anx1 = '1'
    #     anx2 = '1'
    #     anx3 = '1'
    #     anx4 = '1'
    #     anx5 = '1'
    #     anx6 = '1'
    #     anx7 = '1'
    #     if declaration.presence_anx1:
    #         anx1 = '0'
    #     if declaration.presence_anx2:
    #         anx2 = '0'
    #     if declaration.presence_anx3:
    #         anx3 = '0'
    #     if declaration.presence_anx4:
    #         anx4 = '0'
    #     if declaration.presence_anx5:
    #         anx5 = '0'
    #     if declaration.presence_anx6:
    #         anx6 = '0'
    #     if declaration.presence_anx7:
    #         anx7 = '0'
    #     res = '000' + position_4_to_19 + \
    #         anx1 + anx2 + anx3 + anx4 + anx5 + anx6 + anx7 + ''.ljust(12) + \
    #         '\n' + \
    #         '010' + str(int(declaration.assiette_010 * 1000)).zfill(15) + \
    #         '00000' + str(int(declaration.retenue_010 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '170' + str(int(declaration.assiette_170 * 1000)).zfill(15) + \
    #         '00000' + str(int(declaration.retenue_170 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '300' + ''.zfill(20) + \
    #         str(int(declaration.retenue_300 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '400' + ''.zfill(20) + \
    #         str(int(declaration.retenue_400 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '021' + str(int(declaration.assiette_021 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_021 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '023' + str(int(declaration.assiette_023 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_023 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '025' + str(int(declaration.assiette_025 * 1000)).zfill(15) + \
    #         '00250' + str(int(declaration.retenue_025 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '030' + str(int(declaration.assiette_030 * 1000)).zfill(15) + \
    #         '00500' + str(int(declaration.retenue_030 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '180' + str(int(declaration.assiette_180 * 1000)).zfill(15) + \
    #         '00250' + str(int(declaration.retenue_180 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '040' + str(int(declaration.assiette_040 * 1000)).zfill(15) + \
    #         '00500' + str(int(declaration.retenue_040 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '260' + str(int(declaration.assiette_260 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_260 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '060' + str(int(declaration.assiette_060 * 1000)).zfill(15) + \
    #         '02000' + str(int(declaration.retenue_060 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '071' + str(int(declaration.assiette_071 * 1000)).zfill(15) + \
    #         '02000' + str(int(declaration.retenue_071 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '073' + str(int(declaration.assiette_073 * 1000)).zfill(15) + \
    #         '02000' + str(int(declaration.retenue_073 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '080' + str(int(declaration.assiette_080 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_080 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '241' + str(int(declaration.assiette_241 * 1000)).zfill(15) + \
    #         '00500' + str(int(declaration.retenue_241 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '242' + str(int(declaration.assiette_242 * 1000)).zfill(15) + \
    #         '00500' + str(int(declaration.retenue_242 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '091' + str(int(declaration.assiette_091 * 1000)).zfill(15) + \
    #         '02000' + str(int(declaration.retenue_091 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '093' + str(int(declaration.assiette_093 * 1000)).zfill(15) + \
    #         '02000' + str(int(declaration.retenue_093 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '100' + str(int(declaration.assiette_100 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_100 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '110' + str(int(declaration.assiette_110 * 1000)).zfill(15) + \
    #         '00500' + str(int(declaration.retenue_110 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '121' + str(int(declaration.assiette_121 * 1000)).zfill(15) + \
    #         '00250' + str(int(declaration.retenue_121 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '122' + str(int(declaration.assiette_122 * 1000)).zfill(15) + \
    #         '00250' + str(int(declaration.retenue_122 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '123' + str(int(declaration.assiette_123 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_123 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '131' + str(int(declaration.assiette_131 * 1000)).zfill(15) + \
    #         '00050' + str(int(declaration.retenue_131 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '132' + str(int(declaration.assiette_132 * 1000)).zfill(15) + \
    #         '00150' + str(int(declaration.retenue_132 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '140' + str(int(declaration.assiette_140 * 1000)).zfill(15) + \
    #         '05000' + str(int(declaration.retenue_140 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '150' + str(int(declaration.assiette_150 * 1000)).zfill(15) + \
    #         '10000' + str(int(declaration.retenue_150 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '160' + str(int(declaration.assiette_160 * 1000)).zfill(15) + \
    #         '00000' + str(int(declaration.retenue_160 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '270' + str(int(declaration.assiette_270 * 1000)).zfill(15) + \
    #         '02500' + str(int(declaration.retenue_270 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '271' + str(int(declaration.assiette_271 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_271 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '200' + str(int(declaration.assiette_200 * 1000)).zfill(15) + \
    #         '00100' + str(int(declaration.retenue_200 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '191' + str(int(declaration.assiette_191 * 1000)).zfill(15) + \
    #         '01000' + str(int(declaration.retenue_191 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '192' + str(int(declaration.assiette_192 * 1000)).zfill(15) + \
    #         '02500' + str(int(declaration.retenue_192 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '051' + str(int(declaration.assiette_051 * 1000)).zfill(15) + \
    #         '01500' + str(int(declaration.retenue_051 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '220' + str(int(declaration.assiette_220 * 1000)).zfill(15) + \
    #         '02500' + str(int(declaration.retenue_220 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '250' + str(int(declaration.assiette_250 * 1000)).zfill(15) + \
    #         '00150' + str(int(declaration.retenue_250 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '280' + str(int(declaration.assiette_280 * 1000)).zfill(15) + \
    #         '02500' + str(int(declaration.retenue_280 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '290' + str(int(declaration.assiette_290 * 1000)).zfill(15) + \
    #         '00300' + str(int(declaration.retenue_290 * 1000)).zfill(15) + \
    #         '\n' + \
    #         '999' + ''.ljust(20) + \
    #         str(int(declaration.retenues_total * 1000)).zfill(15)
    #     # res = (res.upper()).encode('ascii', 'replace')
    #     # print(res)
    #     return res

    # def texte_annexe1(self, id):
    #     pool = Pool()
    #     User = pool.get('res.user')
    #     user = User.browse([Transaction().user])[0]
    #     party = user.company.party
    #     company_address = get_company_address_formatted(party.addresses[0])
    #     declaration = self.browse([id])[0]
    #     position_3_to_18 = party.identifiers[0].code.zfill(8) + party.code_categorie + \
    #         party.etablissement + declaration.fiscalyear.name
    #     res = 'E1' + position_3_to_18 + \
    #         'An1' + declaration.code_acte + str(len(declaration.annexe1_lines)).zfill(6) + party.name.ljust(40) + \
    #         (party.activite or '').ljust(40) + \
    #         (company_address.city or '').ljust(40) + \
    #         ((company_address.street or '') + (company_address.streetbis or '')).ljust(72) + \
    #         '0034' + \
    #         (company_address.zip or '').ljust(4) + \
    #         ''.ljust(177) + '\n'
    #     for line in declaration.annexe1_lines:

    #         if not (line.party.vat_number or line.party.identifiant):
    #             self.raise_user_error(
    #                 'identifiant manquant:' + line.party.name)
    #         tiers = line.party
    #         party_address = tiers.addresses[0]
    #         adresse_tiers = (party_address.street or '') + ' ' + \
    #             (party_address.streetbis or '') + ' ' + \
    #             (party_address.zip or '') + ' ' + \
    #             (party_address.city or '')
    #         if tiers.nature_identifiant == 'cin':
    #             nature_id = '2'
    #             identifiant_tiers = tiers.identifiant.zfill(8) + ''.ljust(5)
    #         elif tiers.nature_identifiant == 'carte de sejour':
    #             nature_id = '3'
    #             identifiant_tiers = tiers.identifiant.zfill(8) + ''.ljust(5)
    #         else:
    #             self.raise_user_error(
    #                 'nature identifiant invalide:' + tiers.name)
    #         res += 'L1' + \
    #             position_3_to_18 + \
    #             str(line.ordre).zfill(6) + nature_id + \
    #             (tiers.identifiant.rjust(7, ' ')).ljust(13) + \
    #             tiers.name.ljust(40) + (tiers.activite or '').ljust(40) + \
    #             adresse_tiers.ljust(120) + \
    #             line.situation + str(line.nbre_enfants).zfill(2) + \
    #             line.date_debut.strftime("%d%m%Y") + line.date_fin.strftime("%d%m%Y") + str(line.duree).zfill(3) + \
    #             str(int(line.revenu_imposable * 1000)).zfill(15) + \
    #             str(int(line.avantages * 1000)).zfill(15) + \
    #             str(int(line.revenu_imposable_total * 1000)).zfill(15) + \
    #             str(int(line.revenu_reinvesti * 1000)).zfill(15) + \
    #             str(int(line.retenues_regime_commun * 1000)).zfill(15) + \
    #             str(int(line.retenues_taux20 * 1000)).zfill(15) + \
    #             str(int(line.contribution_solidarite * 1000)).zfill(15) + \
    #             str(int(line.contribution_2020 * 1000)).zfill(15) + \
    #             str(int(line.montant_net * 1000)).zfill(15) + \
    #             ''.ljust(10) + '\n'
    #     res += 'T1' + \
    #         position_3_to_18 + \
    #         ''.ljust(242) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'revenu_imposable') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'avantages') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'revenu_imposable_total') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'revenu_reinvesti') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'retenues_regime_commun') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'retenues_taux20') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'contribution_solidarite') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'contribution_2020') * 1000)).zfill(15) + \
    #         str(int(self.sum(declaration.annexe1_lines, 'montant_net') * 1000)).zfill(15) + \
    #         ''.ljust(10) + '\n'
    #     res = self.supprime_accent(res)
    #     res = (res.upper()).encode('ascii', 'replace')
    #     print res
    #     return res
    # @classmethod
    # def set_assiettes_total(cls, declarations, name, value):
    #     pass

    # @classmethod
    # def set_retenues_total(cls, declarations, name, value):
    #     pass


class Annexe1Line(ModelSQL, ModelView):
    'Annexe 1 Line'
    __name__ = 'declaration_employeur.annexe1.line'

    declaration = fields.Many2One(
        'declaration_employeur.declaration', 'Declaration', required=True)
    ordre = fields.Integer('Ordre')
    party = fields.Many2One('party.party', 'Tiers', required=True)
    situation = fields.Selection([
        ('1', '1- Célibataire'),
        ('2', '2- Marié(e)'),
        ('3', '3- Divorcé(e)'),
        ('4', '4- Veuf/Veuve'),
        ], 'Situation familiale', required=True)
    nbre_enfants = fields.Integer('Nombre Enfants')
    date_debut = fields.Date('Date début', required=True)
    date_fin = fields.Date('Date fin', required=True)
    duree = fields.Integer('Durée en jours')
    revenu_imposable = fields.Numeric('Revenu imposable', digits=(16, 3))
    avantages = fields.Numeric('Avantages en nature', digits=(16, 3))
    revenu_imposable_total = fields.Function(fields.Numeric('Total du revenu bruts imposable', digits=(16, 3),
            readonly=True), 'on_change_with_revenu_imposable_total')
    revenu_reinvesti = fields.Numeric('Revenu reinvesti', digits=(16, 3))
    retenues_regime_commun = fields.Numeric(
        'Retenues selon régime commun', digits=(16, 3))
    retenues_taux20 = fields.Numeric('Retenues selon taux 20', digits=(16, 3))
    contribution_solidarite = fields.Numeric(
        'Contribution de solidarité 2018', digits=(16, 3))
    contribution_2020 = fields.Numeric('Contribution 2020', digits=(16, 3))
    conpensation = fields.Numeric(
        'Redevance caisse de conpensation', digits=(16, 3))
    montant_net = fields.Function(fields.Numeric('Net servi', digits=(16, 3),
            readonly=True), 'on_change_with_montant_net')

    @fields.depends('revenu_imposable', 'avantages')
    def on_change_with_revenu_imposable_total(self, name=None):
        revenu_imposable_total = self.revenu_imposable + self.avantages
        return revenu_imposable_total

    @fields.depends('revenu_imposable', 'avantages', 'retenues_regime_commun',
        'retenues_taux20', 'contribution_solidarite', 'contribution_2020',
        'conpensation')
    def on_change_with_montant_net(self, name=None):
        montant_net = self.revenu_imposable + self.avantages - \
            self.retenues_regime_commun - self.retenues_taux20 - \
            self.contribution_solidarite - self.contribution_2020 - self.conpensation
        return montant_net


class Annexe2Line(ModelSQL, ModelView):
    'Annexe 2 Line'
    __name__ = 'declaration_employeur.annexe2.line'

    declaration = fields.Many2One(
        'declaration_employeur.declaration', 'Déclaration', required=True)
    ordre = fields.Integer('Ordre')
    party = fields.Many2One('party.party', 'Tiers', required=True)
    type_montant = fields.Selection([
        ('1', '1- Honoraires'),
        ('2', '2- Commissions'),
        ('3', '3- Courtages'),
        ('4', '4- Loyers'),
        ('5', '5- Rémunérations au titre des activités non commerciales'),
        ('0', '0- Montant brut Nul')
        ], 'Type des montants', required=True)
    montant_honoraires = fields.Numeric('Brut Honoraires', digits=(16, 3))
    montant_rr = fields.Numeric('Brut Honoraires Régime Réel', digits=(16, 3))
    montant_jetons = fields.Numeric('Brut Jetons', digits=(16, 3))
    montant_remunerations = fields.Numeric(
        'Brut Rémunérations', digits=(16, 3))
    montant_plusvalue = fields.Numeric('Brut Plus Value', digits=(16, 3))
    montant_hotels = fields.Numeric('Brut Loyers des Hôtels', digits=(16, 3))
    montant_artistes = fields.Numeric(
        'Rémunérations artistes et créateurs', digits=(16, 3))
    montant_bureaux_exportateurs = fields.Numeric(
        'Honoraires bureaux études exportateurs', digits=(16, 3))
    type_montant_exportation = fields.Selection([
        ('1', '1- Honoraires'),
        ('2', '2- Commissions'),
        ('3', '3- Courtages'),
        ('4', '4- Loyers'),
        ('5', '5- Rémunérations au titre des activités non commerciales'),
        ('0', '0- Montant brut Nul')
        ], 'Type des montants exportations', required=True)
    montant_honoraires_exportation = fields.Numeric(
        'Brut Honoraires exportations', digits=(16, 3))
    montant_retenues = fields.Numeric('Retenues', digits=(16, 3))
    montant_conpensation = fields.Numeric(
        'Caisse de conpensation', digits=(16, 3))
    montant_net = fields.Numeric('Net servi', digits=(16, 3))

    # TODO
    # def __init__(self):
    #     super(Annexe2Line, self).__init__()
    #     self._order.insert(0, ('ordre', 'ASC'))

    @classmethod
    def default_montant_honoraires(cls):
        return 0

    @classmethod
    def default_montant_rr(cls):
        return 0

    @classmethod
    def default_montant_jetons(cls):
        return 0

    @classmethod
    def default_montant_remunerations(cls):
        return 0

    @classmethod
    def default_montant_plusvalue(cls):
        return 0

    @classmethod
    def default_montant_hotels(cls):
        return 0

    @classmethod
    def default_montant_artistes(cls):
        return 0

    @classmethod
    def default_montant_bureaux_exportateurs(cls):
        return 0

    @classmethod
    def default_montant_honoraires_exportation(cls):
        return 0

    @classmethod
    def default_montant_retenues(cls):
        return 0

    @classmethod
    def default_montant_net(cls):
        return 0

    @classmethod
    def default_montant_conpensation(cls):
        return 0

    @fields.depends('montant_honoraires', 'montant_rr', 'montant_jetons',
            'montant_remunerations', 'montant_plusvalue', 'montant_hotels',
            'montant_artistes', 'montant_bureaux_exportateurs', 'montant_retenues')
    def on_change_with_montant_net(self, name=None):
        montant_net = self.montant_honoraires + self.montant_rr + self.montant_jetons + \
            self.montant_remunerations + self.montant_plusvalue + self.montant_hotels + \
            self.montant_artistes + self.montant_bureaux_exportateurs - self.montant_retenues
        return montant_net


class Annexe5Line(ModelSQL, ModelView):
    'Annexe 5 Line'
    __name__ = 'declaration_employeur.annexe5.line'

    declaration = fields.Many2One(
        'declaration_employeur.declaration', 'Déclaration', required=True)
    ordre = fields.Integer('Ordre')
    party = fields.Many2One('party.party', 'Tiers', required=True)
    montant_1000_export_IS10 = fields.Numeric(
        'Brut Montants Sup 1000 D export ou IS10', digits=(16, 3))
    montant_ret_1000_export_IS10 = fields.Numeric(
        'Retenues Montants Sup 1000 D\'export ou IS10', digits=(16, 3))
    montant_1000_autres = fields.Numeric(
        'Brut Autres Montants Sup 1000 D', digits=(16, 3))
    montant_ret_1000_autres = fields.Numeric(
        'Retenues Autres Montants Sup 1000 D', digits=(16, 3))
    montant_1000_public = fields.Numeric(
        'Brut Montants Sup 1000 D\'Etablissements Publics TVA', digits=(16, 3))
    montant_ret_1000_public = fields.Numeric(
        'Retenues Montants Sup 1000 D\'Etablissements Publics TVA', digits=(16, 3))
    montant_marches_nonresidents = fields.Numeric(
        'Brut Marches avec non résidents', digits=(16, 3))
    montant_ret_marches_nonresidents = fields.Numeric(
        'Retenues Marches avec non résidents', digits=(16, 3))
    montant_conpensation = fields.Numeric(
        'Brut Caisse Conpensation', digits=(16, 3))
    montant_net = fields.Numeric('Net servi', digits=(16, 3))

    @classmethod
    def default_montant_1000_export_IS10(cls):
        return 0

    @classmethod
    def default_montant_ret_1000_export_IS10(cls):
        return 0

    @classmethod
    def default_montant_1000_autres(cls):
        return 0

    @classmethod
    def default_montant_ret_1000_autres(cls):
        return 0

    @classmethod
    def default_montant_1000_public(cls):
        return 0

    @classmethod
    def default_montant_ret_1000_public(cls):
        return 0

    @classmethod
    def default_montant_conpensation(cls):
        return 0

    @classmethod
    def default_montant_marches_nonresidents(cls):
        return 0

    @classmethod
    def default_montant_ret_marches_nonresidents(cls):
        return 0

    @fields.depends('montant_1000_export_IS10', 'montant_ret_1000_export_IS10',
        'montant_1000_autres', 'montant_ret_1000_autres',
        'montant_1000_public', 'montant_ret_1000_public',
        'montant_marches_nonresidents', 'montant_ret_marches_nonresidents',
        'montant_conpensation')
    def on_change_with_montant_net(self, name=None):
        montant_net = self.montant_1000_export_IS10 - self.montant_ret_1000_export_IS10 +  \
            self.montant_1000_autres - self.montant_ret_1000_autres + \
            self.montant_1000_public - self.montant_ret_1000_public + \
            self.montant_marches_nonresidents - self.montant_ret_marches_nonresidents - \
            self.montant_conpensation
        return montant_net


class Annexe6Line(ModelSQL, ModelView):
    'Annexe 6 Line'
    __name__ = 'declaration_employeur.annexe6.line'
    _description = __doc__

    declaration = fields.Many2One(
        'declaration_employeur.declaration', 'Déclaration', required=True)
    ordre = fields.Integer('Ordre')
    party = fields.Many2One('party.party', 'Tiers', required=True)
    montant_ristournes = fields.Numeric('Ristournes servies', digits=(16, 3))
    montant_ventes_forfaitaire = fields.Numeric(
        'Ventes aux P.P régime forfaitaire', digits=(16, 3))
    montant_avance_ventes_forfaitaire = fields.Numeric(
        'Avance sur ventes aux P.P régime forfaitaire', digits=(16, 3))
    montant_jeux_hasard = fields.Numeric('Jeux de hasard', digits=(16, 3))
    retenue_jeux_hasard = fields.Numeric(
        'Retenue Jeux de hasard', digits=(16, 3))
    montant_distribution_20md = fields.Numeric(
        'Ventes distribution 20mD', digits=(16, 3))
    retenue_distribution_20md = fields.Numeric(
        'Retenue Ventes distribution 20mD', digits=(16, 3))
    montant_especes = fields.Numeric('Recouvrement en espèces', digits=(16, 3))


class DeclarationReport(Report):
    __name__ = 'declaration_employeur.declaration'

    @classmethod
    def get_company_address_formatted(cls, address):
        street = address.street or ''
        city = f' {address.city}' or ''
        subdivision = address.subdivision.name or ''
        postal_code = address.postal_code or ''
        address_formatted = f'{street} -{city} {subdivision} {postal_code}'
        return address_formatted.upper()

    @classmethod
    def sum(cls, lines, field):
        result = Decimal('0.0')
        for line in lines:
            result += line[field]
        return result

    @classmethod
    def get_context(cls, records, header, data):
        pool = Pool()
        Date = pool.get('ir.date')
        User = pool.get('res.user')
        user = User.browse([Transaction().user])
        context = super().get_context(records, header, data)
        context['company'] = user[0].company
        context['user'] = user[0]
        context['sum'] = cls.sum
        context['currency'] = user[0].company.currency
        context['format_address'] = cls.get_company_address_formatted
        context['retenues'] = records
        context['today'] = Date.today()
        return context


class CreateDeclaration(Wizard):
    'Create Declaration'
    __name__ = 'declaration_employeur.create_declaration'

    start = StateView('declaration_employeur.create_declaration.parameters',
        'declaration_employeur.create_declaration_parameters_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'create_declaration', 'tryton-ok', default=True),
            ])
    create_declaration = StateTransition()
    open_declaration = StateAction('declaration_employeur.act_declaration_create')

    def default_start(self, name):
        pool = Pool()
        context = Transaction().context
        fiscalyear = context.get('fiscalyear') or None
        today_date = datetime.date.today()
        return {
            'fiscalyear': fiscalyear,
            'from_date': datetime.date(today_date.year, 1, 1),
            'to_date': today_date,
            }

    def transition_create_declaration(self):
        pool = Pool()
        Declaration = pool.get('declaration_employeur.declaration')
        Party = pool.get('party.party')
        Retenue = pool.get('retenue_source.retenue')
        RetenueType = pool.get('retenue_source.retenue.type')
        Annexe2Line = pool.get('declaration_employeur.annexe2.line')
        Annexe5Line = pool.get('declaration_employeur.annexe5.line')

        assiette_010 = retenue_010 = Decimal('0')
        assiette_021 = retenue_021 = Decimal('0')
        assiette_022 = retenue_022 = Decimal('0')
        assiette_023 = retenue_023 = Decimal('0')
        assiette_024 = retenue_024 = Decimal('0')
        assiette_030 = retenue_030 = Decimal('0')
        assiette_040 = retenue_040 = Decimal('0')
        assiette_051 = retenue_051 = Decimal('0')
        assiette_052 = retenue_052 = Decimal('0')
        assiette_060 = retenue_060 = Decimal('0')
        assiette_071 = retenue_071 = Decimal('0')
        assiette_072 = retenue_072 = Decimal('0')
        assiette_073 = retenue_073 = Decimal('0')
        assiette_074 = retenue_074 = Decimal('0')
        assiette_080 = retenue_080 = Decimal('0')
        assiette_091 = retenue_091 = Decimal('0')
        assiette_092 = retenue_092 = Decimal('0')
        assiette_093 = retenue_093 = Decimal('0')
        assiette_094 = retenue_094 = Decimal('0')
        assiette_100 = retenue_100 = Decimal('0')
        assiette_110 = retenue_110 = Decimal('0')
        assiette_121 = retenue_121 = Decimal('0')
        assiette_122 = retenue_122 = Decimal('0')
        assiette_123 = retenue_123 = Decimal('0')
        assiette_131 = retenue_131 = Decimal('0')
        assiette_132 = retenue_132 = Decimal('0')
        assiette_140 = retenue_140 = Decimal('0')
        assiette_150 = retenue_150 = Decimal('0')
        assiette_160 = retenue_160 = Decimal('0')

        declaration = Declaration.create([{
            'fiscalyear': self.start.fiscalyear.id,
            'code_acte': '0',
            'description': time.strftime('%d-%m-%Y %H:%M', time.localtime())
            }])[0]
        parties = Party.search([])
        retenue_types = RetenueType.search([])
        for party in parties:
            for retenue_type in retenue_types:
                retenues = Retenue.search([
                    ('party', '=', party.id),
                    ('type', '=', retenue_type.id),
                    ('date', '>=', self.start.from_date),
                    ('date', '<=', self.start.to_date),
                    ])
                montant_brut = Decimal('0')
                montant_retenue = Decimal('0')
                montant_net = Decimal('0')
                for retenue in retenues:
                    montant_brut += retenue.montant_brut
                    montant_retenue += retenue.montant_retenue
                    montant_net += retenue.montant_net
                if montant_retenue:
                    if retenue_type.code[:2] == '01':
                        raise UserError('Retenue de type 1 !!!')
                    elif retenue_type.code[:2] == '02':
                        raise UserError('Retenue de type 2 !!!:')
                    elif retenue_type.code[:3] == '03a':
                        assiette_021 += montant_brut
                        retenue_021 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_honoraires': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '03b':
                        assiette_021 += montant_brut
                        retenue_021 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_honoraires': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '03c':
                        assiette_023 += montant_brut
                        retenue_023 += montant_retenue
                    elif retenue_type.code[:3] == '03d':
                        assiette_023 += montant_brut
                        retenue_023 += montant_retenue
                    elif retenue_type.code[:2] == '04':
                        assiette_030 += montant_brut
                        retenue_030 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_rr': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:2] == '05':
                        raise UserError('retenue de type 5 !!!:')
                    elif retenue_type.code[:2] == '06':
                        assiette_040 += montant_brut
                        retenue_040 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_hotels': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '071':
                        assiette_051 += montant_brut
                        retenue_051 += montant_retenue
                    elif retenue_type.code[:3] == '072':
                        assiette_051 += montant_brut
                        retenue_051 += montant_retenue
                    elif retenue_type.code[:2] == '08':
                        assiette_060 += montant_brut
                        retenue_060 += montant_retenue
                    elif retenue_type.code[:3] == '091':
                        assiette_071 += montant_brut
                        retenue_071 += montant_retenue
                    elif retenue_type.code[:3] == '092':
                        assiette_071 += montant_brut
                        retenue_071 += montant_retenue
                    elif retenue_type.code[:3] == '093':
                        assiette_073 += montant_brut
                        retenue_073 += montant_retenue
                    elif retenue_type.code[:3] == '094':
                        assiette_073 += montant_brut
                        retenue_073 += montant_retenue
                    elif retenue_type.code[:2] == '10':
                        assiette_080 += montant_brut
                        retenue_080 += montant_retenue
                    elif retenue_type.code[:3] == '11a':
                        assiette_091 += montant_brut
                        retenue_091 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_jetons': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '11b':
                        assiette_091 += montant_brut
                        retenue_091 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_jetons': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '11c':
                        assiette_093 += montant_brut
                        retenue_093 += montant_retenue
                    elif retenue_type.code[:3] == '11d':
                        assiette_093 += montant_brut
                        retenue_093 += montant_retenue
                    elif retenue_type.code[:2] == '12':
                        assiette_100 += montant_brut
                        retenue_100 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_remunerations': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:2] == '13':
                        assiette_110 += montant_brut
                        retenue_110 += montant_retenue
                    elif retenue_type.code[:3] == '14a':
                        assiette_121 += montant_brut
                        retenue_121 += montant_retenue
                        Annexe2Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'type_montant': '1',
                            'montant_plusvalue': montant_brut,
                            'type_montant_exportation': '0',
                            'montant_retenues': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '14b':
                        assiette_122 += montant_brut
                        retenue_122 += montant_retenue
                    elif retenue_type.code[:3] == '14c':
                        assiette_123 += montant_brut
                        retenue_123 += montant_retenue
                    elif retenue_type.code[:3] == '15a':
                        assiette_132 += montant_brut
                        retenue_132 += montant_retenue
                        Annexe5Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'montant_1000_autres': montant_brut,
                            'montant_ret_1000_autres': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '15b':
                        assiette_132 += montant_brut
                        retenue_132 += montant_retenue
                        Annexe5Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'montant_1000_autres': montant_brut,
                            'montant_ret_1000_autres': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:2] == '16':
                        assiette_140 += montant_brut
                        retenue_140 += montant_retenue
                        Annexe5Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'montant_1000_public': montant_brut,
                            'montant_ret_1000_public': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:2] == '17':
                        assiette_150 += montant_brut
                        retenue_150 += montant_retenue
                        Annexe5Line.create([{
                            'declaration': declaration.id,
                            'party': party.id,
                            'montant_marches_nonresidents': montant_brut,
                            'montant_ret_marches_nonresidents': montant_retenue,
                            'montant_net': montant_net,
                            }])
                    elif retenue_type.code[:3] == '18':
                        assiette_160 += montant_brut
                        retenue_160 += montant_retenue
                    elif retenue_type.code[:3] == '19a':
                        raise UserError('retenue de type 19a !!!:')
                    elif retenue_type.code[:3] == '19b':
                        raise UserError('retenue de type 19b !!!:')
                    else:
                        raise UserError(
                            'il existe des retenues de type non pris en compte !')
        Declaration.write([declaration], {
            'assiette_010': assiette_010,
            'retenue_010': retenue_010,
            'assiette_021': assiette_021,
            'retenue_021': retenue_021,
            'assiette_023': assiette_023,
            'retenue_023': retenue_023,
            'assiette_030': assiette_030,
            'retenue_030': retenue_030,
            'assiette_040': assiette_040,
            'retenue_040': retenue_040,
            'assiette_051': assiette_051,
            'retenue_051': retenue_051,
            'assiette_060': assiette_060,
            'retenue_060': retenue_060,
            'assiette_071': assiette_071,
            'retenue_071': retenue_071,
            'assiette_073': assiette_073,
            'retenue_073': retenue_073,
            'assiette_080': assiette_080,
            'retenue_080': retenue_080,
            'assiette_091': assiette_091,
            'retenue_091': retenue_091,
            'assiette_093': assiette_093,
            'retenue_093': retenue_093,
            'assiette_100': assiette_100,
            'retenue_100': retenue_100,
            'assiette_110': assiette_110,
            'retenue_110': retenue_110,
            'assiette_121': assiette_121,
            'retenue_121': retenue_121,
            'assiette_122': assiette_122,
            'retenue_122': retenue_122,
            'assiette_123': assiette_123,
            'retenue_123': retenue_123,
            'assiette_131': assiette_131,
            'retenue_131': retenue_131,
            'assiette_132': assiette_132,
            'retenue_132': retenue_132,
            'assiette_140': assiette_140,
            'retenue_140': retenue_140,
            'assiette_150': assiette_150,
            'retenue_150': retenue_150,
            'assiette_160': assiette_160,
            'retenue_160': retenue_160,
            })

        # Ajouter les numeros dordre aux lignes des annexes
        lines_2 = Annexe2Line.search([('declaration', '=', declaration.id)])
        ordre_2 = 0
        for line in lines_2:
            ordre_2 += 1
            Annexe2Line.write([line], {'ordre': ordre_2})
        lines_5 = Annexe5Line.search([('declaration', '=', declaration.id)])
        ordre_5 = 0
        for line in lines_5:
            ordre_5 += 1
            Annexe5Line.write(line, {'ordre': ordre_5})
        return 'open_declaration'


class CreateDeclarationParameters(ModelView):
    'Create Declaration Parameters'
    __name__ = 'declaration_employeur.create_declaration.parameters'

    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
            required=True)
    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
