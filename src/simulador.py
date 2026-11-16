import numpy as np
import pandas as pd
import os
from transmissao_e_canais import (texto_para_bits, bits_para_texto, codificar_linha, 
                                  mapear_bpsk, mapear_qpsk, mapear_16qam, 
                                  canal_awgn, canal_burst_noise, plotar_comparacao_constelacoes, transmitir)
from recepcao_e_metricas import demodular, decodificar_ami, decodificar_manchester, calcular_ber, calcular_eficiencia_espectral

def executar_simulacao_ber(modulacao: str, cod_linha: str, snr_db: float, canal_tipo: str, bits_originais: np.ndarray):
    """Executa uma única rodada de simulação (sem reconstruir o texto para ser mais rápido)."""
    tamanho_original = len(bits_originais)
    
    # 2. Codificação de Linha
    if cod_linha:
        sinal_codificado = codificar_linha(bits_originais, cod_linha)
        if cod_linha.upper() == 'AMI':
            bits_para_modular = np.where(sinal_codificado != 0, 1, 0)
        elif cod_linha.upper() == 'MANCHESTER':
            bits_para_modular = np.where(sinal_codificado > 0, 1, 0)
    else:
        bits_para_modular = bits_originais
        
    # 3. Modulação
    if modulacao.upper() == 'BPSK':
        simbolos_limpos = mapear_bpsk(bits_para_modular)
    elif modulacao.upper() == 'QPSK':
        simbolos_limpos = mapear_qpsk(bits_para_modular)
    elif modulacao.upper() == '16-QAM':
        simbolos_limpos = mapear_16qam(bits_para_modular)
        
    # 4. Canal Ruidoso
    if canal_tipo.lower() == 'awgn':
        simbolos_ruidosos = canal_awgn(simbolos_limpos, snr_db=snr_db)
    else:
        simbolos_ruidosos = canal_burst_noise(simbolos_limpos, snr_db=snr_db)

    # 5 e 6. Demodulação e Decodificação
    bits_demodulados = demodular(simbolos_ruidosos, modulacao)
    
    if cod_linha:
        if cod_linha.upper() == 'AMI':
            bits_recebidos = decodificar_ami(bits_demodulados)
        elif cod_linha.upper() == 'MANCHESTER':
            bits_recebidos = decodificar_manchester(bits_demodulados)
    else:
        bits_recebidos = bits_demodulados
        
    # 7. Remover Padding
    bits_recebidos = bits_recebidos[:tamanho_original]
    
    # 8. Cálculo de BER
    return calcular_ber(bits_originais, bits_recebidos)

def executar_teste_consistencia():
    """
    Testar recuperação perfeita no canal ideal.
    Requisito do trabalho: testar recuperação perfeita no canal ideal.
    
    NOTA DE PROJETO (Por que usar uma mensagem curta aqui?):
    1. TESTE FUNCIONAL (Smoke Test): O objetivo deste teste NÃO é estatístico, 
       mas sim provar que a lógica da cadeia (Texto -> Modulação -> Canal Ideal -> 
       Demodulação -> Texto) está correta e sem bugs de padding ou decodificação.
    2. PERFORMANCE: Reconstruir o texto (função bits_para_texto) é um processo 
       lento em Python. Fazer isso com 100.000 bits em 480 testes deixaria o 
       script extremamente pesado. 
       
    A mensagem abaixo tem 43 caracteres (344 bits). A validação estatística 
    com os 100.000 bits exigidos pelo edital ocorre na bateria principal de testes.
    
    """
    print("\n=== TESTE DE CONSISTÊNCIA (Canal Ideal / SNR Alta) ===")
    mensagem = "Redes de Computadores - Teste de Validacao!"
    snr_ideal = 100.0 # Praticamente sem ruído
    
    bits_originais = texto_para_bits(mensagem)
    tamanho_original = len(bits_originais)
    
    combinacoes = [
        ('BPSK', 'AMI'), ('BPSK', 'MANCHESTER'),
        ('QPSK', 'AMI'), ('QPSK', 'MANCHESTER'),
        ('16-QAM', 'AMI'), ('16-QAM', 'MANCHESTER')
    ]
    
    sucesso_total = True
    for mod, cod in combinacoes:
        # Roda a cadeia completa internamente
        sinal_codificado = codificar_linha(bits_originais, cod)
        if cod == 'AMI':
            bits_para_modular = np.where(sinal_codificado != 0, 1, 0)
        else:
            bits_para_modular = np.where(sinal_codificado > 0, 1, 0)
            
        if mod == 'BPSK': simbolos_limpos = mapear_bpsk(bits_para_modular)
        elif mod == 'QPSK': simbolos_limpos = mapear_qpsk(bits_para_modular)
        else: simbolos_limpos = mapear_16qam(bits_para_modular)
        
        simbolos_ruidosos = canal_awgn(simbolos_limpos, snr_db=snr_ideal)
        bits_demodulados = demodular(simbolos_ruidosos, mod)
        
        if cod == 'AMI': bits_recebidos = decodificar_ami(bits_demodulados)
        else: bits_recebidos = decodificar_manchester(bits_demodulados)
            
        bits_recebidos = bits_recebidos[:tamanho_original]
        
        texto_reconstruido = bits_para_texto(bits_recebidos)
        ber = calcular_ber(bits_originais, bits_recebidos)
        
        if texto_reconstruido == mensagem and ber == 0.0:
            print(f"[OK] {mod:<6} | {cod:<10} | BER: {ber}")
        else:
            print(f"[FALHA] {mod:<6} | {cod:<10} | Texto voltou: {texto_reconstruido}")
            sucesso_total = False
            
    if sucesso_total:
        print("=== TESTE DE CONSISTÊNCIA PASSOU! ===\n")
    else:
        print("=== ATENÇÃO: FALHA NO TESTE DE CONSISTÊNCIA! ===\n")

