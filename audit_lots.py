import pandas as pd
import glob
import numpy as np

df = pd.read_csv('data/dataset.csv')
print('=== RAW DATASET PER LOT ===')
counts = df.groupby('SystemCodeNumber').size()
for name, c in counts.items():
    if c < 500:
        print(f"Raw lot {name}: count={c}")

print('\n=== ALL PROCESSED CLIENT NPZ SAMPLES ===')
train_tot = 0
val_tot = 0
test_tot = 0
for f in sorted(glob.glob('data/processed/client_*.npz')):
    d = np.load(f)
    name = f.split('client_')[-1].replace('.npz', '')
    tr = len(d['y30_train'])
    va = len(d['y30_val'])
    te = len(d['y30_test'])
    train_tot += tr
    val_tot += va
    test_tot += te
    if tr < 300 or te < 50:
        print(f"{name}: train={tr}, val={va}, test={te}, cap={d['capacity']}")

print(f"TOTAL: train={train_tot}, val={val_tot}, test={test_tot}, all={train_tot+val_tot+test_tot}")
