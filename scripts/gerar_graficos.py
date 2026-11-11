import pandas as pd
import matplotlib.pyplot as plt
import os

def gerar_graficos():
    # 1. Configurar caminhos absolutos
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(diretorio_script)
    
    caminho_csv = os.path.join(raiz_projeto, "resultados", "dados_brutos", "resultados_simulacao.csv")
    diretorio_figuras = os.path.join(raiz_projeto, "resultados", "figuras")
    
    os.makedirs(diretorio_figuras, exist_ok=True)
    
    # 2. Ler os dados
    print("Lendo dados do CSV...")
    df = pd.read_csv(caminho_csv)
    
    # 3. Definir estilos visuais para diferenciar as curvas
    estilos = {
        ('BPSK', 'AMI'): {'color': 'blue', 'marker': 'o', 'linestyle': '-'},
        ('BPSK', 'MANCHESTER'): {'color': 'blue', 'marker': 's', 'linestyle': '--'},
        ('QPSK', 'AMI'): {'color': 'green', 'marker': '^', 'linestyle': '-'},
        ('QPSK', 'MANCHESTER'): {'color': 'green', 'marker': 'v', 'linestyle': '--'},
        ('16-QAM', 'AMI'): {'color': 'red', 'marker': 'D', 'linestyle': '-'},
        ('16-QAM', 'MANCHESTER'): {'color': 'red', 'marker': 'x', 'linestyle': '--'}
    }
    
    canais = ['awgn', 'burst']
    
    # 4. Gerar um gráfico para cada canal
    for canal in canais:
        plt.figure(figsize=(10, 6))
        
        # Filtrar dados do canal atual
        df_canal = df[df['Canal'] == canal]
        
        # Plotar cada combinação de Modulação + Codificação
        for modulacao in ['BPSK', 'QPSK', '16-QAM']:
            for codificacao in ['AMI', 'MANCHESTER']:
                df_curva = df_canal[(df_canal['Modulacao'] == modulacao) & (df_canal['Codificacao'] == codificacao)]
                
                if df_curva.empty:
                    continue
                
                snr = df_curva['SNR_dB']
                ber_media = df_curva['BER_Media']
                ber_std = df_curva['BER_Desvio_Padrao']
                
                # Evitar problemas com log(0) nas barras de erro se a média ou std for 0
                # (Adicionamos um valor minúsculo apenas para o plot não reclamar)
                ber_media_plot = ber_media.replace(0, 1e-7)
                ber_std_plot = ber_std.replace(0, 1e-7)
                
                estilo = estilos[(modulacao, codificacao)]
                
                plt.errorbar(
                    snr, 
                    ber_media_plot, 
                    yerr=ber_std_plot, 
                    label=f"{modulacao} - {codificacao}", 
                    capsize=4,
                    elinewidth=1,
                    markeredgewidth=1,
                    **estilo
                )
        
        # 5. Configurações do Gráfico
        plt.yscale('log')
        plt.title(f"Curvas de BER vs SNR - Canal {canal.upper()}", fontsize=14, fontweight='bold')
        plt.xlabel("SNR (dB)", fontsize=12)
        plt.ylabel("Bit Error Rate (BER)", fontsize=12)
        plt.grid(True, which="both", ls="--", alpha=0.5)
        
        # Legenda fora do gráfico para não cobrir as linhas
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # 6. Salvar a figura
        nome_arquivo = f"ber_vs_snr_{canal}.png"
        caminho_figura = os.path.join(diretorio_figuras, nome_arquivo)
        plt.savefig(caminho_figura, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Gráfico salvo: {caminho_figura}")

if __name__ == "__main__":
    print("=== GERANDO GRÁFICOS DE BER x SNR ===")
    gerar_graficos()
    print("=== CONCLUÍDO! Verifique a pasta 'resultados/figuras'. ===")