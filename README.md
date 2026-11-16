# Trabalho Grau B - Redes de Computadores

Simulador de transmissão digital ponta a ponta com codificação de linha, modulação, canais ruidosos e cálculo de métricas (BER e Eficiência Espectral).

## Estrutura de Pastas

```text
trabalho-grauB/
├── src/
│   ├── transmissao_e_canais.py    # Módulo do transmissor e canais (Leonardo)
│   ├── recepcao_e_metricas.py     # Módulo de demodulação e métricas (Luís)
│   └── simulador.py               # Script principal de automação dos testes
├── scripts/
│   ├── gerar_graficos.py          # Script para gerar os gráficos BER x SNR
│   └── gerar_tabela.py            # Script para gerar a tabela de compromisso
├── resultados/
│   ├── dados_brutos/
│   │   └── resultados_simulacao.csv # Base de dados gerada pelo simulador
│   ├── figuras/
│   │   ├── ber_vs_snr_awgn.png      # Gráfico do canal AWGN
│   │   ├── ber_vs_snr_burst.png     # Gráfico do canal Burst Noise
│   │   ├── constelacao_BPSK_awgn.png # Constelação BPSK pós-canal
│   │   ├── constelacao_QPSK_awgn.png # Constelação QPSK pós-canal
│   │   └── constelacao_16QAM_awgn.png # Constelação 16-QAM pós-canal
│   └── tabela_compromisso.md        # Tabela extraída em Markdown
├── .gitignore
├── README.md
└── requirements.txt
Arquitetura do Simulador
O projeto está dividido em três etapas principais:

Transmissão (src/transmissao_e_canais.py): Conversão ASCII/Binário, Codificação de Linha (AMI, Manchester), Modulação (BPSK, QPSK, 16-QAM) e Canais (AWGN e Burst Noise).

Recepção e Métricas (src/recepcao_e_metricas.py): Demodulação (menor distância euclidiana), Decodificação de linha, cálculo de BER e Eficiência Espectral.

Execução e Análise (src/simulador.py e scripts/): Automação dos testes, geração de dados brutos (.csv), gráficos de BER x SNR, diagramas de constelação e tabela de compromisso.

Parâmetros Experimentais
Mensagem base: Texto longo gerado aleatoriamente (12.500 caracteres = 100.000 bits por repetição, totalizando 500.000 bits por cenário com as 5 repetições).

Codificações de linha: AMI e Manchester.

Modulações: BPSK, QPSK e 16-QAM.

Canais: AWGN e Burst Noise (ruído em rajadas com 5% de probabilidade e fator de degradação de 5x).

Variação de SNR: -2 dB a 12 dB (8 valores, passo de 2 dB).

Repetições: 5 repetições por combinação para cálculo de desvio padrão (variabilidade).

Divisão de Responsabilidades
Leonardo : Conversão de dados, Codificação de linha, Transmissor (Modulação), Modelagem dos Canais (AWGN e Burst) e plots de constelação.

Luís: Demodulação, Decodificação de linha, Cálculo de métricas (BER e Eficiência), Automação de testes, Gráficos finais, Gestão do GitHub e documentação.

Vídeo e Apresentação: Ambos.

Instruções de Instalação e Execução
Clone o repositório:
git clone https://github.com/luisfaleiro/trabalho-grauB.git

Instale as dependências:
pip install -r requirements.txt

Execute a simulação completa (gera os dados brutos em CSV e as constelações):
python src/simulador.py

Gere os gráficos de BER x SNR:
python scripts/gerar_graficos.py

Gere a tabela de compromisso:
python scripts/gerar_tabela.py

Resultados
Tabela de Compromisso (Canal AWGN, SNR = 10 dB)
Modulação	Codificação	Eficiência Espectral (bits/s/Hz)	BER Média
BPSK	AMI	1	4e-06
BPSK	MANCHESTER	0.5	2e-06
QPSK	AMI	2	0.000796
QPSK	MANCHESTER	1	0.000736
16-QAM	AMI	4	0.055288
16-QAM	MANCHESTER	2	0.0733
Análise: O BPSK demonstra a maior robustez (menor BER) ao custo da menor eficiência espectral. O 16-QAM oferece 4 vezes mais eficiência que o BPSK, mas requer SNRs muito mais altas para atingir uma BER aceitável. A codificação Manchester reduz a eficiência pela metade por usar dois símbolos por bit, mantendo uma BER semelhante à do AMI na mesma SNR.

Gráficos de BER x SNR
Os gráficos comparando os canais AWGN e Burst Noise estão disponíveis na pasta resultados/figuras/.

O canal Burst Noise degrada significativamente o desempenho em SNRs altas, criando um "piso de erro" (error floor) que impede a comunicação confiável em comparação ao AWGN.

Diagramas de Constelação
Foram geradas constelações (limpas vs. ruidosas a 12 dB) para BPSK, QPSK e 16-QAM, demonstrando visualmente o efeito do ruído gaussiano nos símbolos transmitidos. Estão disponíveis na pasta resultados/figuras/.

Vídeo de Demonstração
(Adicionar o link do vídeo aqui)