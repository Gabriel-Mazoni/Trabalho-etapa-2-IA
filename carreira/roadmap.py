"""Análise independente de competências e sequência de estudo."""
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Gap:
    name: str
    current: int
    target: int
    priority: int
    study: str

    @property
    def missing(self) -> int:
        return self.target - self.current


class RoadmapService:
    def gaps(self, track: dict, levels: Mapping[str, int]) -> list[Gap]:
        if set(levels) != {s['name'] for s in track['skills']}:
            raise ValueError('Informe o nível de todas as competências da trilha.')
        if any(type(v) is not int or not 0 <= v <= 5 for v in levels.values()):
            raise ValueError('Conhecimentos devem ser inteiros entre 0 e 5.')
        gaps = [Gap(s['name'], levels[s['name']], s['target'], s['priority'], s['study'])
                for s in track['skills'] if levels[s['name']] < s['target']]
        return sorted(gaps, key=lambda g: (g.priority, -g.missing, g.name))

    def readiness(self, track: dict, levels: Mapping[str, int]) -> float:
        self.gaps(track, levels)
        return round(100 * sum(min(levels[s['name']], s['target']) for s in track['skills'])
                     / sum(s['target'] for s in track['skills']), 2)
