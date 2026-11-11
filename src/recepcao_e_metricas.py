import numpy as np

# ==========================================
# 7. DEMODULAÇÃO (Detector de Mínima Distância Euclidiana)
# ==========================================

def demodular_bpsk(simbolos: np.ndarray) -> np.ndarray:
    """Detecta BPSK olhando para o eixo Real (esquerda = 0, direita = 1)."""
    return np.where(simbolos.real > 0, 1, 0)

def demodular_qpsk(simbolos: np.ndarray) -> np.ndarray:
    """Detecta QPSK baseado nos quadrantes (eixos Real e Imaginário)."""
    bits = []
    for s in simbolos:
        # No código do Leonardo: b0 é a parte real, b1 é a imaginária
        b0 = 1 if s.real > 0 else 0
        b1 = 1 if s.imag > 0 else 0
        bits.extend([b0, b1])
    return np.array(bits, dtype=int)

def demodular_16qam(simbolos: np.ndarray) -> np.ndarray:
    """Detecta 16-QAM calculando a distância euclidiana para os 16 pontos ideais."""
    # Mapeamento definido no código do Leonardo: {(0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3}
    mapa_bits = {(0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3}
    
    # Gera os 16 pontos ideais (normalizados por raiz de 10, como ele fez)
    fator_normalizacao = np.sqrt(10)
    constelacao_ideal = []
    
    # Reverter o dicionário para ter bits como chave e símbolo como valor
    for (b_real, b_imag), val_real in mapa_bits.items():
        for (b2_real, b2_imag), val_imag in mapa_bits.items():
            # Monta o símbolo complexo normalizado
            simbolo = complex(val_real, val_imag) / fator_normalizacao
            # Salva os 4 bits (b_real, b_imag, b2_real, b2_imag)
            bits = [b_real, b_imag, b2_real, b2_imag]
            constelacao_ideal.append((simbolo, bits))
            
    bits_demodulados = []
    for s in simbolos:
        # Calcula a distância para todos os 16 pontos
        distancias = [np.abs(s - ponto[0]) for ponto in constelacao_ideal]
        # Pega o índice do ponto mais próximo
        idx_mais_proximo = np.argmin(distancias)
        # Adiciona os bits correspondentes
        bits_demodulados.extend(constelacao_ideal[idx_mais_proximo][1])
        
    return np.array(bits_demodulados, dtype=int)

def demodular(simbolos: np.ndarray, modulacao: str) -> np.ndarray:
    """Função wrapper para chamar a demodulação correta."""
    modulacao = modulacao.upper()
    if modulacao == 'BPSK':
        return demodular_bpsk(simbolos)
    elif modulacao == 'QPSK':
        return demodular_qpsk(simbolos)
    elif modulacao == '16-QAM':
        return demodular_16qam(simbolos)
    else:
        raise ValueError("Modulação inválida! Use 'BPSK', 'QPSK' ou '16-QAM'.")


# ==========================================
# 8. DECODIFICAÇÃO DE LINHA
# ==========================================

def decodificar_ami(simbolos_ou_bits: np.ndarray) -> np.ndarray:
    """
    Decodifica AMI. 
    ATENÇÃO: No código atual do Leonardo, a função 'transmitir' transforma -1 em 0 
    antes de modular. Se você passar os bits demodulados aqui, +1 vira 1 e 0/-1 viram 0.
    """
    # Se for o sinal físico (com -1, 0, 1), mapeia -1 e +1 para 1, e 0 para 0.
    # Se já for bits (0 e 1), o np.abs() resolve, pois abs(-1) = 1 e abs(0) = 0.
    return np.where(np.abs(simbolos_ou_bits) > 0, 1, 0)

def decodificar_manchester(bits: np.ndarray) -> np.ndarray:
    """
    Decodifica Manchester.
    O código do Leonardo usa: 0 -> [1, -1] (bits 1, 0) e 1 -> [-1, 1] (bits 0, 1).
    Portanto, a sequência [1, 0] vira bit 0, e [0, 1] vira bit 1.
    """
    bits_decodificados = []
    for i in range(0, len(bits), 2):
        if i + 1 < len(bits):
            par = (bits[i], bits[i+1])
            if par == (1, 0):
                bits_decodificados.append(0)
            elif par == (0, 1):
                bits_decodificados.append(1)
            else:
                # Em caso de erro no canal, assume 0 (ou poderíamos fazer outra lógica)
                bits_decodificados.append(0) 
    return np.array(bits_decodificados, dtype=int)

# ==========================================
# 9. CÁLCULO DE MÉTRICAS ESTATÍSTICAS
# ==========================================

def calcular_ber(bits_transmitidos: np.ndarray, bits_recebidos: np.ndarray) -> float:
    """
    Calcula a Taxa de Erro de Bits (BER).
    Nota: Os arrays precisam ter o mesmo tamanho. Se houver padding, 
    corte o array recebido antes de chamar esta função no simulador.
    """
    if len(bits_transmitidos) != len(bits_recebidos):
        # Proteção para garantir que estamos comparando o mesmo número de bits
        min_len = min(len(bits_transmitidos), len(bits_recebidos))
        bits_transmitidos = bits_transmitidos[:min_len]
        bits_recebidos = bits_recebidos[:min_len]
        
    erros = np.sum(bits_transmitidos != bits_recebidos)
    return erros / len(bits_transmitidos)

def calcular_eficiencia_espectral(modulacao: str, cod_linha: str = None) -> float:
    """
    Retorna a Eficiência Espectral Nominal em bits/s/Hz.
    Considera a quantidade de bits por símbolo e a penalidade da codificação de linha.
    """
    modulacao = modulacao.upper()
    
    # Bits por símbolo nominal
    if modulacao == 'BPSK':
        eficiencia = 1.0
    elif modulacao == 'QPSK':
        eficiencia = 2.0
    elif modulacao == '16-QAM':
        eficiencia = 4.0
    else:
        raise ValueError("Modulação inválida.")

    # Penalidade de codificação de linha
    if cod_linha and cod_linha.upper() == 'MANCHESTER':
        # Manchester gasta 2 símbolos para transmitir 1 bit, logo a eficiência cai pela metade
        eficiencia = eficiencia / 2.0
        
    return eficiencia