import time, warnings, multiprocessing
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
warnings.filterwarnings('ignore')

def eval_arima_single(series):
    try:
        res = ARIMA(series, order=(2, 1, 1)).fit()
        fc = res.forecast(steps=2)
        return float(np.clip(fc[0], 0, 1)), float(np.clip(fc[1], 0, 1))
    except:
        lv = float(series[-1])
        return lv, lv

if __name__ == '__main__':
    data = np.load('data/processed/global_dataset.npz')
    X_test = data['X_test']
    print(f'Total test samples: {len(X_test)}')
    series_list = [X_test[i, :, 0] for i in range(100)]
    t0 = time.time()
    with multiprocessing.Pool(processes=8) as pool:
        preds = pool.map(eval_arima_single, series_list)
    dt = time.time() - t0
    print(f'100 samples took {dt:.2f}s ({dt/100:.3f}s per sample) using 8 processes')
    est_total = (dt / 100) * len(X_test)
    print(f'Projected full run ({len(X_test)} samples): {est_total:.1f}s (~{est_total/60:.1f} minutes)')
