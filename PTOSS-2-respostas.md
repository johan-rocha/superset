# PTOSS-2: Testes Unitários

## 1. Introdução

Este relatório documenta a atividade PTOSS-2 da disciplina FGA0314 - Testes de
Software. O trabalho foi realizado sobre o Apache Superset, com foco em testes
unitários de funções reais do backend Python.

A equipe possui 6 integrantes. Por isso, foram selecionados 6 métodos/funções
com decisões compostas, permitindo aplicar MC/DC em todos eles.

| Integrante | Responsabilidade principal |
| --- | --- |
| Integrante 1 | `get_current_user` |
| Integrante 2 | `get_dev_env_label` |
| Integrante 3 | `user_label` |
| Integrante 4 | `split` |
| Integrante 5 | `check_for_oauth2` |
| Integrante 6 | `ScreenshotCachePayload.should_trigger_task` |

## 2. Descrição do projeto

O Apache Superset é uma plataforma de visualização de dados de código aberto.
O backend é implementado em Python/Flask e o frontend em React/TypeScript.

Nesta atividade, a análise foi concentrada em funções utilitárias do backend,
pois elas possuem entradas e saídas bem definidas e permitem testes unitários
sem depender diretamente de interface gráfica.

Arquivos envolvidos:

| Arquivo | Papel no projeto |
| --- | --- |
| `superset/utils/core.py` | Utilitários centrais do backend |
| `superset/utils/oauth2.py` | Fluxo auxiliar de OAuth2 |
| `superset/utils/screenshots.py` | Controle de payload/cache de screenshots |
| `superset/tasks/utils.py` | Utilitários para execução de tarefas assíncronas |
| `superset/utils/version.py` | Metadados de versão/ambiente de desenvolvimento |
| `superset/utils/urls.py` | Manipulação de URLs, usada na parte de TDD |

## 3. Planejamento dos testes

A seleção foi refeita para atender ao requisito de MC/DC: todos os 6 métodos
testados possuem ao menos uma decisão composta com duas ou mais condições
atômicas.

Critérios usados:

| Critério | Aplicação |
| --- | --- |
| Particionamento de equivalência | Usuário autenticado/anônimo/ausente, ambiente com branch/SHA, usuário completo/incompleto, estados de cache |
| Análise de valor limite | `None`, string vazia, item sem delimitador, imagem ausente, SHA truncado |
| Cobertura de branches | Caminhos verdadeiro/falso das decisões |
| MC/DC | Cada condição atômica foi variada para demonstrar impacto independente na decisão |
| TDD | Aplicado separadamente em `modify_url_query` |

## 4. Descrição das técnicas utilizadas

Foram usadas técnicas de caixa-preta e caixa-branca de forma complementar.
Caixa-preta orientou a escolha das classes de entrada e saídas esperadas sem
depender da implementação. Caixa-branca orientou a seleção dos métodos e a
variação das condições internas, especialmente nos casos de MC/DC.

As principais técnicas aplicadas foram:

| Técnica | Uso na atividade |
| --- | --- |
| Particionamento de equivalência | Separação de entradas válidas, ausentes, incompletas e estados distintos |
| Análise de valor limite | Uso de `None`, strings vazias, SHA truncado, delimitador ausente e imagem ausente |
| Cobertura de branches | Exercício dos caminhos verdadeiro e falso das decisões relevantes |
| MC/DC | Variação independente de cada condição atômica em decisões compostas |
| TDD | Criação de testes antes da correção em `modify_url_query` |

## 5. Métodos selecionados para MC/DC

| ID | Função/método | Decisão composta analisada |
| --- | --- | --- |
| M1 | `get_current_user` | `hasattr(g, "user") and g.user`; `user and not user.is_anonymous` |
| M2 | `get_dev_env_label` | `branch and sha` |
| M3 | `user_label` | `user.first_name and user.last_name` |
| M4 | `split` | `parens == 0 and not quotes and character == delimiter` |
| M5 | `check_for_oauth2` | `database.is_oauth2_enabled() and database.db_engine_spec.needs_oauth2(ex)` |
| M6 | `ScreenshotCachePayload.should_trigger_task` | combinação de `or` com subdecisões `and` por estado |

### Mapeamento método -> arquivo

