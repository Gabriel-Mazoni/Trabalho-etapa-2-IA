# Bússola TI — Sistema Especialista de Carreiras

Trabalho da segunda etapa de Inteligência Artificial, Ciência da Computação / UNIPAC Barbacena. Implementação em Python 3.10+ de um consultor baseado em regras, soma ponderada e respostas graduais. A base de conhecimento é externa e editável, sem alterar o motor.

## Executar

Na pasta do repositório, crie um ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra o endereço local informado pelo Streamlit. Se a ativação estiver bloqueada pelo PowerShell, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e `.\.venv\Scripts\python.exe -m streamlit run app.py` diretamente.

## Como usar

1. **Perfil pessoal:** indique sua afinidade com comunicação e aprendizado contínuo.
2. **Afinidades técnicas:** responda sobre lógica, matemática, programação, dados, design, infraestrutura, segurança e qualidade.
3. **Objetivos de carreira:** avalie interesse no negócio e disponibilidade para incidentes/plantões.
4. **Resultado:** compare o Top 3 e o gráfico das dez trilhas. Escolha qualquer trilha para consultar justificativas e informe seu conhecimento atual. O sistema calcula as lacunas para júnior, ordena os estudos, sugere certificações e um projeto de portfólio. Baixe seu plano em JSON ou volte para revisar as respostas.

As respostas de afinidade vão de 1 (nenhuma) a 5 (muito alta). Conhecimento é avaliado separadamente, de 0 (não conheço) a 5 (avançado). Afinidade não deve ser confundida com experiência profissional.

## Trilhas atendidas

Back-end, Front-end/UX, Cientista de Dados, Engenheiro de Dados, Cibersegurança, DevOps/SRE, Cloud Architecture, Mobile, QA e Product Management. Cada trilha possui pesos próprios, penalidades, metas de competências, sequência de estudos, sugestões de certificação e projeto.

## Inferência e tratamento de incerteza

Para uma resposta `r` de 1 a 5, usamos a afinidade normalizada `a = (r - 1) / 4`. Para cada trilha:

```text
pontuação bruta = 100 × soma(peso × afinidade) / soma(pesos)
compatibilidade = limitar(pontuação bruta - penalidades, 0, 100)
```

O mínimo da escala representa afinidade zero; o máximo representa 100%. As penalidades do JSON são subtraídas em pontos percentuais quando uma resposta fica abaixo do limiar da regra. Exemplo: pesos 3 e 1, respostas 5 e 1 resultam em 75%; com uma penalidade de 12 pontos, o resultado é 63%.

O sistema mostra cada contribuição e cada penalidade aplicada. Respostas graduais representam a incerteza por graus de afinidade, sem pretender estimar probabilidades estatísticas. Não utiliza aprendizado de máquina nem fatores de certeza probabilísticos.

Empates na pontuação arredondada a duas casas usam o identificador da trilha em ordem alfabética para tornar o resultado reprodutível. O empate é informado; diferenças de até cinco pontos também recebem um aviso de proximidade. O percentual não é uma probabilidade de sucesso.

## Gaps e roadmap

Cada competência possui uma meta para júnior entre 1 e 5 e uma prioridade de estudo no JSON. A lacuna é `meta - nível atual`, somente quando positiva. O roadmap segue a prioridade curricular, depois o tamanho da lacuna e o nome. As competências já atendidas não aparecem como lacunas.

A cobertura para júnior é `100 × soma(min(nível atual, meta)) / soma(metas)`. Conhecimento acima da meta não compensa lacunas em outra competência. Atingir 100% significa atender às metas autodeclaradas desta base; não certifica senioridade. Certificações são sugestões genéricas e opcionais, sem pressupor que sejam gratuitas. O escopo é a preparação para júnior; não há classificação automática de pleno/sênior.

## Arquitetura e SOLID

```text
app.py                      Composição dos serviços e interface Streamlit
carreira/knowledge.py       Contrato da fonte e leitura/validação JSON
carreira/inference.py       Contrato da pontuação, soma ponderada e ranking
carreira/roadmap.py         Lacunas e cobertura das metas
 data/regras_carreiras.json  Perguntas, pesos, penalidades e recomendações
 tests/test_system.py       Testes do domínio e navegação da interface
```

- **S — Responsabilidade única:** carregamento, pontuação, roadmap e apresentação ficam em componentes separados.
- **O — Aberto/fechado:** novas trilhas são adicionadas ao JSON; outra estratégia de pontuação pode implementar `ScoringPolicy` sem mudar o consultor.
- **L — Substituição de Liskov:** fontes e políticas alternativas devem respeitar os contratos `load()` e `score()`, retornando a mesma estrutura esperada pelos consumidores.
- **I — Segregação de interfaces:** os protocolos expõem somente uma operação cada; o motor não depende de funções de interface ou de persistência de relatórios.
- **D — Inversão de dependência:** `CareerAdvisor` recebe `KnowledgeSource` e `ScoringPolicy` por injeção; `app.py` escolhe as implementações concretas.

## Editar a base de conhecimento

Em `data/regras_carreiras.json`, `questions` define identificador, texto e etapa de cada pergunta. `tracks` define identificador, nome, `weights`, `penalties`, `skills`, `certifications` e `project`. Os pesos devem ser positivos e referenciar perguntas existentes. Competências possuem nome único na trilha, meta de 1 a 5, prioridade e orientação de estudo. As regras são recarregadas nas execuções da interface.

Para manter o wizard, use as etapas `Perfil pessoal`, `Afinidades técnicas` e `Objetivos de carreira`. Perguntas podem ser irrelevantes para uma trilha e, nesse caso, não precisam estar em seus pesos. Aprendizado contínuo é coletado como contexto e não influencia a pontuação atual. Os pesos e metas são uma modelagem didática, sem validação empírica com profissionais; podem ser revisados pelo professor/especialista.

## Testes

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

A suíte verifica os extremos da escala, empates estáveis, perfil misto de dados e web, cálculo manual das penalidades, respostas inválidas/incompletas, base com pesos inválidos, ausência/presença de gaps e navegação pelas etapas do Streamlit com troca de trilha e retorno. Não requer servidor nem navegador externo.

## Correspondência com o enunciado

| Requisito | Implementação |
| --- | --- |
| Engenharia de conhecimento das dez trilhas | JSON externo com pesos e regras específicas |
| Respostas graduais | Sliders Likert de 1 a 5 |
| Ranking e Top 3 percentual | Motor ponderado, métricas, tabela e gráfico de barras |
| Perfis conflitantes | Penalidades lógicas explicadas por trilha |
| Conhecimento atual e metas júnior | Sliders de 0 a 5 e análise por competência |
| Roadmap individualizado | Apenas lacunas, prioridade, certificações e projeto |
| Interface por etapas | Wizard com retorno e preservação das respostas |
| Robustez e casos limite | Testes automatizados de domínio e interface |
| Separação e SOLID | Serviços com contratos e injeção de dependências |

## Privacidade e limites

Não há coleta de nome, login ou envio de respostas a serviços externos no código da aplicação. As respostas ficam na sessão do Streamlit; o arquivo JSON só é baixado quando solicitado. O perfil é autodeclarado e serve como apoio à exploração de carreira. Pesos, metas e projetos são educacionais, não substituem avaliação de um profissional ou análise de vagas reais.
