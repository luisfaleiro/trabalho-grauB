import pandas as pd
import os

def gerar_tabela_compromisso(snr_alvo=10):
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.dirname(diretorio_script)
    caminho_csv = os.path.join(raiz_projeto, "resultados", "dados_brutos", "resultados_simulacao.csv")
    
    df = pd.read_csv(caminho_csv)
    
    # Filtrar apenas pelo canal AWGN e pela SNR alvo
    df_filtrado = df[(df['Canal'] == 'awgn') & (df['SNR_dB'] == snr_alvo)]
    
    # Agrupar por modulação e codificação para pegar os valores
    tabela = df_filtrado[['Modulacao', 'Codificacao', 'Eficiencia_Esp', 'BER_Media']].copy()
    
    # Formatar a BER para notação científica (ex: 4.00e-06)
    tabela['BER_Media'] = tabela['BER_Media'].apply(lambda x: f"{x:.2e}")
    
    # Renomear colunas para ficar bonito em português
    tabela.columns = ['Modulação', 'Codificação', 'Eficiência Espectral (bits/s/Hz)', 'BER Média']
    
    # Gerar a tabela em formato Markdown
    print(f"\n=== TABELA DE COMPROMISSO (Canal AWGN, SNR = {snr_alvo} dB) ===\n")
    print(tabela.to_markdown(index=False))
    
    # Salvar a tabela em um arquivo de texto para facilitar o copiar/colar
    caminho_tabela = os.path.join(raiz_projeto, "resultados", "tabela_compromisso.md")
    with open(caminho_tabela, 'w', encoding='utf-8') as f:
        f.write(f"### Tabela de Compromisso (Canal AWGN, SNR = {snr_alvo} dB)\n\n")
        f.write(tabela.to_markdown(index=False))
        
    print(f"\nTabela salva em: {caminho_tabela}")

if __name__ == "__main__":
    # Para usar o to_markdown, precisamos da biblioteca tabulate
    # Se der erro, rode no terminal: pip install tabulate
    gerar_tabela_compromisso(snr_alvo=10)