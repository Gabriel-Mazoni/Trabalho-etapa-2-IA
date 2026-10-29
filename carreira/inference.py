"""Soma ponderada explicável e política substituível de pontuação."""
from dataclasses import dataclass
from typing import Mapping, Protocol
from carreira.knowledge import KnowledgeSource


@dataclass(frozen=True)
class Result:
    track: dict
    percentage: float
    raw_percentage: float
    penalties: tuple[str, ...]
    contributions: dict[str, float]


class ScoringPolicy(Protocol):
    def score(self, track: dict, answers: Mapping[str, int]) -> Result: ...


class WeightedScoring:
    def score(self, track: dict, answers: Mapping[str, int]) -> Result:
        total = sum(track['weights'].values())
        contributions = {q: 100 * w * (answers[q] - 1) / (4 * total)
                         for q, w in track['weights'].items()}
        raw = sum(contributions.values())
        rules = [r for r in track['penalties'] if answers[r['question']] < r['below']]
        penalty = sum(r['points'] for r in rules)
        return Result(track, round(max(0, min(100, raw - penalty)), 2),
                      round(raw, 2), tuple(f"{r['reason']} (-{r['points']} p.p.)" for r in rules),
                      contributions)


class CareerAdvisor:
    def __init__(self, source: KnowledgeSource, scoring: ScoringPolicy):
        self.base = source.load()
        self.scoring = scoring

    def rank(self, answers: Mapping[str, int]) -> list[Result]:
        required = {q['id'] for q in self.base['questions']}
        if set(answers) != required:
            raise ValueError('Responda exatamente todas as perguntas do perfil.')
        if any(type(v) is not int or not 1 <= v <= 5 for v in answers.values()):
            raise ValueError('Respostas devem ser inteiros entre 1 e 5.')
        results = [self.scoring.score(t, answers) for t in self.base['tracks']]
        return sorted(results, key=lambda r: (-r.percentage, r.track['id']))
