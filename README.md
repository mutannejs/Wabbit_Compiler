# Wabbit Compiler

Compilador da linguagem **Wabbit**. Feito para a matéria Laboratório de Compiladores.

1. [X] modelo de dados do WabbitScript (subconjunto da linguagem Wabbit)
1. [X] interpretador do WabbitScript
1. [X] modelo:
    1. [X] complementar operadores (numéricos, sobre caracteres e booleanos)
    1. [X] adicionar definições no modelo do compilador
    1. [X] no CompoundExpression aceitar statements na última instrução
    1. [X] adicionar o tipo `unit ()` (é um objeto, como None no Python)
    1. [X] obrigar constantes receberem um inicializador
1. [X] fazer o anterior para o interp também
1. [X] criar Lexer
1. [X] realizar mais testes para o Lexer
1. [X] adicionar `break` e `continue` no modelo
1. [X] criar Parse
1. [X] arrumar o Parse e funções como to_source e tokenize
1. [X] avaliação de tipos
1. [X] compilar para C
    1. [X] arrumar tipo booleano
    1. [X] implementar curto-circuito
1. [X] tranformar o modelo, simplificando-o
1. [X] compilar para wasm
1. [ ] transformar o WabbitScript em WabbitFunc
    1. [X] model extendido
    1. [X] tokenize extendido
    1. [X] parse extendido
    1. [X] to_source extendido
    1. [X] interp extendido
    1. [ ] corrigir checktype
1. [ ] coerção explícita
1. [ ] implementar WabbitType

### Execução

Para criar um ambiente virtual python:
```
python3 -m venv wabbit_compiler
```

Para executar o ambiente virtual do python:
```
source wabbit_compiler/bin/activate
```

Para instalar o sly no projeto
```
pip install sly
```

Para desativá-lo:
```
deactivate
```