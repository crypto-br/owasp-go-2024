# OWASP GOIÂNIA - 2024
## Automatizando correções de vulnerabildiades em código com OpenAI e Horusec

### PDF da apresentação: [Download](https://raw.githubusercontent.com/crypto-br/owasp-go-2024/blob/main/OWASP-GO-2024-1.pdf)

### Descrição:

Este projeto contém um script em Python que lê um relatório de vulnerabilidades de um arquivo de log, extrai as informações de vulnerabilidades, consulta a API da OpenAI para obter sugestões de correção e gera um relatório HTML com essas informações. Em seguida faz um pull request para o Github com uma SUGESTÃO de correção

## Requisitos

- Python 3.x
- Bibliotecas `openai` `re` `markdown` `pyproject-toml` `pygithub`
- Relatorio gerado pelo Horusec
- Docker

## Gerando relatório do Horusec no diretório local
```
docker run -it -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/exemplo:/src horuszup/horusec-cli:latest horusec start -D -e="true" -p="./src/" --ignore="..." > report.txt
```

## Instalação

1. Clone o repositório para o seu ambiente local:
    ```bash
    git clone https://github.com/crypto-br/owasp-go-2024.git
    ```
2. Navegue até o diretório do projeto:
    ```bash
    cd owasp-go-2024
    ```
3. Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

Modifique o  arquivo .env com suas credenciais (lembrando que isso é apenas um exemplo, e não é a melhor forma de armazenar credenciais)

OPENAI_API_KEY=""
GIT_TOKEN=""
REPO_NAME=""
BRANCH_NAME=""

## Uso

1. Certifique-se de que o arquivo de log de vulnerabilidades (por exemplo, `report.txt`) esteja no mesmo diretório que o script.
2. Execute o script:
    ```bash
    python chat_review.py
    ```
3. O script irá gerar um relatório HTML chamado `relatorio_vulnerabilidades.html` no diretório atual e faz um pull request fazendo uma SUGESTÃO de correção.