| Método/função | Arquivo |
| --- | --- |
| `get_current_user` | `superset/tasks/utils.py` |
| `get_dev_env_label` | `superset/utils/version.py` |
| `user_label` | `superset/utils/core.py` |
| `split` | `superset/utils/core.py` |
| `check_for_oauth2` | `superset/utils/oauth2.py` |
| `ScreenshotCachePayload.should_trigger_task` | `superset/utils/screenshots.py` |
| `modify_url_query` | `superset/utils/urls.py` |

## 6. Testes desenvolvidos

Arquivo principal criado:

```text
tests/unit_tests/utils/ptoss_unitarios_test.py
```

Também foram adicionados testes de TDD em:

```text
tests/unit_tests/utils/urls_tests.py
```

Também foi criado um teste em formato compatível com PR upstream:

```text
tests/unit_tests/utils/version_tests.py
```

### M1 - `get_current_user`

Objetivo: obter o username do usuário atual associado ao contexto de execução,
retornando `None` quando não houver usuário ou quando ele for anônimo.

Decisão 1:

```python
hasattr(g, "user") and g.user
```

Casos MC/DC:

| Caso | Estado de `g` | C1: possui `user` | C2: `g.user` é verdadeiro | Decisão | Esperado |
| --- | --- | --- | --- | --- | --- |
| CT1 | sem atributo `user` | F | - | F | `None` |
| CT2 | `user=None` | T | F | F | `None` |
| CT3 | usuário ativo | T | T | T | `"admin"` |

CT1/CT3 mostram o efeito de C1. CT2/CT3 mostram o efeito de C2.

Decisão 2:

```python
user and not user.is_anonymous
```

| Caso | Usuário | C1: `user` verdadeiro | C2: não anônimo | Decisão | Esperado |
| --- | --- | --- | --- | --- | --- |
| CT4 | usuário ativo | T | T | T | `"admin"` |
| CT5 | usuário anônimo | T | F | F | `None` |
| CT6 | usuário ausente | F | - | F | `None` |

CT4/CT5 mostram o efeito de `not user.is_anonymous`. CT4/CT6 mostram o efeito
da presença do usuário.

### M2 - `get_dev_env_label`

Objetivo: montar o rótulo de ambiente de desenvolvimento a partir da branch e
do SHA disponíveis.

Decisão:

```python
branch and sha
```

| Caso | Branch | SHA | C1: branch presente | C2: SHA presente | Decisão | Esperado |
| --- | --- | --- | --- | --- | --- | --- |
| CT7 | `"feature/mcdc"` | `"abcdef1234567890"` | T | T | T | `"feature/mcdc@abcdef12"` |
| CT8 | `None` | `"abcdef1234567890"` | F | T | F | `"@abcdef12"` |
| CT9 | `"feature/mcdc"` | `None` | T | F | F | `"feature/mcdc"` |

CT7/CT8 mostram o efeito independente de C1. CT7/CT9 mostram o efeito
independente de C2. O SHA também cobre o valor limite de truncamento para 8
caracteres.

#### Testes existentes

Não foi encontrado teste unitário direto para `get_dev_env_label`. O arquivo
existente de versionamento (`superset/utils/version.py`) era exercitado
indiretamente por outros fluxos, mas sem validar explicitamente a formação do
rótulo de ambiente de desenvolvimento.

#### Projeto dos Casos de Testes

O teste foi projetado para ser reaproveitável como PR apenas de teste no
Superset oficial, sem depender da atividade PTOSS. Por isso, ele foi colocado em
`tests/unit_tests/utils/version_tests.py`, com nome e estrutura compatíveis com a
suíte unitária existente.

#### Testes Caixa-Preta

##### Particionamento de Equivalência

| Classe | Entrada representativa | Saída esperada |
| --- | --- | --- |
| Branch e SHA disponíveis | branch local + SHA local | `"branch@sha8"` |
| Apenas SHA disponível | sem branch + SHA local | `"@sha8"` |
| Apenas branch disponível | branch local + sem SHA | `"branch"` |
| Nenhuma informação disponível | sem branch + sem SHA | `""` |
| Ambiente GitHub Actions | `GITHUB_HEAD_REF` + `GITHUB_SHA` | usa variáveis de ambiente |

##### Análise de Valor Limite

| Valor limite | Justificativa | Esperado |
| --- | --- | --- |
| SHA maior que 8 caracteres | A função deve truncar o SHA para exibição curta | primeiros 8 caracteres |
| Branch `None` | Ausência de branch deve cair no formato com apenas SHA | `"@sha8"` |
| SHA `None` | Ausência de SHA deve retornar apenas branch | `"branch"` |
| Branch e SHA `None` | Ausência total de dados deve retornar string vazia | `""` |

