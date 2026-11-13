import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. CONVERSÃO DE DADOS (ASCII <-> BITS)
# ==========================================
def texto_para_bits(texto: str) -> np.ndarray:
    """Converte texto ASCII para um vetor de bits (0s e 1s)."""
    bits = []
    for char in texto:
        bin_char = format(ord(char), '08b')
        bits.extend([int(b) for b in bin_char])
    return np.array(bits, dtype=int)

def bits_para_texto(bits: np.ndarray) -> str:
    """Converte vetor de bits de volta para string ASCII."""
    pad_len = (8 - (len(bits) % 8)) % 8
    if pad_len > 0:
        bits = np.pad(bits, (0, pad_len), 'constant')
    
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        char_code = int("".join(map(str, byte)), 2)
        chars.append(chr(char_code))
    return "".join(chars)


# ==========================================
# 2. CODIFICAÇÃO DE LINHA
# ==========================================
def codificar_linha(bits: np.ndarray, algoritmo: str) -> np.ndarray:
    """
    Aplica codificação de linha aos bits.
    - AMI: 0 -> 0, 1 -> alternado (+1, -1)
    - MANCHESTER: 0 -> [+1, -1], 1 -> [-1, +1]
    """
    algoritmo = algoritmo.upper()
    
    if algoritmo == 'AMI':
        sinal = np.zeros(len(bits), dtype=int)
        polaridade = 1
        for i, bit in enumerate(bits):
            if bit == 1:
                sinal[i] = polaridade
                polaridade *= -1
        return sinal

    elif algoritmo == 'MANCHESTER':
        sinal = []
        for bit in bits:
            if bit == 0:
                sinal.extend([1, -1])
            else:
                sinal.extend([-1, 1])
        return np.array(sinal, dtype=int)
    
    else:
        raise ValueError("Codificação de linha inválida! Use 'AMI' ou 'MANCHESTER'.")


# ==========================================
# 3. MODULAÇÃO DIGITAL (Es = 1 Exato)
# ==========================================
def mapear_bpsk(bits: np.ndarray) -> np.ndarray:
    """BPSK: 0 -> -1 + 0j, 1 -> +1 + 0j (Es = 1)"""
    sinais = np.where(bits == 1, 1.0, -1.0)
    return sinais.astype(np.complex128)

def mapear_qpsk(bits: np.ndarray) -> np.ndarray:
    """QPSK: Agrupa em pares de bits com Es = 1"""
    bits_work = bits.copy()
    if len(bits_work) % 2 != 0:
        bits_work = np.append(bits_work, 0)
        
    simbolos = []
    fator = 1.0 / np.sqrt(2)
    
    for i in range(0, len(bits_work), 2):
        b0, b1 = bits_work[i], bits_work[i+1]
        real = fator if b0 == 1 else -fator
        imag = fator if b1 == 1 else -fator
        simbolos.append(complex(real, imag))
        
    return np.array(simbolos, dtype=np.complex128)

def mapear_16qam(bits: np.ndarray) -> np.ndarray:
    """16-QAM: Agrupa em quadras (4 bits) com Es = 1 exato"""
    bits_work = bits.copy()
    pad_len = (4 - (len(bits_work) % 4)) % 4
    if pad_len > 0:
        bits_work = np.pad(bits_work, (0, pad_len), 'constant')
        
    mapa_2bits = {(0,0): -3, (0,1): -1, (1,1): 1, (1,0): 3}
    simbolos = []
    
    for i in range(0, len(bits_work), 4):
        b_real = tuple(bits_work[i:i+2])
        b_imag = tuple(bits_work[i+2:i+4])
        
        real = mapa_2bits[b_real]
        imag = mapa_2bits[b_imag]
        simbolos.append(complex(real, imag))
        
    simbolos = np.array(simbolos, dtype=np.complex128)
    energia_media = np.mean(np.abs(simbolos)**2)
    return simbolos / np.sqrt(energia_media)


