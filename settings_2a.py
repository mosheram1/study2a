from os import environ
INSTALLED_APPS = [
    'otree',
    'otree.extra_template_filters',
    'TASKA.filters'
]

# TODO - TB: how do you prevent duplicates?
SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=0.1, participation_fee=0, mturk_hit_settings={
    'keywords' : ['bonus, study'],
    'title' : 'Decision Making Exp',
    'description' : 'Bargaining and a Guessing task',
    'frame_height' : 500,
    'template' : 'global/mturk_template.html',
    'minutes_allotted_per_assignment' : 45,
    'expiration_hours' : 7 * 24,
    'qualification_requirements' : [        
        # Only US
        {
            'QualificationTypeId': "00000000000000000071",
            'Comparator': "EqualTo",
            'LocaleValues': [{'Country': "US"}]
        },
        # At least 50 HITs approved
        {
            'QualificationTypeId': "00000000000000000040",
            'Comparator': "GreaterThanOrEqualTo",
            'IntegerValues': [50]
        },

        ]
  })
SESSION_CONFIGS = [
    dict(name='Bargaining_and_morality', num_demo_participants=None, app_sequence=['bargaining_and_morality_Study2'])]
    #dict(name='Bargaining_and_morality', num_demo_participants=None,app_sequence=['bargaining_and_morality_Study2', 'Intro', 'bargaining_and_morality_Study1b', 'Results'])]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = [
    'excluded', 'unmatched', 'wait_page_arrival'
]
SESSION_FIELDS = []
ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = 'blahblah'

AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