#### Testes Caixa-Branca

##### Tabela MC/DC

Decisão analisada:

```python
branch and sha
```

| Caso | C1: branch presente | C2: SHA presente | Decisão | Resultado |
| --- | --- | --- | --- | --- |
| V1 | T | T | T | `"feature/version-label@abcdef12"` |
| V2 | F | T | F | `"@abcdef12"` |
| V3 | T | F | F | `"feature/version-label"` |
| V4 | F | F | F | `""` |

V1/V2 demonstram o efeito independente de `branch`. V1/V3 demonstram o efeito
independente de `sha`.

##### Cobertura Estrutural

O teste cobre os ramos principais de `get_dev_env_label`: branch com SHA, apenas
SHA, apenas branch, ausência de ambos e precedência das variáveis de ambiente do
GitHub Actions sobre os valores locais.

#### Implementação dos Testes

Foram implementados:

```text
test_get_dev_env_label_formats_branch_and_sha
test_get_dev_env_label_prefers_github_environment
```

O primeiro teste usa parametrização para cobrir as classes de equivalência. O
segundo valida a regra de precedência entre variáveis de ambiente e fallback
local.

#### Resultado da Execução e Cobertura

O arquivo `tests/unit_tests/utils/version_tests.py` foi incluído no workflow
`PTOSS Backend Tests`, tanto na checagem sintática quanto na execução com
cobertura. O relatório final deve ser consultado no artefato
`ptoss-coverage-reports` após a próxima execução do GitHub Actions.

### M3 - `user_label`

Objetivo: montar o nome exibido de um usuário usando nome e sobrenome quando
ambos existem; caso contrário, usar `username`.

Decisão:

```python
user.first_name and user.last_name
```

| Caso | `first_name` | `last_name` | Decisão | Esperado |
| --- | --- | --- | --- | --- |
| CT11 | `"Ada"` | `"Lovelace"` | T | `"Ada Lovelace"` |
| CT12 | `"Ada"` | `""` | F | `"ada"` |
| CT13 | `""` | `"Lovelace"` | F | `"ada"` |
| CT14 | usuário `None` | - | branch externo | `None` |

CT11/CT12 mostram o efeito independente de `last_name`. CT11/CT13 mostram o
efeito independente de `first_name`.

### M4 - `split`

Objetivo: separar strings respeitando delimitadores dentro de aspas e
parênteses.

Decisão analisada:

```python
complete and character == delimiter
```

Onde:

```python
complete = parens == 0 and not quotes
```

Decisão expandida para MC/DC:

```text
parens == 0 and not quotes and character == delimiter
```

| Caso | Entrada | C1: fora de parênteses | C2: fora de aspas | C3: caractere delimitador | Esperado |
| --- | --- | --- | --- | --- | --- |
| CT15 | `"a,b"` | T | T | T | `["a", "b"]` |
| CT16 | `"func(a,b),c"` | F no delimitador interno | T | T | `["func(a,b)", "c"]` |
| CT17 | `"\"a,b\",c"` | T | F no delimitador interno | T | `["\"a,b\"", "c"]` |
| CT18 | `"abc"` | T | T | F | `["abc"]` |

Os casos variam cada condição mantendo as demais sob controle para mostrar se o
delimitador é aceito ou ignorado.

### M5 - `check_for_oauth2`

Objetivo: detectar se uma falha de banco exige início do fluxo OAuth2.

Decisão:

```python
database.is_oauth2_enabled() and database.db_engine_spec.needs_oauth2(ex)
```

| Caso | OAuth2 habilitado | Exceção exige OAuth2 | Decisão | Esperado |
| --- | --- | --- | --- | --- |
| CT19 | T | T | T | chama `start_oauth2_dance` |
| CT20 | F | T | F | não chama |
| CT21 | T | F | F | não chama |

CT19/CT20 mostram o efeito independente da primeira condição. CT19/CT21 mostram
o efeito independente da segunda.

### M6 - `ScreenshotCachePayload.should_trigger_task`

Objetivo: decidir se uma tarefa de screenshot deve ser disparada a partir do
estado do cache.

Decisão:

```python
force
or self.status == StatusValues.PENDING
or (self.status == StatusValues.ERROR and self.is_error_cache_ttl_expired())
or (self.status == StatusValues.COMPUTING and self.is_computing_stale())
or (self.status == StatusValues.UPDATED and self._image is None)
```

