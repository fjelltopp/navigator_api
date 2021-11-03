import random
from random import randint
from lorem import get_sentence, get_word

possible_milestones = [
    "Generate Data",
    "Spectrum Prep",
    "ADR Prep",
    "Shiny90",
    "Naomi Prep",
    "Naomi"
]

possible_tasks = [
    "Generate input data",
    "Go to Spectrum/AIM. Row 34",
    "Download data templates from ADR",
    "Populate Shiny90 survey template",
    "Populate Shiny90 HIV testing template",
    "Populate the Population template",
    "Populate ANC survey template",
    "Populate ART template",
    "Populate Naomi survey template",
    "Populate geo template",
    "Create user account",
]


def id():
    return random.getrandbits(5)


def milestone():
    return possible_milestones[
        randint(0, len(possible_milestones) - 1)
    ]


def boolean():
    return bool(randint(0, 1))


def html():
    task_name = possible_tasks[
        randint(0, len(possible_tasks) - 1)
    ]
    list_items = ('').join([
        f'<li>{get_sentence(count=(1, 3))}</li>'
        for x in range(randint(1, 7))
    ])
    html = ''.join([
        f'<h3>{task_name}</h3>',
        f'<p>{get_sentence(count=(1, 3))}</p>',
        f'<ol>{list_items}</ol>'
    ])
    return html


def actionable_links():
    return [
        {
            'label': possible_tasks[
                randint(0, len(possible_tasks) - 1)
            ],
            'link': 'http://example.com'
        }
        for x in range(randint(0, 3))
    ]
