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
| Integrante 2 | `parse_js_uri_path_item` |
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
| `superset/utils/urls.py` | Manipulação de URLs, usada na parte de TDD |

## 3. Planejamento dos testes

A seleção foi refeita para atender ao requisito de MC/DC: todos os 6 métodos
testados possuem ao menos uma decisão composta com duas ou mais condições
atômicas.

Critérios usados:

| Critério | Aplicação |
| --- | --- |
| Particionamento de equivalência | Usuário autenticado/anônimo/ausente, usuário completo/incompleto, estados de cache |
| Análise de valor limite | `None`, string vazia, item sem delimitador, imagem ausente |
| Cobertura de branches | Caminhos verdadeiro/falso das decisões |
| MC/DC | Cada condição atômica foi variada para demonstrar impacto independente na decisão |
| TDD | Aplicado separadamente em `modify_url_query` |

## 4. Métodos selecionados para MC/DC

| ID | Função/método | Decisão composta analisada |
| --- | --- | --- |
| M1 | `get_current_user` | `hasattr(g, "user") and g.user`; `user and not user.is_anonymous` |
| M2 | `parse_js_uri_path_item` | `eval_undefined and item in (...)`; `unquote and item` |
| M3 | `user_label` | `user.first_name and user.last_name` |
| M4 | `split` | `parens == 0 and not quotes and character == delimiter` |
| M5 | `check_for_oauth2` | `database.is_oauth2_enabled() and database.db_engine_spec.needs_oauth2(ex)` |
| M6 | `ScreenshotCachePayload.should_trigger_task` | combinação de `or` com subdecisões `and` por estado |

### Mapeamento método -> arquivo

| Método/função | Arquivo |
| --- | --- |
| `get_current_user` | `superset/tasks/utils.py` |
| `parse_js_uri_path_item` | `superset/utils/core.py` |
| `user_label` | `superset/utils/core.py` |
| `split` | `superset/utils/core.py` |
| `check_for_oauth2` | `superset/utils/oauth2.py` |
| `ScreenshotCachePayload.should_trigger_task` | `superset/utils/screenshots.py` |
| `modify_url_query` | `superset/utils/urls.py` |

## 5. Testes desenvolvidos

Arquivo principal criado:

```text
tests/unit_tests/utils/ptoss_unitarios_test.py
```

Também foram adicionados testes de TDD em:

