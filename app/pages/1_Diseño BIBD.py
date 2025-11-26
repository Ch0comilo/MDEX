import streamlit as st
import pandas as pd
from itertools import combinations
from collections import Counter

st.title("Modelo BIBD")

df = st.session_state.get("df")  # <--- Aquí pueden trabajar con un dataset existente si lo desean


# ----------------------------------------------------------------------
# --------------------------- BIBD GENERATOR ---------------------------
# ----------------------------------------------------------------------

def validate_parameters(v, k, lam):
    num = lam * v * (v - 1)
    den = k * (k - 1)
    if num % den != 0:
        raise ValueError("❌ b no es entero — parámetros no compatibles.")
    b = num // den

    if (lam * (v - 1)) % (k - 1) != 0:
        raise ValueError("❌ r no es entero — parámetros no compatibles.")
    r = (lam * (v - 1)) // (k - 1)

    if b * k != v * r:
        raise ValueError("❌ condición bk = vr no satisfecha.")

    return int(b), int(r)


def find_bibd(v, k, lam, max_iters=2_000_000):
    b, r = validate_parameters(v, k, lam)

    combos = list(combinations(range(v), k))
    combo_pairs = [tuple((min(a, b), max(a, b)) for a, b in combinations(c, 2)) for c in combos]

    pair_target = lam
    treat_target = r

    pair_count = Counter()
    treat_count = [0] * v
    solution_blocks = []

    iterations = 0

    def backtrack(start_idx, blocks_selected):
        nonlocal iterations
        iterations += 1
        if iterations > max_iters:
            return False

        if blocks_selected == b:
            # Validar solución completa
            if all(t == treat_target for t in treat_count) and \
               all(pair_count[p] == pair_target for p in pair_count):
                return True
            return False

        remaining = b - blocks_selected
        need_total = sum(max(0, treat_target - tc) for tc in treat_count)
        if need_total > remaining * k:
            return False

        for idx in range(start_idx, len(combos)):
            block = combos[idx]

            # No exceder r
            if any(treat_count[t] + 1 > treat_target for t in block):
                continue
            # No exceder lambda por par
            if any(pair_count[p] + 1 > pair_target for p in combo_pairs[idx]):
                continue

            solution_blocks.append(block)
            for t in block:
                treat_count[t] += 1
            for p in combo_pairs[idx]:
                pair_count[p] += 1

            if backtrack(idx, blocks_selected + 1):
                return True

            solution_blocks.pop()
            for t in block:
                treat_count[t] -= 1
            for p in combo_pairs[idx]:
                pair_count[p] -= 1

        return False

    if not backtrack(0, 0):
        raise RuntimeError("❌ No se encontró un BIBD válido. Cambia parámetros.")

    return {
        "v": v,
        "k": k,
        "lambda": lam,
        "b": b,
        "r": r,
        "blocks": solution_blocks
    }


def blocks_to_dataframe(bibd, labels=None):
    blocks = bibd["blocks"]
    v = bibd["v"]

    if labels is None:
        labels = [f"Tratamiento {i+1}" for i in range(v)]

    rows = []
    for bi, blk in enumerate(blocks, start=1):
        for t in blk:
            rows.append({
                "Block": bi,
                "Tratamiento_ID": chr(ord("A") + t),
                "Nombre": labels[t]
            })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# ------------------------------- UI ----------------------------------
# ----------------------------------------------------------------------

st.subheader("Parámetros del Diseño BIBD")

col1, col2, col3 = st.columns(3)
v = col1.number_input("Número de tratamientos (v)", min_value=2, value=5)
k = col2.number_input("Tamaño de cada bloque (k)", min_value=2, value=3)
lam = col3.number_input("Lambda (λ)", min_value=1, value=3)

if st.button("Generar Diseño BIBD"):
    try:
        bibd = find_bibd(v, k, lam)

        st.success(
            f"Diseño encontrado: "
            f"b={bibd['b']} bloques, r={bibd['r']} repeticiones por tratamiento"
        )

        # Si el usuario subió un df, intentar usar la primera columna como nombres
        if df is not None:
            labels = df.iloc[:, 0].astype(str).tolist()
        else:
            labels = None

        result_df = blocks_to_dataframe(bibd, labels)

        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar CSV del Diseño",
            csv,
            "bibd_design.csv",
            "text/csv"
        )

    except Exception as e:
        st.error(str(e))
