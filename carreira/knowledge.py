"""Carregamento e validação da base externa de conhecimento."""
import json
import math
from pathlib import Path
from typing import Protocol


class KnowledgeSource(Protocol):
    def load(self) -> dict: ...


class JsonKnowledgeSource:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict:
        base = json.loads(self.path.read_text(encoding='utf-8'))
        questions = base['questions']
        ids = {q['id'] for q in questions}
        if not ids or len(ids) != len(questions):
            raise ValueError('Perguntas vazias ou duplicadas.')
        tracks = base['tracks']
        if not tracks or len({t['id'] for t in tracks}) != len(tracks):
            raise ValueError('Trilhas vazias ou duplicadas.')
        for track in tracks:
            weights = track['weights']
            if not weights or not set(weights) <= ids:
                raise ValueError('Pesos referenciam perguntas inválidas.')
            if any(type(w) not in (int, float) or not math.isfinite(w) or w <= 0 for w in weights.values()):
                raise ValueError('Pesos devem ser positivos e finitos.')
            skills = track['skills']
            if not skills or len({s['name'] for s in skills}) != len(skills):
                raise ValueError('Competências vazias ou duplicadas.')
            for skill in skills:
                if type(skill['target']) is not int or not 1 <= skill['target'] <= 5 or skill['priority'] < 1:
                    raise ValueError('Meta ou prioridade inválida.')
            for rule in track['penalties']:
                if rule['question'] not in ids or not 1 <= rule['below'] <= 5 or not 0 <= rule['points'] <= 100:
                    raise ValueError('Penalidade inválida.')
        return base
