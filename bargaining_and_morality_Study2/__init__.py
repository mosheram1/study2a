from otree.api import *
import random
import ast
import json
from bargaining_and_morality_Study1c import Instructions

class C(BaseConstants):
    NAME_IN_URL = 'mini_trust_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 2
    TRUST_POINTS = 30
    NO_TRUST_POINTS = 10
    REWARD_MULTIPLIER = 0.10
    LETTERS = ['A', 'B', 'C', 'D', 'E', 'F']
    NUMBERS = [1, 2, 3, 4, 5, 6]

class Subsession(BaseSubsession):
    pass
def creating_session(self):
    for group in self.get_groups():
        players = group.get_players()

        if self.round_number == 1:
            players[0].participant_role = 'Sender'
            players[1].participant_role = 'Receiver'

            # קבע תפקיד לשלב 2 והעבר ל-participant.vars
            roles = ['First', 'Second']
            random.shuffle(roles)
            players[0].stage2_role = roles[0]
            players[0].participant.vars['fixed_stage2_role'] = roles[0]

            players[1].stage2_role = roles[1]
            players[1].participant.vars['fixed_stage2_role'] = roles[1]

        else:
            # שמור על אותו תפקיד כמו בסיבוב הראשון
            for p in players:
                p.stage2_role = p.participant.vars['fixed_stage2_role']

        # יצירת מיפוי מחדש בכל סיבוב
        letters = C.LETTERS.copy()
        numbers = C.NUMBERS.copy()
        random.shuffle(numbers)
        group.letter_number_mapping = json.dumps(dict(zip(letters, numbers)))


        # יצירת מיפוי מחדש בכל סיבוב
        letters = C.LETTERS.copy()
        numbers = C.NUMBERS.copy()
        random.shuffle(numbers)
        group.letter_number_mapping = json.dumps(dict(zip(letters, numbers)))



class Group(BaseGroup):
    sender_decision = models.BooleanField(choices=[(False, "No Trust (Keep 10 points)"), (True, "Full Trust (Send 30 points)")], label="Sender Decision", blank=False)
    receiver_decision = models.BooleanField(choices=[(True, "Trustworthy (Return 15 points)"), (False, "Untrustworthy (Keep all 30 points)")], label="Receiver's Strategy Method Decision", blank=False)
    sender_payoff = models.FloatField()
    receiver_payoff = models.FloatField()

    letter_number_mapping = models.StringField()
    number_report_A = models.IntegerField(label="Enter the number under your chosen letter:", min=1, max=6)
    number_report_B = models.IntegerField(label="Enter the number under your chosen letter:", min=1, max=6)
    stage2_payoff_A = models.FloatField(initial=0)
    stage2_payoff_B = models.FloatField(initial=0)

    def set_stage2_payoffs(self):
        number_A = self.field_maybe_none('number_report_A')
        number_B = self.field_maybe_none('number_report_B')

        # ברירת מחדל: אפס
        self.stage2_payoff_A = 0
        self.stage2_payoff_B = 0

        # רק אם אנחנו בסיבוב השני ויש התאמה
        if self.round_number == 2 and number_A is not None and number_B is not None and number_A == number_B:
            payout = number_B / 2
            self.stage2_payoff_A = payout
            self.stage2_payoff_B = payout

        # עדכון payoff לכל שחקן
        for p in self.get_players():
            if p.stage2_role == 'First':
                p.payoff = self.stage2_payoff_A
            else:
                p.payoff = self.stage2_payoff_B


class Player(BasePlayer):
    participant_role = models.StringField(initial='')
    stage2_role = models.StringField(initial='')
    total_payoff = models.FloatField()
    Age_dec = models.StringField(
        choices=["I am over 18 and agree to participate"],
        label="Consent",
        widget=widgets.RadioSelect,
    )
    MTurk_ID = models.StringField(label="Please write your MTurk ID (for verification):")
    Residence = models.StringField(
        choices=["Yes", "No"],
        label="Do you live in the United States?",
        widget=widgets.RadioSelect,
    )
    English = models.StringField(
        choices=["Yes", "No"],
        label="Do you speak, read, and write English fluently?",
        widget=widgets.RadioSelect,
    )
    Verification = models.StringField(
        choices=["Yes", "No"],
        label="Are you reading carefully? Please mark 'no' in this question.",
        widget=widgets.RadioSelect,
    )
    wants_same_partner = models.BooleanField(
        label="Would you like to continue with the same partner in the next stage?",
        choices=[
            (True, "Yes, I prefer to continue with the same person."),
            (False, "No, I prefer to be matched with a new person.")
        ],
        widget=widgets.RadioSelect
    )
    Age = models.StringField(choices=[['18-29', '18-29'], ['30-39', '30-39'], ['40-49', '40-49'], ['50-59', '50-59'],
                                      ['60+', '60 or older']], label='Which category below includes your age?')
    Gender = models.StringField(choices=[['Male', 'Male'], ['Female', 'Female'], ['Not listed', 'Not listed']],
                                label='What is your gender?')
    feedback = models.LongStringField(blank=True,
                                      label='Is there any feedback you’d like to give about this research study?')