Casos MC/DC principais:

| Caso | Situação | Decisão esperada |
| --- | --- | --- |
| CT22 | `UPDATED` com imagem, `force=False` | F |
| CT23 | mesmo estado, `force=True` | T |
| CT24 | `PENDING` | T |
| CT25 | `ERROR` com TTL expirado | T |
| CT26 | `ERROR` sem TTL expirado | F |
| CT27 | `COMPUTING` obsoleto | T |
| CT28 | `COMPUTING` não obsoleto | F |
| CT29 | `UPDATED` sem imagem | T |

O baseline CT22 deixa os termos da decisão falsos. Os demais casos ativam uma
condição ou subdecisão específica, permitindo observar seu efeito no resultado.

## 7. Integração entre caixa-preta e caixa-branca

A caixa-preta definiu classes de entrada com base no comportamento esperado:
usuário autenticado/anônimo/ausente, ambiente com branch/SHA, usuário
completo/incompleto, estados de cache e falha OAuth2.

A caixa-branca complementou essa visão ao revelar os predicados internos que
precisavam ser cobertos por MC/DC. Sem a leitura do código, seria fácil testar
apenas casos comuns e deixar sem cobertura condições como usuário anônimo,
usuário ausente, delimitador dentro de aspas ou `ERROR` sem TTL expirado.

| Lacuna funcional | Complemento estrutural |
| --- | --- |
| Usuário autenticado seria testado, mas usuário anônimo poderia ser tratado errado | MC/DC variou presença de `g.user` e `is_anonymous` |
| Ter apenas branch ou apenas SHA muda o rótulo do ambiente | MC/DC variou branch e SHA separadamente |
| Separar string por vírgula não cobre aspas e parênteses | MC/DC incluiu vírgula dentro de aspas e parênteses |
| Testar usuário completo não cobre fallback para `username` | MC/DC variou nome e sobrenome |
| Testar OAuth2 habilitado não cobre exceção que não exige OAuth2 | MC/DC variou a resposta de `needs_oauth2` |
| Testar cache pendente não cobre estados `ERROR`, `COMPUTING` e `UPDATED` | MC/DC ativou cada termo da decisão |

## 8. Rastreabilidade

| Funcionalidade | Função/método | Teste |
| --- | --- | --- |
| Resolução do usuário atual | `get_current_user` | `test_get_current_user_mcdc_user_presence_decision` e `test_get_current_user_mcdc_anonymous_user_decision` |
| Rótulo de ambiente de desenvolvimento | `get_dev_env_label` | `test_get_dev_env_label_mcdc_branch_and_sha_decision`, `test_get_dev_env_label_formats_branch_and_sha` e `test_get_dev_env_label_prefers_github_environment` |
| Label de usuário | `user_label` | `test_user_label_mcdc_full_name_decision` |
| Split respeitando contexto | `split` | `test_split_mcdc_delimiter_decision` |
| Detecção de OAuth2 | `check_for_oauth2` | `test_check_for_oauth2_mcdc_decision` |
| Disparo de tarefa de screenshot | `ScreenshotCachePayload.should_trigger_task` | `test_screenshot_payload_should_trigger_task_mcdc_decision` |
| Melhoria por TDD | `modify_url_query` | `test_modify_url_query_preserves_repeated_existing_parameters` e `test_modify_url_query_adds_list_values_as_repeated_parameters` |

## 9. Métricas e evidências de cobertura

Foi realizada checagem sintática dos arquivos alterados:

```bash
python3 -m py_compile superset/utils/urls.py tests/unit_tests/utils/conftest.py tests/unit_tests/utils/urls_tests.py tests/unit_tests/utils/version_tests.py tests/unit_tests/utils/ptoss_unitarios_test.py
```

Resultado: comando executado com sucesso.

Os testes não puderam ser executados neste ambiente porque as dependências de
desenvolvimento do Superset não estão instaladas:

```text
/usr/bin/python3: No module named pytest
ModuleNotFoundError: No module named 'werkzeug'
ModuleNotFoundError: No module named 'coverage'
/bin/bash: line 1: pre-commit: command not found
```

O health check do Superset também falhou porque o servidor local não estava em
execução:

```bash
curl -f http://localhost:8088/health
```

Resultado:

```text
Failed to connect to localhost port 8088
```

No GitHub Actions, o workflow `.github/workflows/ptoss-backend-tests.yml`
executa os testes da atividade com cobertura. A cobertura pode ser consultada
em três lugares:

