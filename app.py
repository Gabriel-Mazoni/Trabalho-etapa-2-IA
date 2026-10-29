"""Ponto de composição: Streamlit conecta infraestrutura e serviços."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from carreira.inference import CareerAdvisor, WeightedScoring
from carreira.knowledge import JsonKnowledgeSource
from carreira.roadmap import RoadmapService

st.set_page_config(page_title='Bússola TI', page_icon='🧭', layout='wide')
st.title('Bússola TI · Consultor de carreiras')
st.caption('Descubra afinidades, compare dez trilhas e construa seu plano para o nível júnior.')
try:
    advisor = CareerAdvisor(JsonKnowledgeSource(Path(__file__).parent / 'data/regras_carreiras.json'), WeightedScoring())
except (ValueError, KeyError, OSError) as exc:
    st.error(f'Não foi possível carregar a base de conhecimento: {exc}')
    st.stop()
roadmap = RoadmapService()
st.session_state.setdefault('step', 0)
st.session_state.setdefault('answers', {})
stages = ['Perfil pessoal', 'Afinidades técnicas', 'Objetivos de carreira', 'Resultado e plano']
step = st.session_state.step
st.progress((step + 1) / len(stages), text=f'Passo {step + 1} de 4: {stages[step]}')
if step < 3:
    st.subheader(stages[step])
    st.info('Escala de afinidade: 1 = nenhuma · 2 = pouca · 3 = moderada · 4 = alta · 5 = muito alta.')
    with st.form(f'stage_{step}'):
        values = {}
        for q in advisor.base['questions']:
            if q['stage'] == stages[step]:
                values[q['id']] = st.slider(q['label'], 1, 5, st.session_state.answers.get(q['id'], 3), key=f"answer_{q['id']}")
        back, forward = st.columns(2)
        previous = back.form_submit_button('Voltar', disabled=step == 0)
        advance = forward.form_submit_button('Ver resultado' if step == 2 else 'Continuar', type='primary')
        if previous or advance:
            st.session_state.answers.update(values)
            st.session_state.step += -1 if previous else 1
            st.rerun()
else:
    ranking = advisor.rank(st.session_state.answers)
    st.subheader('Suas três maiores compatibilidades')
    for col, result in zip(st.columns(3), ranking[:3]):
        col.metric(result.track['name'], f'{result.percentage:.1f}%')
    if ranking[0].percentage == ranking[1].percentage:
        st.info('Há empate na maior pontuação. A ordem usa o identificador da trilha como desempate estável; explore ambas.')
    elif ranking[0].percentage - ranking[1].percentage <= 5:
        st.info('As primeiras trilhas estão próximas (até 5 pontos). Compare os projetos e as competências antes de escolher.')
    st.caption('Compatibilidade representa afinidade ponderada, não probabilidade de sucesso ou garantia de contratação.')
    table = pd.DataFrame([{'Trilha':r.track['name'], 'Compatibilidade (%)':r.percentage} for r in ranking])
    st.bar_chart(table.set_index('Trilha'), horizontal=True)
    st.dataframe(table, hide_index=True, use_container_width=True)
    selected = st.selectbox('Escolha uma trilha para explorar', [r.track['id'] for r in ranking], format_func=lambda ident: next(r.track['name'] for r in ranking if r.track['id'] == ident))
    result = next(r for r in ranking if r.track['id'] == selected)
    with st.expander('Como esta pontuação foi calculada?'):
        labels = {q['id']:q['label'] for q in advisor.base['questions']}
        st.write(f'Pontuação antes das penalidades: {result.raw_percentage:.2f}%.')
        st.dataframe(pd.DataFrame([{'Afinidade':labels[q], 'Contribuição (p.p.)':round(v, 2)} for q,v in result.contributions.items()]), hide_index=True)
        for reason in result.penalties:
            st.write(reason)
        if not result.penalties:
            st.write('Nenhuma penalidade aplicada.')
    st.subheader('Conhecimento atual e lacunas para júnior')
    st.caption('0 = não conheço · 1 = contato inicial · 2 = básico · 3 = aplico com apoio · 4 = autonomia · 5 = avançado.')
    levels = {s['name']:st.slider(s['name'], 0, 5, 0, key=f"skill_{selected}_{s['name']}") for s in result.track['skills']}
    gaps = roadmap.gaps(result.track, levels)
    st.metric('Cobertura das competências júnior da base', f'{roadmap.readiness(result.track, levels):.1f}%')
    st.caption('A avaliação é autodeclarada e relativa a esta base; não determina senioridade profissional.')
    st.subheader('Seu roadmap')
    for n,gap in enumerate(gaps, 1):
        st.markdown(f'**{n}. {gap.name}** — nível atual {gap.current}, meta {gap.target}, lacuna {gap.missing}.\n\n{gap.study}')
    if not gaps:
        st.success('Você atingiu as metas júnior desta base. Consolide o conhecimento no projeto e peça revisão de código.')
    st.markdown('**Certificações sugeridas** (opcionais; consulte o programa e os custos do provedor):')
    for certification in result.track['certifications']:
        st.write(f'• {certification}')
    st.markdown(f"**Projeto de portfólio:** {result.track['project']}")
    st.write('Publique no GitHub com README, instruções de execução, testes e decisões técnicas. Nunca publique credenciais.')
    report = {'trilha':result.track['name'], 'compatibilidade':result.percentage, 'niveis':levels, 'lacunas':[g.__dict__ for g in gaps], 'certificacoes':result.track['certifications'], 'projeto':result.track['project'], 'respostas':st.session_state.answers}
    st.download_button('Baixar plano em JSON', json.dumps(report, ensure_ascii=False, indent=2), 'plano_carreira.json', 'application/json')
    if st.button('Revisar respostas'):
        st.session_state.step = 0
        st.rerun()
