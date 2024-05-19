import sys
import os
import time
import requests
import mimetypes
import nltk
from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer
from pydub import AudioSegment
import argparse

# Baixar o vader_lexicon
nltk.download('vader_lexicon')

# Configurar API Key do AssemblyAI
API_KEY = os.getenv('ASSEMBLYAI_API_KEY', '6dd9c61f8efa4c30be248f902bd0e659')
ASSEMBLYAI_ENDPOINT = 'https://api.assemblyai.com/v2'

headers = {
    'authorization': API_KEY,
    'content-type': 'application/json'
}

def eh_arquivo_audio(caminho_arquivo):
    """Verifica se o arquivo fornecido é um arquivo de áudio."""
    tipo_mime, _ = mimetypes.guess_type(caminho_arquivo)
    return tipo_mime and tipo_mime.startswith('audio')

def adicionar_silencio_ao_audio(caminho_arquivo, duracao_ms=120000):
    """Adiciona silêncio ao final de um arquivo de áudio."""
    audio = AudioSegment.from_file(caminho_arquivo)
    silencio = AudioSegment.silent(duration=duracao_ms)
    audio_com_silencio = audio + silencio
    novo_caminho_arquivo = "temp_com_silencio_" + os.path.basename(caminho_arquivo)
    audio_com_silencio.export(novo_caminho_arquivo, format="mp3")
    return novo_caminho_arquivo

def fazer_upload_audio(caminho_arquivo):
    """Faz o upload do arquivo de áudio para o AssemblyAI."""
    print("Iniciando upload do arquivo de áudio...")
    url_upload = f"{ASSEMBLYAI_ENDPOINT}/upload"
    with open(caminho_arquivo, 'rb') as f:
        resposta = requests.post(url_upload, headers=headers, files={'file': f})
    resposta.raise_for_status()
    url_audio = resposta.json()['upload_url']
    print(f"Upload concluído. URL do áudio: {url_audio}")
    return url_audio

def solicitar_transcricao(url_audio):
    """Solicita a transcrição do arquivo de áudio com diarização do locutor."""
    print("Solicitando transcrição com diarização...")
    pedido_transcricao = {
        'audio_url': url_audio,
        'speaker_labels': True,
        'punctuate': True,
        'format_text': True,
        'language_code': 'pt'
    }
    resposta = requests.post(f"{ASSEMBLYAI_ENDPOINT}/transcript", json=pedido_transcricao, headers=headers)
    resposta.raise_for_status()
    id_transcricao = resposta.json()['id']
    print(f"ID da transcrição: {id_transcricao}")
    return id_transcricao

def obter_resultado_transcricao(id_transcricao):
    """Verifica o status da transcrição e recupera o resultado quando concluído."""
    print("Aguardando conclusão da transcrição...")
    tempo_inicio = time.time()
    timeout = 3600  # Tempo máximo de espera (em segundos)
    while True:
        resposta = requests.get(f"{ASSEMBLYAI_ENDPOINT}/transcript/{id_transcricao}", headers=headers)
        resposta.raise_for_status()
        status = resposta.json()['status']
        print(f"Status da transcrição: {status}")
        if status == 'completed':
            print("Transcrição concluída.")
            return resposta.json()
        elif status == 'failed':
            raise Exception('Transcrição falhou')
        elif time.time() - tempo_inicio > timeout:
            raise Exception('Tempo de espera para transcrição excedido')
        print("Transcrição ainda em processamento...")
        time.sleep(10)

def transcrever_audio_com_diarizacao(caminho_arquivo):
    """Transcreve o arquivo de áudio fornecido com diarização."""
    if not eh_arquivo_audio(caminho_arquivo):
        raise Exception(f"O arquivo {caminho_arquivo} não parece ser um arquivo de áudio.")
    
    # Adicionar silêncio ao final do áudio
    novo_caminho_arquivo = adicionar_silencio_ao_audio(caminho_arquivo)
    url_audio = fazer_upload_audio(novo_caminho_arquivo)
    id_transcricao = solicitar_transcricao(url_audio)
    resultado_transcricao = obter_resultado_transcricao(id_transcricao)
    os.remove(novo_caminho_arquivo)  # Remover o arquivo temporário

    return resultado_transcricao

