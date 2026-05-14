# SBOMBOM

SBOMBOM é uma CLI simples e direta para gerar SBOMs em CycloneDX JSON a partir dos arquivos que declaram as dependências da sua aplicação.

É possível gerar o SBOM de três formas: informando manualmente os arquivos de referência das bibliotecas, analisando um repositório local ou a partir de um repositório Git remoto.

Por que SBOMBOM? Quem nao gosta de um bombom? :D

## Modos de uso

SBOMBOM pode gerar SBOM de tres formas principais:

### 1) Arquivos de referencia informados manualmente

Este e o modo mais direto quando voce ja sabe quais arquivos representam as dependencias da aplicacao. E ideal para pipelines, automacoes de AppSec e cenarios em que nao e necessario clonar ou varrer um repositorio inteiro.

```bash
sbombom --app app-shellcat --referencias pom.xml --output sbom.json
```

### 2) Repositorio local

Use quando o codigo ja esta disponivel na maquina ou no ambiente de CI. O SBOMBOM detecta automaticamente os arquivos de dependencia suportados dentro do diretorio.

```bash
sbombom --repo ./meu-repositorio --output sbom.json
```

### 3) Repositorio Git remoto

Use quando quiser gerar o SBOM diretamente a partir de uma URL Git. O SBOMBOM faz um clone temporario, analisa os arquivos suportados e limpa o diretorio temporario ao final.

```bash
sbombom --repo https://github.com/org/amycat.git --output sbom.json
```

## Features

- Gera SBOM em **CycloneDX JSON 1.5**.
- Cobre os tres modos de uso: arquivos de referencia, repositorio local e repositorio Git remoto.
- Imprime o JSON no stdout ou salva em arquivo com `--output`.
- Filtra a analise por ecossistema com `--language`.
- Detecta e processa dependencias de Python, JavaScript/Node.js, Java, .NET e Golang.
- Gera `purl` e `bom-ref` para componentes quando possivel.
- Deduplica componentes e ordena a saida para facilitar comparacao entre execucoes.
- Ignora arquivos ainda nao implementados no MVP com aviso em modo `--verbose`.
- Nao executa scan de vulnerabilidades, nao consulta APIs externas e nao depende de banco de dados.

## Instalacao local

Requisitos:

- Python 3.11+
- Git instalado para uso com repositorios remotos

Para instalar direto do GitHub com `pip`:

```bash
pip install git+https://github.com/renanhsilva/sbombom.git
```

Depois da instalacao:

```bash
sbombom --help
```

Para atualizar uma instalacao feita a partir do GitHub:

```bash
pip install --upgrade git+https://github.com/renanhsilva/sbombom.git
```

Para desenvolvimento local, use instalacao editavel:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Como rodar

```bash
sbombom --help
python -m sbombom.cli --help
```

Quando `--output` nao for informado, o JSON e impresso no stdout.

Use `--language` para limitar a deteccao a um ecossistema especifico. Isso e util em repositorios grandes com fixtures, exemplos ou arquivos quebrados de outras linguagens.

Linguagens aceitas:

- `python`
- `javascript`
- `java`
- `dotnet`
- `golang`

Aliases aceitos incluem `go`, `node`, `nodejs`, `npm`, `maven`, `nuget`, `py` e `csharp`.

## Exemplos

Gerar SBOM a partir de um repositorio local:

```bash
sbombom --repo ./meu-repositorio --output sbom.json
```

Gerar SBOM a partir de um repositorio Git remoto:

```bash
sbombom --repo https://github.com/org/projeto.git --output sbom.json
```

Gerar SBOM de um repositorio Go:

```bash
sbombom --repo https://github.com/aquasecurity/trivy --language go --output sbom.json
```

Gerar SBOM a partir de `requirements.txt`:

```bash
sbombom --app minha-api --referencias requirements.txt --output sbom.json
```

Gerar SBOM a partir de multiplos arquivos:

```bash
sbombom --app minha-app --referencias requirements.txt package-lock.json pom.xml go.mod --output sbom.json
```

Gerar SBOM a partir de `package.json`:

```bash
sbombom --app webapp --referencias package.json --output sbom.json
```

Gerar SBOM a partir de `pom.xml`:

```bash
sbombom --app java-api --referencias pom.xml --output sbom.json
```

Gerar SBOM a partir de `.csproj`:

```bash
sbombom --app dotnet-api --referencias src/App/App.csproj --output sbom.json
```

Gerar SBOM a partir de `packages.config`:

```bash
sbombom --app dotnet-api --referencias packages.config --output sbom.json
```

Gerar SBOM a partir de `go.mod`:

```bash
sbombom --app go-api --referencias go.mod --output sbom.json
```

## Formato de saida

A saida gerada segue CycloneDX JSON 1.5 e inclui:

- `bomFormat: CycloneDX`
- `specVersion: 1.5`
- `serialNumber` com UUID
- `metadata.timestamp`
- `metadata.tools` com SBOMBOM
- `metadata.component` representando a aplicacao principal
- `components` com as dependencias encontradas
- `purl` e `bom-ref` quando possivel

## Arquivos detectados

O detector reconhece estes arquivos dentro de repositorios:

- Python: `requirements.txt`, `requirements-dev.txt`, arquivos `*requirements*.txt`, arquivos `*constraints*.txt`, arquivos `.txt` dentro de diretorios `requirements/`, `pyproject.toml`, `Pipfile.lock`, `poetry.lock`
- JavaScript/Node.js: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- Java: `pom.xml`, `build.gradle`, `build.gradle.kts`, `gradle.lockfile`
- .NET: `*.csproj`, `packages.lock.json`, `packages.config`
- Golang: `go.mod`, `go.sum`

## Parsers implementados no MVP

- Python: `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, arquivos `*requirements*.txt`, arquivos `*constraints*.txt` e arquivos `.txt` dentro de diretorios `requirements/`
- JavaScript/Node.js: `package.json`, `package-lock.json`
- Java: `pom.xml`
- .NET: `*.csproj`, `packages.config`
- Golang: `go.mod`

Arquivos detectados mas ainda nao implementados sao ignorados. Use `--verbose` para ver os avisos.

## Limitacoes do MVP

- Nao executa scanner de vulnerabilidades.
- Nao consulta APIs externas.
- Nao cria dashboard.
- Nao resolve propriedades Maven.
- Nao monta grafo de relacoes entre dependencias.
- Nao inclui testes unitarios neste momento.

## Roadmap

- Suporte aos demais lockfiles detectados.
- Resolucao de propriedades Maven.
- Melhor suporte a constraints por ecossistema.
- Relacoes de dependencias no documento CycloneDX.
- Validacao formal de PURL.
- Assinatura e attestation de SBOM.
- Saida em formatos adicionais.