```text
tests/unit_tests/utils/urls_tests.py
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

### M2 - `parse_js_uri_path_item`

Objetivo: interpretar componentes de URL vindos do JavaScript, tratando
`null`/`undefined` e aplicando `unquote` quando solicitado.

Decisão 1:

```python
eval_undefined and item in ("null", "undefined")
```

| Caso | Entrada | C1: `eval_undefined` | C2: item sentinela | Decisão | Esperado |
| --- | --- | --- | --- | --- | --- |
| CT5 | `"undefined"`, `True` | T | T | T | `None` |
| CT6 | `"undefined"`, `False` | F | T | F | `"undefined"` |
| CT7 | `"dashboard"`, `True` | T | F | F | `"dashboard"` |

Decisão 2:

```python
unquote and item
```

| Caso | Entrada | C1: `unquote` | C2: item presente | Decisão | Esperado |
| --- | --- | --- | --- | --- | --- |
| CT8 | `"sales%2Fnorth"`, `True` | T | T | T | `"sales/north"` |
| CT9 | `"sales%2Fnorth"`, `False` | F | T | F | `"sales%2Fnorth"` |
| CT10 | `None`, `True` | T | F | F | `None` |

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

## 6. Integração entre caixa-preta e caixa-branca

A caixa-preta definiu classes de entrada com base no comportamento esperado:
usuário autenticado/anônimo/ausente, usuário completo/incompleto, URL
codificada, estados de cache e falha OAuth2.

A caixa-branca complementou essa visão ao revelar os predicados internos que
precisavam ser cobertos por MC/DC. Sem a leitura do código, seria fácil testar
apenas casos comuns e deixar sem cobertura condições como usuário anônimo,
usuário ausente, delimitador dentro de aspas ou `ERROR` sem TTL expirado.

| Lacuna funcional | Complemento estrutural |
| --- | --- |
| Usuário autenticado seria testado, mas usuário anônimo poderia ser tratado errado | MC/DC variou presença de `g.user` e `is_anonymous` |
| Separar string por vírgula não cobre aspas e parênteses | MC/DC incluiu vírgula dentro de aspas e parênteses |
| Testar usuário completo não cobre fallback para `username` | MC/DC variou nome e sobrenome |
| Testar OAuth2 habilitado não cobre exceção que não exige OAuth2 | MC/DC variou a resposta de `needs_oauth2` |
| Testar cache pendente não cobre estados `ERROR`, `COMPUTING` e `UPDATED` | MC/DC ativou cada termo da decisão |

## 7. Rastreabilidade

| Funcionalidade | Função/método | Teste |
| --- | --- | --- |
| Resolução do usuário atual | `get_current_user` | `test_get_current_user_mcdc_user_presence_decision` e `test_get_current_user_mcdc_anonymous_user_decision` |
| Interpretação de item de URL | `parse_js_uri_path_item` | `test_parse_js_uri_path_item_mcdc_eval_undefined_decision` e `test_parse_js_uri_path_item_mcdc_unquote_decision` |
| Label de usuário | `user_label` | `test_user_label_mcdc_full_name_decision` |
| Split respeitando contexto | `split` | `test_split_mcdc_delimiter_decision` |
| Detecção de OAuth2 | `check_for_oauth2` | `test_check_for_oauth2_mcdc_decision` |
| Disparo de tarefa de screenshot | `ScreenshotCachePayload.should_trigger_task` | `test_screenshot_payload_should_trigger_task_mcdc_decision` |
| Melhoria por TDD | `modify_url_query` | `test_modify_url_query_preserves_repeated_existing_parameters` e `test_modify_url_query_adds_list_values_as_repeated_parameters` |

## 8. Métricas e evidências de cobertura

Foi realizada checagem sintática dos arquivos alterados:

```bash
python3 -m py_compile superset/utils/urls.py tests/unit_tests/utils/urls_tests.py tests/unit_tests/utils/ptoss_unitarios_test.py
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

Com o ambiente configurado, o comando recomendado é:

```bash
python3 -m pytest \
  tests/unit_tests/utils/ptoss_unitarios_test.py \
  tests/unit_tests/utils/urls_tests.py \
  --cov=superset.tasks.utils \
  --cov=superset.utils.core \
  --cov=superset.utils.oauth2 \
  --cov=superset.utils.screenshots \
  --cov=superset.utils.urls \
  --cov-branch \
  --cov-report=term-missing
```

## 9. Processo de TDD

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

## 10. Análise crítica

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

## 11. Conclusão

A atividade aplicou testes unitários em 6 métodos compatíveis com MC/DC, além de
uma melhoria desenvolvida por TDD. A seleção final evita forçar MC/DC em métodos
sem decisão composta e torna explícita a relação entre condições, casos de teste
e resultados esperados.

Como próximos passos, a equipe deve ativar o ambiente de desenvolvimento do
Superset, executar `pytest` com cobertura e rodar `pre-commit run --all-files`
antes de entregar ou enviar alterações.

## 12. Instruções de execução

Com o ambiente configurado:

```bash
python3 -m pytest tests/unit_tests/utils/ptoss_unitarios_test.py tests/unit_tests/utils/urls_tests.py -q
```

Para cobertura:

```bash
python3 -m pytest \
  tests/unit_tests/utils/ptoss_unitarios_test.py \
  tests/unit_tests/utils/urls_tests.py \
  --cov=superset.tasks.utils \
  --cov=superset.utils.core \
  --cov=superset.utils.oauth2 \
  --cov=superset.utils.screenshots \
  --cov=superset.utils.urls \
  --cov-branch \
  --cov-report=html \
  --cov-report=term-missing
```

Antes de enviar alterações ao repositório:

```bash
git add .
pre-commit run --all-files
```