if __name__ == "__main__":
    # Chama o teste de consistência logo no início
    executar_teste_consistencia()

    print("=== INICIANDO AUTOMAÇÃO DE TESTES (ITEM 10) ===")
    
    # 1. Gerar uma mensagem longa para garantir 100.000 bits
    # (12500 caracteres ASCII = 100.000 bits)
    texto_longo = "".join(np.random.choice(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "), 12500))
    bits_originais = texto_para_bits(texto_longo)
    
    # Parâmetros do experimento
    snrs = [-2, 0, 2, 4, 6, 8, 10, 12] # 8 valores de SNR
    repeticoes = 5
    modulacoes = ['BPSK', 'QPSK', '16-QAM']
    codificacoes = ['AMI', 'MANCHESTER']
    canais = ['awgn', 'burst']
    
    resultados = []
    
    # Loop de Simulação
    for canal in canais:
        for modulacao in modulacoes:
            for cod_linha in codificacoes:
                eficiencia = calcular_eficiencia_espectral(modulacao, cod_linha)
                
                for snr in snrs:
                    bers = []
                    for rep in range(repeticoes):
                        ber = executar_simulacao_ber(modulacao, cod_linha, snr, canal, bits_originais)
                        bers.append(ber)
                        
                    # Estatísticas
                    ber_medio = np.mean(bers)
                    ber_std = np.std(bers)
                    
                    # Salva no formato de lista
                    resultados.append({
                        'Canal': canal,
                        'Modulacao': modulacao,
                        'Codificacao': cod_linha,
                        'SNR_dB': snr,
                        'Eficiencia_Esp': eficiencia,
                        'BER_Media': ber_medio,
                        'BER_Desvio_Padrao': ber_std
                    })
                    print(f"Canal: {canal.upper():<5} | Mod: {modulacao:<6} | Cod: {cod_linha:<10} | SNR: {snr:>3} dB | BER Média: {ber_medio:.5f} +/- {ber_std:.5f}")

    # 2. Preparar diretórios e salvar os dados brutos em CSV
    df = pd.DataFrame(resultados)
    
    # Descobre a pasta raiz do projeto dinamicamente
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(diretorio_script)
    
    # Garantir que as pastas de resultados existam
    diretorio_saida = os.path.join(raiz_projeto, "resultados", "dados_brutos")
    diretorio_figuras = os.path.join(raiz_projeto, "resultados", "figuras")
    os.makedirs(diretorio_saida, exist_ok=True)
    os.makedirs(diretorio_figuras, exist_ok=True)
    
    # Salvar o CSV
    caminho_csv = os.path.join(diretorio_saida, "resultados_simulacao.csv")
    df.to_csv(caminho_csv, index=False)
    print(f"\nDados salvos com sucesso em: {caminho_csv}")

    # 3. Gerar e Salvar Gráficos de Constelação (Item 6 do trabalho)
    print("\nGerando e salvando gráficos de constelação...")
    modulacoes_constelacao = ['BPSK', 'QPSK', '16-QAM']
    
    for mod in modulacoes_constelacao:
        # Gerar símbolos limpos
        simbolos_limpos = transmitir("Teste de Constelacao", modulacao=mod, cod_linha='AMI')
        
        # Passar pelo canal AWGN (SNR de 12 dB para ficar visível)
        simbolos_awgn = canal_awgn(simbolos_limpos, snr_db=12.0)
        
        # Salvar o gráfico
        nome_arquivo = f"constelacao_{mod.replace('-', '')}_awgn.png"
        caminho_figura = os.path.join(diretorio_figuras, nome_arquivo)
        
        plotar_comparacao_constelacoes(
            simbolos_limpos, 
            simbolos_awgn, 
            f"Constelacao {mod} sob AWGN (12 dB)", 
            caminho_salvar=caminho_figura
        )
        print(f"Constelacao salva: {caminho_figura}")

    print("\n=== SIMULAÇÃO CONCLUÍDA COM SUCESSO! ===")