| Local | Evidência |
| --- | --- |
| Log do job | Saída `term-missing` do `pytest-cov` |
| Resumo da execução | Bloco `PTOSS coverage` no `Summary` da run |
| Artefatos | `ptoss-coverage-reports`, contendo `coverage.xml` e `htmlcov/` |

Para baixar o relatório HTML: GitHub > repositório > Actions > execução
`PTOSS Backend Tests` > seção `Artifacts` > `ptoss-coverage-reports`. Depois,
abra `htmlcov/index.html`.

Resultado obtido no GitHub Actions na execução anterior:

| Arquivo | Stmts | Miss | Branch | BrPart | Cobertura |
| --- | ---: | ---: | ---: | ---: | ---: |
| `superset/tasks/utils.py` | 123 | 92 | 70 | 0 | 17% |
| `superset/utils/core.py` | 929 | 587 | 324 | 1 | 29% |
| `superset/utils/oauth2.py` | 113 | 59 | 20 | 0 | 42% |
| `superset/utils/screenshots.py` | 201 | 118 | 24 | 0 | 37% |
| `superset/utils/urls.py` | 32 | 15 | 10 | 0 | 50% |
| `superset/utils/version.py` | 39 | 21 | 14 | 1 | 47% |
| Total dos módulos instrumentados | 1437 | 892 | 462 | 2 | 30% |

Após a inclusão de `tests/unit_tests/utils/version_tests.py`, a próxima execução
do workflow deve gerar novos percentuais no artefato de cobertura.

Essa métrica é calculada sobre arquivos inteiros do Superset, muitos deles com
centenas de linhas e funções não selecionadas para a atividade. Por isso, o
percentual total de 30% não representa a cobertura completa do backend nem a
cobertura das decisões analisadas por MC/DC. A evidência específica de MC/DC
está nas tabelas de casos de teste dos métodos M1 a M6, onde cada condição
atômica das decisões selecionadas é variada independentemente.

O workflow usa `--confcutdir=tests/unit_tests/utils` para não carregar o
`tests/conftest.py` global do Superset, pois esse arquivo inicializa a aplicação
inteira e não é necessário para os testes unitários da atividade. O
`tests/unit_tests/utils/conftest.py` local usa stubs para impedir a execução do
`superset/__init__.py` pesado e para evitar dependências nativas como `nh3` e
`cryptography`, que são importadas no bootstrap do projeto, mas não são
exercitadas pelos métodos testados.

Com o ambiente local configurado, o comando equivalente é:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_cov.plugin \
  --confcutdir=tests/unit_tests/utils \
  tests/unit_tests/utils/ptoss_unitarios_test.py \
  tests/unit_tests/utils/urls_tests.py \
  tests/unit_tests/utils/version_tests.py \
  --cov=superset.tasks.utils \
  --cov=superset.utils.core \
  --cov=superset.utils.oauth2 \
  --cov=superset.utils.screenshots \
  --cov=superset.utils.version \
  --cov=superset.utils.urls \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov
```

## 10. Processo de TDD

Funcionalidade escolhida: melhoria em `modify_url_query`.

Problema identificado: a implementação anterior reconstruía a query string
usando apenas `v[0]`. Isso fazia com que parâmetros repetidos fossem perdidos.

Exemplo de entrada:

```text
http://localhost:9000/explore/?filter=a&filter=b
```

Ao adicionar `standalone=1`, o resultado esperado é preservar ambos os filtros:

```text
http://localhost:9000/explore/?filter=a&filter=b&standalone=1
```

### Red

Foram adicionados testes que falhariam na implementação anterior:

```python
def test_modify_url_query_preserves_repeated_existing_parameters() -> None:
    test_url = modify_url_query(
        "http://localhost:9000/explore/?filter=a&filter=b",
        standalone="1",
    )

    assert test_url == "http://localhost:9000/explore/?filter=a&filter=b&standalone=1"
```

Também foi criado teste para valores em lista:

```python
def test_modify_url_query_adds_list_values_as_repeated_parameters() -> None:
    test_url = modify_url_query(
        "http://localhost:9000/explore/?existing=ok",
        tag=["alpha value", "beta/value"],
    )
