import re
from typing import List

from cryptomonitor.database import models


def match_rules(match_rules: List[models.Rule], body: str) -> List[models.Rule]:
    matching_rules: List[models.Rule] = []
    for rule in match_rules:
        if re.match(rule.pattern, body):
            matching_rules.append(rule)
    return matching_rules
