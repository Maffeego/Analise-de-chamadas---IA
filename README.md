# Analise-de-chamadas---IA
Projeto de Transcrição e Análise de Sentimentos

Descrição do Projeto:
  Este projeto é uma solução automatizada para transcrever áudios com diarização (identificação de diferentes locutores) e realizar análise de sentimentos sobre as falas de um locutor específico. Visando analisar chamadas de atendimento ao cliente, avaliando o desempenho do analista em questão.
  Utiliza a API da AssemblyAI para a transcrição e a biblioteca TextBlob para a análise de sentimentos.

Funcionalidades:

- Transcrição de Áudio: Converte arquivos de áudio em texto, identificando diferentes locutores.
- Análise de Sentimentos: Analisa o sentimento das falas de um locutor específico (O falante1, levando em conta que o analista seria o primeiro a cumprimentar o cliente), classificando-as como positivas, negativas ou neutras.
- Adição de Silêncio: Adiciona um período de silêncio ao final do áudio para garantir a completa transcrição.

Tecnologias Utilizadas:

Linguagem: Python

Bibliotecas:

- requests para comunicação com a API da AssemblyAI
- mimetypes para verificação do tipo de arquivo
- nltk e textblob para análise de sentimentos
- pydub para manipulação de arquivos de áudio
  
API: AssemblyAI para transcrição de áudio


Estrutura do Código
project/
├── main.py
└── requirements.txt

Arquivo main.py
Contém toda a lógica do projeto, incluindo funções para:
- Verificar se um arquivo é de áudio
- Adicionar silêncio ao final de um arquivo de áudio
- Fazer upload do áudio para a API da AssemblyAI
- Solicitar a transcrição do áudio
- Obter o resultado da transcrição
- Analisar os sentimentos do texto transcrito
- Identificar as falas de um locutor específico
- Resumir a transcrição
- Salvar os resultados em arquivos

Como Executar:
- Pré-requisitos:
    Python 3.7 ou superior.
Instalar as dependências listadas em requirements.txt
  - pip install -r requirements.txt
  - python -m textblob.download_corpora
Baixar e instalar o ffmpeg:
  No Windows:
  - Baixe o executável do ffmpeg do site oficial: https://ffmpeg.org/download.html
  - Extraia o conteúdo do arquivo compactado.
  - Adicione o caminho do diretório bin do ffmpeg ao PATH do sistema.
  No macOS:
  - bash
  - brew install ffmpeg
  No Linux (Debian/Ubuntu):
  - bash
  - sudo apt-get install ffmpeg

Configuração da API Key:
  Obtenha uma API Key da AssemblyAI (Versão gratuita).
  *Defina a variável de ambiente ASSEMBLYAI_API_KEY com a sua API Key*

Execução do Script:
- Abra o CMD;
- Acesse o diretório contendo o arquivo main.py;
- Para executar o script, utilize o comando: python main.py caminho_para_o_audio caminho_para_salvar_transcricao caminho_para_salvar_analise
Ex: python main.py entrada/audio.mp3 saida/transcricao.txt saida/analise.txt

Exemplos de Uso:

Entrada
  Arquivo de áudio: audio.mp3
Saída
  Transcrição salva em: transcricao.txt
  Análise de sentimentos salva em: analise.txt
  
Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests no repositório.

Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
