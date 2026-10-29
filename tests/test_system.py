from copy import deepcopy
from pathlib import Path
import json
import pytest
from carreira.inference import CareerAdvisor, WeightedScoring
from carreira.knowledge import JsonKnowledgeSource
from carreira.roadmap import RoadmapService

@pytest.fixture
def advisor():
    return CareerAdvisor(JsonKnowledgeSource(Path('data/regras_carreiras.json')), WeightedScoring())

def answers(advisor, value):
    return {q['id']: value for q in advisor.base['questions']}

@pytest.mark.parametrize('value,expected', [(1,0),(5,100)])
def test_extremes(advisor, value, expected):
    ranked = advisor.rank(answers(advisor, value))
    assert len(ranked) == 10
    assert all(r.percentage == expected for r in ranked)

def test_tie_is_stable(advisor):
    ranked = advisor.rank(answers(advisor, 3))
    assert all(r.percentage == 50 for r in ranked)
    assert [r.track['id'] for r in ranked] == sorted(r.track['id'] for r in ranked)

@pytest.mark.parametrize('value', [0,6,True,2.5,float('nan')])
def test_invalid_answer(advisor, value):
    with pytest.raises(ValueError):
        advisor.rank(answers(advisor, value))

def test_missing_answer(advisor):
    with pytest.raises(ValueError): advisor.rank({})

def test_weighted_formula_and_penalty():
    track = {'weights':{'a':3,'b':1}, 'penalties':[{'question':'b','below':3,'points':12,'reason':'conflito'}]}
    result = WeightedScoring().score(track, {'a':5,'b':1})
    assert result.raw_percentage == 75
    assert result.percentage == 63
    assert len(result.penalties) == 1

def test_ambiguous_profile(advisor):
    profile = answers(advisor, 3)
    profile.update(codigo=5, dados=5, matematica=5, visual=5)
    result = advisor.rank(profile)
    assert result[0].track['id'] == 'ciencia'
    assert all(0 <= r.percentage <= 100 for r in result)
    assert any(r.track['id'] == 'frontend' for r in result[:3])

def test_gaps_and_readiness(advisor):
    track = advisor.base['tracks'][0]
    service = RoadmapService()
    levels = {s['name']:0 for s in track['skills']}
    assert len(service.gaps(track, levels)) == len(levels)
    assert service.readiness(track, levels) == 0
    levels = {s['name']:5 for s in track['skills']}
    assert service.gaps(track, levels) == []
    assert service.readiness(track, levels) == 100
    with pytest.raises(ValueError): service.gaps(track, {})
    with pytest.raises(ValueError): service.gaps(track, {s:6 for s in levels})

def test_invalid_knowledge(tmp_path, advisor):
    base = deepcopy(advisor.base)
    base['tracks'][0]['weights']['logica'] = -1
    path = tmp_path / 'base.json'
    path.write_text(json.dumps(base), encoding='utf-8')
    with pytest.raises(ValueError): JsonKnowledgeSource(path).load()

def test_wizard():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path('app.py').resolve()), default_timeout=20).run()
    assert not app.exception
    for _ in range(3):
        app.button[1].click().run()
        assert not app.exception
    assert len(app.metric) == 4
    app.slider[0].set_value(5).run()
    assert not app.exception
    app.selectbox[0].select('qa').run()
    assert not app.exception
    app.button[-1].click().run()
    assert len(app.slider) == 2


