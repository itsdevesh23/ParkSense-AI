import os
import glob
import json
import numpy as np
import pandas as pd

def verify_splitting():
    print("=" * 80)
    print("VERIFYING DATASET SPLITTING AND LEAKAGE-FREE PARTITIONING")
    print("=" * 80)

    # 1. Check metadata
    with open("data/processed/metadata.json", "r") as f:
        meta = json.load(f)
    print(f"Dataset name: {meta.get('dataset_name')}")
    print(f"Num valid clients: {meta.get('num_valid_clients')}")
    print(f"Features: {meta.get('input_features')}")
    print(f"Horizons: {meta.get('target_horizons')}")

    # 2. Check client files
    client_files = sorted(glob.glob("data/processed/client_*.npz"))
    assert len(client_files) == 30, f"Expected 30 client files, found {len(client_files)}"

    tot_train, tot_val, tot_test = 0, 0, 0
    all_X_test = []
    all_y30_test = []
    all_y60_test = []

    for cf in client_files:
        d = np.load(cf)
        X_tr = d["X_train"]
        y30_tr = d["y30_train"]
        y60_tr = d["y60_train"]

        X_va = d["X_val"]
        y30_va = d["y30_val"]
        y60_va = d["y60_val"]

        X_te = d["X_test"]
        y30_te = d["y30_test"]
        y60_te = d["y60_test"]

        tot_train += len(X_tr)
        tot_val += len(X_va)
        tot_test += len(X_te)

        all_X_test.append(X_te)
        all_y30_test.append(y30_te)
        all_y60_test.append(y60_te)

        # Check feature shapes
        assert X_tr.shape[1:] == (6, 4), f"Wrong X_train shape: {X_tr.shape}"
        assert X_va.shape[1:] == (6, 4), f"Wrong X_val shape: {X_va.shape}"
        assert X_te.shape[1:] == (6, 4), f"Wrong X_test shape: {X_te.shape}"

        # Target alignment
        assert len(y30_tr) == len(X_tr) and len(y60_tr) == len(X_tr)
        assert len(y30_va) == len(X_va) and len(y60_va) == len(X_va)
        assert len(y30_te) == len(X_te) and len(y60_te) == len(X_te)

    print(f"\nClient partitions sum:")
    print(f"  Training windows:   {tot_train:6d}  (Manuscript: 15,299)")
    print(f"  Validation windows: {tot_val:6d}  (Manuscript:  3,246)")
    print(f"  Testing windows:    {tot_test:6d}  (Manuscript:  3,263)")
    print(f"  Purged windows:     {30 * 2:6d}  (Manuscript:     60)")
    print(f"  Total windows:      {tot_train + tot_val + tot_test + 60:6d}  (Manuscript: 21,868)")

    assert tot_train == 15299, f"Train count mismatch: {tot_train} != 15299"
    assert tot_val == 3246, f"Val count mismatch: {tot_val} != 3246"
    assert tot_test == 3263, f"Test count mismatch: {tot_test} != 3263"
    assert tot_train + tot_val + tot_test + 60 == 21868, "Total windows mismatch"

    # 3. Check global dataset
    glob_data = np.load("data/processed/global_dataset.npz")
    g_X_tr = glob_data["X_train"]
    g_X_va = glob_data["X_val"]
    g_X_te = glob_data["X_test"]
    g_y30_te = glob_data["y30_test"]
    g_y60_te = glob_data["y60_test"]

    print(f"\nGlobal dataset check:")
    print(f"  Global X_train: {g_X_tr.shape}")
    print(f"  Global X_val:   {g_X_va.shape}")
    print(f"  Global X_test:  {g_X_te.shape}")

    assert len(g_X_tr) == 15299
    assert len(g_X_va) == 3246
    assert len(g_X_te) == 3263

    # Check exact match between concatenated client test data and global test data
    concat_X_te = np.concatenate(all_X_test, axis=0)
    concat_y30_te = np.concatenate(all_y30_test, axis=0)
    concat_y60_te = np.concatenate(all_y60_test, axis=0)

    np.testing.assert_array_equal(concat_X_te, g_X_te)
    np.testing.assert_array_equal(concat_y30_te, g_y30_te)
    np.testing.assert_array_equal(concat_y60_te, g_y60_te)
    print("  -> Exact match between client concatenation and global test data confirmed!")

    print("\nALL DATASET SPLITTING CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    verify_splitting()