```

### Green

A implementação mínima substituiu a concatenação manual por:

```python
urllib.parse.urlencode(params, doseq=True, quote_via=urllib.parse.quote, safe="/")
```

Com `doseq=True`, listas são serializadas como parâmetros repetidos.

### Refactor

A refatoração reduziu manipulação manual de strings e passou a usar API própria
da biblioteca padrão para query strings. Isso melhora legibilidade e reduz risco
de erro em encoding.

| Item exigido | Evidência no ciclo TDD |
| --- | --- |
| Evolução dos testes | O primeiro teste cobre preservação de parâmetros repetidos já existentes; o segundo amplia o cenário para listas recebidas como entrada nova |
| Evolução da implementação | A versão anterior usava apenas `v[0]`; a implementação passou a preservar listas completas e parâmetros repetidos |
| Refatorações realizadas | A montagem manual da query foi substituída por `urllib.parse.urlencode` com `doseq=True` |
| Dificuldades observadas | Foi necessário preservar o comportamento existente de encoding e, ao mesmo tempo, não perder valores repetidos |
| Benefícios observados | O código ficou menor, mais legível e protegido contra regressão por testes específicos |

## 11. Análise crítica

O principal aprendizado foi que nem todo método é adequado para MC/DC. Métodos
com apenas branches simples devem ser avaliados com cobertura de branches, mas
não sustentam a análise de independência de condições exigida pelo MC/DC.

A nova seleção ficou mais defensável porque cada função contém pelo menos uma
decisão composta. A caixa-preta ajudou a escolher entradas representativas; a
caixa-branca mostrou quais condições deveriam variar independentemente.

A testabilidade do Superset é boa em funções utilitárias pequenas, mas sistemas
reais trazem acoplamentos de ambiente. Algumas importações dependem de Flask,
Werkzeug, cache, configuração de aplicação e bibliotecas opcionais. Por isso, a
virtualenv correta é necessária para executar a suíte.

O TDD em `modify_url_query` mostrou valor prático: o teste descreveu uma perda
real de comportamento, e a implementação ficou mais simples ao usar
`urllib.parse.urlencode` com `doseq=True`.

Lições aprendidas pela equipe:

| Tema | Reflexão |
| --- | --- |
| Complementaridade | Caixa-preta ajuda a pensar no comportamento; caixa-branca revela condições internas esquecidas |
| Testabilidade | Funções utilitárias pequenas são mais testáveis que trechos acoplados a Flask, banco ou cache |
| Sistemas reais | Dependências, configuração e importações tornam a execução local mais difícil |
| Limitações | MC/DC não é adequado para métodos sem decisão composta e não substitui testes de integração |
| TDD | Escrever o teste primeiro deixou o defeito de `modify_url_query` mais claro e guiou uma correção menor |

## 12. Conclusão

A atividade aplicou testes unitários em 6 métodos compatíveis com MC/DC, além de
uma melhoria desenvolvida por TDD. A seleção final evita forçar MC/DC em métodos
sem decisão composta e torna explícita a relação entre condições, casos de teste
e resultados esperados.

Como próximos passos, a equipe deve executar o workflow no fork, anexar ou
referenciar o artefato de cobertura gerado e rodar `pre-commit run --all-files`
antes de entregar ou enviar alterações.

## 13. Instruções de execução

Com o ambiente configurado:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  --confcutdir=tests/unit_tests/utils \
  tests/unit_tests/utils/ptoss_unitarios_test.py \
  tests/unit_tests/utils/urls_tests.py \
  tests/unit_tests/utils/version_tests.py \
  -q
```

Para cobertura:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest \
  -p pytest_cov.plugin \
  --confcutdir=tests/unit_tests/utils \
  tests/unit_tests/utils/ptoss_unitarios_test.py \
  tests/unit_tests/utils/urls_tests.py \
  tests/unit_tests/utils/version_tests.py \
  --cov=superset.tasks.utils \
  --cov=superset.utils.core \
  --cov=superset.utils.oauth2 \
  --cov=superset.utils.screenshots \
  --cov=superset.utils.version \
  --cov=superset.utils.urls \
  --cov-branch \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov \
  --cov-report=term-missing
```

Para executar no GitHub Actions:

1. Envie as alterações para uma branch `ptoss-*` ou `feat/ptoss-*`.
2. Acesse `Actions > PTOSS Backend Tests`.
3. Abra a execução mais recente.
4. Consulte o bloco `PTOSS coverage` no `Summary`.
5. Baixe o artefato `ptoss-coverage-reports` para obter `coverage.xml` e
   `htmlcov/index.html`.

Antes de enviar alterações ao repositório:

```bash
git add .
pre-commit run --all-files
```