def analisar_sentimentos(texto):
    """Analisa o sentimento do texto fornecido."""
    blob = TextBlob(texto, analyzer=PatternAnalyzer())
    sentimento = blob.sentiment
    return {
        "neg": sentimento.polarity < 0,
        "neu": sentimento.polarity == 0,
        "pos": sentimento.polarity > 0,
        "compound": sentimento.polarity
    }

def identificar_analista(transcricao, etiqueta_analista='SPEAKER_1'):
    """Identifica a fala do analista a partir da transcrição."""
    texto_analista = []
    if not transcricao.get('utterances'):
        raise Exception('Transcrição não contém falas. Verifique se a diarização foi ativada corretamente.')
    for segmento in transcricao['utterances']:
        if segmento['speaker'] == etiqueta_analista:
            texto_analista.append(segmento['text'].strip())
    return " ".join(texto_analista)

def resumir_transcricao(transcricao):
    """Resume a transcrição por locutor e tópicos."""
    resumo = []
    if not transcricao.get('utterances'):
        raise Exception('Transcrição não contém falas. Verifique se a diarização foi ativada corretamente.')
    for segmento in transcricao['utterances']:
        locutor = segmento['speaker']
        texto = segmento['text'].strip()
        if len(texto) > 0:
            resumo.append(f"- {locutor}: {texto}")
    return "\n".join(resumo)

def processar_atendimento(caminho_arquivo, etiqueta_analista='SPEAKER_1'):
    """Processa a interação de atendimento ao cliente."""
    transcricao = transcrever_audio_com_diarizacao(caminho_arquivo)
    if not transcricao:
        raise Exception("Transcrição falhou ou não retornou dados.")
    
    texto_analista = identificar_analista(transcricao, etiqueta_analista)
    sentimentos = analisar_sentimentos(texto_analista)
    resumo_transcricao = resumir_transcricao(transcricao)
    
    return {
        'resumo_transcricao': resumo_transcricao,
        'sentimentos': sentimentos
    }

def salvar_transcricao(resumo_transcricao, caminho_transcricao):
    """Salva o resultado da transcrição em um arquivo."""
    with open(caminho_transcricao, 'w') as arquivo_transcricao:
        arquivo_transcricao.write("Transcrição:\n")
        arquivo_transcricao.write(resumo_transcricao + "\n")

def salvar_analise(resultado, caminho_analise):
    """Salva a análise de sentimentos em um arquivo."""
    with open(caminho_analise, 'w') as arquivo_analise:
        arquivo_analise.write("Análise de Sentimentos (Analista):\n")
        for sentimento, valor in resultado['sentimentos'].items():
            arquivo_analise.write(f"{sentimento}: {valor}\n")

def main():
    parser = argparse.ArgumentParser(description="Processamento de atendimento com transcrição e análise de sentimentos.")
    parser.add_argument("caminho_audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("caminho_transcricao", help="Caminho para salvar a transcrição")
    parser.add_argument("caminho_analise", help="Caminho para salvar a análise de sentimentos")

    args = parser.parse_args()

    if not os.path.isfile(args.caminho_audio):
        print(f"Arquivo de áudio não encontrado: {args.caminho_audio}")
        sys.exit(1)

    print("Iniciando processamento...")
    try:
        resultado = processar_atendimento(args.caminho_audio)
        salvar_transcricao(resultado['resumo_transcricao'], args.caminho_transcricao)
        salvar_analise(resultado, args.caminho_analise)
        print(f"Processamento concluído. Transcrição salva em: {args.caminho_transcricao}")
        print(f"Análise de sentimentos salva em: {args.caminho_analise}")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")

if __name__ == '__main__':
    main()
