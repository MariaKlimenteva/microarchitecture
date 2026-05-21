import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gmean

def parse_results(results_dir):
    data = []
    # Pattern to extract IPC and MPKI
    ipc_pattern = re.compile(r"CPU 0 cumulative IPC: (\d+\.?\d*)")
    mpki_pattern = re.compile(r"MPKI: (\d+\.?\d*)")

    for filename in os.listdir(results_dir):
        if not filename.endswith(".txt"):
            continue
        
        # Filename format: {predictor}_{trace}.txt
        parts = filename.split('_')
        if len(parts) < 2:
            continue
        
        predictor = parts[0]
        # Extract trace name - everything after predictor and before .txt
        trace_full = '_'.join(parts[1:])[:-4]
        # Shorten trace name like in the example (e.g., 600.perlbench_s)
        trace_match = re.search(r"^([0-9]+\.[a-zA-Z0-9_]+)", trace_full)
        trace = trace_match.group(1) if trace_match else trace_full

        file_path = os.path.join(results_dir, filename)
        ipc = None
        mpki = None
        
        with open(file_path, 'r') as f:
            content = f.read()
            ipc_match = ipc_pattern.search(content)
            mpki_match = mpki_pattern.search(content)
            
            if ipc_match:
                ipc = float(ipc_match.group(1))
            if mpki_match:
                mpki = float(mpki_match.group(1))
        
        if ipc is not None and mpki is not None:
            data.append({
                'Predictor': predictor,
                'Trace': trace,
                'IPC': ipc,
                'MPKI': mpki
            })
    
    return pd.DataFrame(data)

def main():
    results_dir = 'hw_2/results'
    if not os.path.exists(results_dir):
        print(f"Directory {results_dir} not found.")
        return

    df = parse_results(results_dir)
    if df.empty:
        print("No data parsed.")
        return

    # Pivot for detailed table
    detailed_ipc = df.pivot(index='Trace', columns='Predictor', values='IPC')
    detailed_mpki = df.pivot(index='Trace', columns='Predictor', values='MPKI')
    
    # Merge for the final detailed table
    detailed_table = detailed_ipc.copy()
    detailed_table.columns = [f'IPC_{c}' for c in detailed_ipc.columns]
    for col in detailed_mpki.columns:
        detailed_table[f'MPKI_{col}'] = detailed_mpki[col]
    
    # Reorder columns to group by predictor if needed, or follow user example
    predictors = sorted(df['Predictor'].unique())
    col_order = []
    for pred in predictors:
        col_order.extend([f'IPC_{pred}', f'MPKI_{pred}'])
    detailed_table = detailed_table[col_order]

    print("\nБолее подробные результаты:")
    print(detailed_table.to_string())
    detailed_table.to_csv('hw_2/final_table.txt', sep='\t')

    # Calculate GMEAN
    # Note: GMEAN doesn't handle 0 well. MPKI can be 0 or very close to 0.
    # We add a tiny epsilon if needed, but here we just use gmean from scipy.
    summary_data = []
    for pred in predictors:
        pred_df = df[df['Predictor'] == pred]
        # ChampSim sometimes reports 0 MPKI for some traces, which breaks gmean
        # Using a small value for 0 to allow gmean calculation
        ipcs = pred_df['IPC'].values
        mpkis = pred_df['MPKI'].values
        mpkis[mpkis == 0] = 1e-6 
        
        summary_data.append({
            'Модель': pred.capitalize(),
            'IPC': gmean(ipcs),
            'MPKI': gmean(mpkis)
        })
    
    summary_df = pd.DataFrame(summary_data)
    print("\nОбщие результаты (GMEAN):")
    print(summary_df.to_string(index=False))

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # IPC plot
    detailed_ipc.plot(kind='bar', ax=ax1)
    ax1.set_title('IPC per Trace')
    ax1.set_ylabel('IPC')
    ax1.legend(title='Predictor')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # MPKI plot
    detailed_mpki.plot(kind='bar', ax=ax2)
    ax2.set_title('MPKI per Trace')
    ax2.set_ylabel('MPKI')
    ax2.legend(title='Predictor')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('hw_2/results_plot.png')
    print("\nГрафик сохранен в hw_2/results_plot.png")

if __name__ == "__main__":
    main()