# ==========================================
# 4. FUNÇÃO PRINCIPAL DE TRANSMISSÃO
# ==========================================
def transmitir(dados, modulacao: str, cod_linha: str = None) -> np.ndarray:
    """
    Interface principal do Transmissor (Leonardo).
    Aceita 'dados' como string (texto) ou np.ndarray (vetor de bits).
    """
    if isinstance(dados, str):
        bits = texto_para_bits(dados)
    else:
        bits = np.array(dados, dtype=int)
    
    # Aplica codificação de linha se solicitada
    if cod_linha:
        # Retorna o sinal codificado em linha diretamente para transmissão em banda base
        sinal_linha = codificar_linha(bits, cod_linha)
        # Se for modular em RF depois da linha, mapeia valores de nível para bits limpos
        if cod_linha.upper() == 'AMI':
            # Para AMI: -1 e 1 são pulsos (bit 1), 0 é ausência (bit 0)
            bits_finais = np.where(sinal_linha != 0, 1, 0)
        else:
            bits_finais = np.where(sinal_linha > 0, 1, 0)
    else:
        bits_finais = bits

    modulacao = modulacao.upper()
    if modulacao == 'BPSK':
        return mapear_bpsk(bits_finais)
    elif modulacao == 'QPSK':
        return mapear_qpsk(bits_finais)
    elif modulacao == '16-QAM':
        return mapear_16qam(bits_finais)
    else:
        raise ValueError("Modulação inválida! Use 'BPSK', 'QPSK' ou '16-QAM'.")


# ==========================================
# 5. MODELAGEM DOS CANAIS
# ==========================================
def canal_awgn(simbolos: np.ndarray, snr_db: float) -> np.ndarray:
    """Adiciona Ruído Gaussiano Branco Aditivo (AWGN) com SNR em dB (Es = 1)."""
    snr_linear = 10.0 ** (snr_db / 10.0)
    sigma = np.sqrt(1.0 / (2.0 * snr_linear))
    
    ruido_real = np.random.normal(0, sigma, len(simbolos))
    ruido_imag = np.random.normal(0, sigma, len(simbolos))
    
    return simbolos + (ruido_real + 1j * ruido_imag)

def canal_burst_noise(simbolos: np.ndarray, snr_db: float, prob_rajada: float = 0.05, fator_degradacao: float = 5.0) -> np.ndarray:
    """Adiciona Ruído em Rajadas (Burst Noise)."""
    simbolos_ruidosos = canal_awgn(simbolos, snr_db)
    
    mascara_rajada = np.random.rand(len(simbolos)) < prob_rajada
    if np.any(mascara_rajada):
        snr_rajada_db = snr_db - (10 * np.log10(fator_degradacao))
        ruido_rajada = canal_awgn(simbolos[mascara_rajada], snr_rajada_db) - simbolos[mascara_rajada]
        simbolos_ruidosos[mascara_rajada] += ruido_rajada
    
    return simbolos_ruidosos


# ==========================================
# 6. PLOT COMPARATIVO DAS CONSTELAÇÕES
# ==========================================
def plotar_comparacao_constelacoes(simbolos_limpos: np.ndarray, simbolos_ruidosos: np.ndarray, titulo: str, caminho_salvar: str = None):
    """Plota diagrama de constelação. Permite salvar em arquivo sem travar o script."""
    plt.figure(figsize=(7, 7))
    plt.scatter(simbolos_ruidosos.real, simbolos_ruidosos.imag, color='red', alpha=0.5, s=20, label='Com Ruído (Pós-Canal)')
    plt.scatter(simbolos_limpos.real, simbolos_limpos.imag, color='blue', marker='o', s=60, edgecolors='black', label='Limpo (Transmissor)')
    
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    plt.title(titulo)
    plt.xlabel('In-Phase (I)')
    plt.ylabel('Quadrature (Q)')
    plt.legend()
    plt.tight_layout()
    
    if caminho_salvar:
        plt.savefig(caminho_salvar, dpi=300)
        plt.close()
    else:
        plt.show()


# ==========================================
# TESTE COMPLETO
# ==========================================
if __name__ == "__main__":
    mensagem_teste = "Redes de Computadores UNISINOS 2026 - Teste Completo"
    print(f"Mensagem Original: '{mensagem_teste}'")
    
    simbolos_16qam = transmitir(mensagem_teste, modulacao='16-QAM')
    print(f"Total de Símbolos 16-QAM Gerados: {len(simbolos_16qam)}")
    print(f"Energia Média: {np.mean(np.abs(simbolos_16qam)**2):.4f}")
    
    snr_teste = 12.0
    sinal_awgn = canal_awgn(simbolos_16qam, snr_db=snr_teste)
    sinal_burst = canal_burst_noise(simbolos_16qam, snr_db=snr_teste)
    
    plotar_comparacao_constelacoes(simbolos_16qam, sinal_awgn, f"Constelação 16-QAM sob AWGN ({snr_teste} dB)")