from openai import OpenAI
import json
import re
import markdown
from dotenv import load_dotenv
import os
from github import Github

# Importando variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')
GIT_TOKEN = os.getenv('GIT_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
BRANCH_NAME = os.getenv('BRANCH_NAME')

# Defina sua chave de API da OpenAI
client = OpenAI(api_key=API_KEY)

# Função para ler o arquivo de log do Horusec
def ler_arquivo_log(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            return arquivo.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
        return None

def extrair_vulnerabilidades(log):
    if not log:
        print("Log vazio ou inválido.")
        return []
    try:
        padrao = re.compile(r'Language: (?P<language>.*?)\nSeverity: (?P<severity>.*?)\nLine: (?P<line>.*?)\nColumn: (?P<column>.*?)\nSecurityTool: (?P<security_tool>.*?)\nConfidence: (?P<confidence>.*?)\nFile: (?P<file>.*?)\nCode: (?P<code>.*?)\nRuleID: (?P<rule_id>.*?)\nType: (?P<type>.*?)\nReferenceHash: (?P<reference_hash>.*?)\nDetails: (?P<details>.*?)\n', re.DOTALL)
        return [m.groupdict() for m in padrao.finditer(log)]
    except re.error as e:
        print(f"Erro ao extrair vulnerabilidades: {e}")
        return []

# Função para consultar a API da OpenAI
def consultar_openai(vulnerabilidade):
    prompt = f"Aqui está uma vulnerabilidade encontrada pelo Horusec: {vulnerabilidade}. Como eu posso corrigir essa vulnerabilidade?"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        md_to_html = response.choices[0].message.content
        return markdown.markdown(md_to_html)
    except Exception as e:
        print(f"Erro ao consultar a API da OpenAI: {e}")
        return "Erro ao gerar sugestão de correção."

# Função para gerar o relatório em HTML
def gerar_relatorio_html(vulnerabilidades, sugestao):
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Vulnerabilidades</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h2 { color: #2F4F4F; }
            pre { background: #f4f4f4; padding: 10px; border: 1px solid #ddd; }
            .vulnerability { margin-bottom: 20px; }
            hr { border: 0; height: 1px; background: #ddd; margin-top: 20px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>Relatório de Vulnerabilidades</h1>
    """
    try:
        for vulnerabilidade in vulnerabilidades:
            detalhes = vulnerabilidade.get('details', 'Detalhes não encontrados')
            codigo = vulnerabilidade.get('code', 'Código não encontrado')
            
            html += f"""
            <div class="vulnerability">
                <h2>Vulnerabilidade Encontrada</h2>
                <p><strong>Detalhes:</strong> {detalhes}</p>
                <p><strong>Código Vulnerável:</strong></p>
                <pre>{codigo}</pre>
                <p><strong>Sugestão de Correção:</strong></p>
                <pre>{sugestao}</pre>
            </div>
            <hr>
            """
        
        html += """
        </body>
        </html>
        """
    except Exception as e:
        print(f"Erro ao gerar relatório HTML: {e}")
    return html

def pull_request_openai(sugestao):
    prompt = f"Pegar apenas o código corrigido no texto na linguagem que ele é: {sugestao}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao extrair código corrigido: {e}")
        return None

def create_pull_request(code_pr, detalhes, cleaned_path):
    if not code_pr or not cleaned_path:
        print("Código ou caminho inválido, PR não criado.")
        return None

    try:
        # Autenticação
        g = Github(GIT_TOKEN)

        # Obter repositório
        repo = g.get_repo(REPO_NAME)

        # Obter o branch principal
        main_branch = repo.get_branch('main')

        # Criar um novo branch para a correção
        repo.create_git_ref(ref=f'refs/heads/{BRANCH_NAME}', sha=main_branch.commit.sha)

        # Caminho do arquivo no repositório
        file_path = f'exemplo/{cleaned_path}'

        # Obter o arquivo atual do repositório
        file = repo.get_contents(file_path, ref=BRANCH_NAME)

        # Atualizar o arquivo no novo branch
        repo.update_file(file.path, 'Sugestão de correção de código', code_pr, file.sha, branch=BRANCH_NAME)

        # Criar um pull request
        pr = repo.create_pull(title='Correção código', body=detalhes, head=BRANCH_NAME, base='main')

        print(f"Pull Request criado: {pr.html_url}")
        return pr.html_url
    except Exception as e:
        print(f"Erro ao criar Pull Request: {e}")
        return None

# Função principal
def main():
    caminho_arquivo = "report.txt"
    log = ler_arquivo_log(caminho_arquivo)
    if log:
        vulnerabilidades = extrair_vulnerabilidades(log)

        for vulnerabilidade in vulnerabilidades:
            detalhes = vulnerabilidade.get('details', 'Detalhes não encontrados')
            sugestao = consultar_openai(vulnerabilidade)
            file_path = vulnerabilidade.get('file')
            cleaned_path = re.sub(r'\.horusec/[0-9a-fA-F-]+/', '', file_path) if file_path else None

        relatorio_html = gerar_relatorio_html(vulnerabilidades, sugestao)
        
        try:
            with open('relatorio_vulnerabilidades.html', 'w', encoding='utf-8') as arquivo_html:
                arquivo_html.write(relatorio_html)
            print("Relatório de vulnerabilidades gerado com sucesso: relatorio_vulnerabilidades.html")
        except Exception as e:
            print(f"Erro ao salvar o relatório HTML: {e}")

        code_pr = pull_request_openai(sugestao)
        create_pull_request(code_pr, detalhes, cleaned_path)
    else:
        print("Nenhuma vulnerabilidade encontrada ou erro ao ler o arquivo de log.")

if __name__ == "__main__":
    main()
