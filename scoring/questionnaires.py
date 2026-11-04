"""Developers' questionnaire answers (Q3-Q9), one dict per service.

The answers are confidential and not part of this repository. This file keeps
the structure the scorer expects, so that score_a.py can be read and run on
another system's data. In the original analysis each list held the answers
transcribed verbatim from the five answered questionnaires (typos and
duplicated rows kept; the scorer removes duplicates).

Q3: (endpoint, [callers])        Q4: (endpoint, provider)
Q5: (topic, [consumers])         Q6: (topic, [producers])
Q7: (name, type, role, actions, [shared by])
Q8: [services]                   Q9: [components]
"""

def _empty():
    return {"q3": [], "q4": [], "q5": [], "q6": [], "q7": [], "q8": [], "q9": []}


SERVICES = ["payin-processor", "credit-card-processor", "agents-commissions", "bank-interface", "payout-processor"]
ALL = {s: _empty() for s in SERVICES}