def set_payoffs(group: Group):
    players = group.get_players()
    sender = players[0]
    receiver = players[1]

    sender_decision = group.field_maybe_none('sender_decision')
    receiver_decision = group.field_maybe_none('receiver_decision')

    if sender_decision is None:
        return

    if sender_decision:
        if receiver_decision is None:
            return
        if receiver_decision:
            group.sender_payoff = 15 * C.REWARD_MULTIPLIER
            group.receiver_payoff = 15 * C.REWARD_MULTIPLIER
        else:
            group.sender_payoff = 0
            group.receiver_payoff = 30 * C.REWARD_MULTIPLIER
    else:
        group.sender_payoff = C.NO_TRUST_POINTS * C.REWARD_MULTIPLIER
        group.receiver_payoff = 0

    sender.total_payoff = group.sender_payoff
    receiver.total_payoff = group.receiver_payoff


class InstructionsPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class WaitForPartner(WaitPage):
    wait_for_all_groups = False  # optional: speeds up matching

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    body_text = "Please wait while we match you with another participant..."

class TrustGame(Page):
    form_model = 'group'

    @staticmethod
    def get_form_fields(player: Player):
        if player.participant_role == 'Sender':
            return ['sender_decision']
        elif player.participant_role == 'Receiver':
            return ['receiver_decision']
        return []

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def before_next_page(self, timeout_happened):
        if self.group.field_maybe_none('sender_decision') is not None:
            if not self.group.sender_decision or self.group.field_maybe_none('receiver_decision') is not None:
                set_payoffs(self.group)


class WaitForReceiver(WaitPage):
    after_all_players_arrive = 'set_payoffs'
    @staticmethod
    def is_displayed(player: Player):
        return player.group.field_maybe_none('sender_decision') == True and player.round_number == 1
class WaitForResults(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    after_all_players_arrive = 'set_payoffs'

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.group.field_maybe_none('sender_payoff') is not None

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'sender_decision': player.group.field_maybe_none('sender_decision'),
            'receiver_decision': player.group.field_maybe_none('receiver_decision'),
            'participant_role': player.participant_role,
            'payoff': player.total_payoff,
        }
class PartnerPreference(Page):
    form_model = 'player'
    form_fields = ['wants_same_partner']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Intro2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        mapping_str = player.group.field_maybe_none('letter_number_mapping')
        try:
            mapping = ast.literal_eval(mapping_str) if mapping_str else {}
        except Exception:
            mapping = {}
        return {'letter_number_mapping': mapping}

class NumberReportingA(Page):
    form_model = 'group'
    form_fields = ['number_report_A']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [1, 2] and player.stage2_role == 'First'

    @staticmethod
    def vars_for_template(player: Player):
        mapping = ast.literal_eval(player.group.field_maybe_none('letter_number_mapping') or '{}' )
        return {'letter_number_mapping': mapping}

class WaitForA(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.set_stage2_payoffs()
    @staticmethod
    def is_displayed(player: Player):
        return player.stage2_role == 'Second'


class WaitForB(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.stage2_role == 'First'  # רק שחקן A ממתין

    @staticmethod

    def after_all_players_arrive(group: Group):
        group.set_stage2_payoffs()

class NumberReportingB(Page):
    form_model = 'group'
    form_fields = ['number_report_B']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [1, 2] and player.stage2_role == 'Second'

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'letter_number_mapping': ast.literal_eval(player.group.field_maybe_none('letter_number_mapping')),
            'player_a_report': player.group.number_report_A
        }

class Stage2Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [1, 2]

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {
            'number_report_A': group.number_report_A,
            'number_report_B': group.number_report_B,
            'is_matched': group.number_report_A == group.number_report_B,
            'player_payoff': player.payoff if player.round_number == 2 else 0,
        }

class Demographic(Page):
    form_model = 'player'
    form_fields = ['Age', 'Gender', 'feedback']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 2

class FinalPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        participation_fee = 2.50
        stage1_payoff = sum(
            p.total_payoff for p in player.in_all_rounds() if p.round_number == 1
        )
        stage2_payoff = player.payoff if player.round_number == 2 else 0
        total = participation_fee + stage1_payoff + stage2_payoff

        return {
            'participation_fee': participation_fee,
            'stage1_payoff': round(stage1_payoff, 2),
            'stage2_payoff': round(stage2_payoff, 2),
            'total_payoff': round(total, 2)
        }



page_sequence = [
    Instructions,
    WaitForPartner,
    TrustGame,
    WaitForReceiver,
    WaitForResults,
    Results,
    PartnerPreference,
    Intro2,
    NumberReportingA,
    WaitForA,
    NumberReportingB,
    WaitForB,
    Stage2Results,
    Demographic,
    FinalPage
]
