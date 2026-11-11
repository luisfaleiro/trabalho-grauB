# Trabalho Grau B - Redes de Computadores

Simulador de transmissão digital ponta a ponta com codificação de linha, modulação, canais ruidosos e cálculo de métricas (BER e Eficiência Espectral).

## 🏗️ Arquitetura do Simulador
O projeto está dividido em três etapas principais:
1. **Transmissão (`src/transmissao_e_canais.py`)**: Conversão ASCII/Binário, Codificação de Linha (AMI, Manchester), Modulação (BPSK, QPSK, 16-QAM) e Canais (AWGN e Burst Noise).
2. **Recepção e Métricas (`src/recepcao_e_metricas.py`)**: Demodulação (menor distância euclidiana), Decodificação de linha e cálculo de BER/Eficiência Espectral.
3. **Execução (`src/simulador.py`)**: Automação dos testes, repetições e salvamento de dados brutos.

## ⚙️ Parâmetros Utilizados
* **Linguagem:** Python 3
* **Codificações de linha:** AMI e Manchester
* **Modulações:** BPSK, QPSK e 16-QAM
* **Canais:** AWGN (variação de SNR) e Burst Noise (ruído em rajadas)
* **Amostragem:** Mínimo de 100.000 bits por teste, 8 valores de SNR, 5 repetições aleatórias por cenário.

## 👥 Divisão de Responsabilidades
* **Leonardo Hillesheim:** Conversão de dados, Codificação de linha, Transmissor (Modulação), Modelagem dos Canais (AWGN e Burst) e plots de constelação.
* **Luís:** Demodulação, Decodificação de linha, Cálculo de métricas (BER e Eficiência), Automação de testes, Gráficos finais, Gestão do GitHub e documentação.
* *Vídeo e Apresentação:* Ambos.

## 🚀 Instruções de Instalação e Execução
1. Clone o repositório:
   `git clone https://github.com/luisfaleiro/trabalho-grauB.git`
2. Instale as dependências:
   `pip install -r requirements.txt`
3. Execute a simulação completa:
   `python src/simulador.py`

## 📊 Resultados
*(Adicionar aqui os gráficos gerados e a tabela de compromisso após a conclusão)*

## 🎥 Vídeo de Demonstração
*(Adicionar o link do vídeo aqui)*


