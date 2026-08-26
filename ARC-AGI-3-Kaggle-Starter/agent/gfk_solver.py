import numpy as np
from typing import Optional
from itertools import product as iterproduct


def gfk_solve(toggle_matrix: np.ndarray, target: np.ndarray, k: int) -> Optional[np.ndarray]:
    n = len(target)
    M = toggle_matrix.copy() % k
    t = target.copy() % k
    if k in [2, 3]:
        return _gaussian_elimination_prime_k(M, t, k, n)
    elif k == 4:
        if n <= 8:
            return _brute_force_zk(M, t, k, n)
        else:
            return _gaussian_elimination_z4(M, t, n)
    else:
        if n <= 6:
            return _brute_force_zk(M, t, k, n)
        return None


def _gaussian_elimination_prime_k(M: np.ndarray, t: np.ndarray, k: int, n: int) -> Optional[np.ndarray]:
    aug = np.hstack([M, t.reshape(-1, 1)]) % k
    pivot_row = 0
    for col in range(n):
        pivot = None
        for row in range(pivot_row, n):
            if aug[row, col] % k != 0:
                pivot = row
                break
        if pivot is None:
            continue
        aug[[pivot_row, pivot]] = aug[[pivot, pivot_row]]
        inv = _mod_inverse(int(aug[pivot_row, col]), k)
        if inv is None:
            return None
        aug[pivot_row] = (aug[pivot_row] * inv) % k
        for row in range(n):
            if row == pivot_row:
                continue
            factor = aug[row, col]
            aug[row] = (aug[row] - factor * aug[pivot_row]) % k
        pivot_row += 1
    solution = np.zeros(n, dtype=int)
    for row in range(n - 1, -1, -1):
        pivot_col = None
        for col in range(n):
            if aug[row, col] != 0:
                pivot_col = col
                break
        if pivot_col is None:
            continue
        solution[pivot_col] = int(aug[row, n]) % k
    check = (M @ solution) % k
    if not np.array_equal(check, t % k):
        return None
    return solution


def _mod_inverse(a: int, k: int) -> Optional[int]:
    for x in range(1, k):
        if (a * x) % k == 1:
            return x
    return None


def _brute_force_zk(M: np.ndarray, t: np.ndarray, k: int, n: int) -> Optional[np.ndarray]:
    for x in iterproduct(range(k), repeat=n):
        xv = np.array(x)
        if np.array_equal((M @ xv) % k, t % k):
            return xv
    return None


def _gaussian_elimination_z4(M: np.ndarray, t: np.ndarray, n: int) -> Optional[np.ndarray]:
    sol_mod2 = _gaussian_elimination_prime_k(M % 2, t % 2, 2, n)
    if sol_mod2 is not None:
        for adjustment in range(2**n):
            candidate = sol_mod2 + 2 * np.array([(adjustment >> i) & 1 for i in range(n)])
            if np.array_equal((M @ candidate) % 4, t % 4):
                return candidate
    return None
