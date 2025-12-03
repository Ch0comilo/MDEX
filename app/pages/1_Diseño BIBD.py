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


# Parámetros fijos — editar aquí si quieres cambiarlos manualmente
v = 5
k = 3
lam = 3


# Generar automáticamente el diseño cuando el DataFrame esté presente
if df is None:
    st.info("Sube un CSV en la página principal para generar automáticamente el BIBD.")
else:
    try:
        bibd = find_bibd(v, k, lam)

        st.success("Diseño BIBD generado automáticamente ✅")

        # Mostrar parámetros en recuadros
        st.markdown("### Parámetros del diseño")
        p1, p2, p3 = st.columns(3)
        p1.metric("Tratamientos (v)", str(bibd["v"]))
        p2.metric("Tamaño de bloque (k)", str(bibd["k"]))
        p3.metric("Lambda (λ)", str(bibd["lambda"]))

        p4, p5 = st.columns(2)
        p4.metric("Bloques (b)", str(bibd["b"]))
        p5.metric("Repeticiones por tratamiento (r)", str(bibd["r"]))

        st.caption("Parámetros calculados del diseño (fijos para este BIBD).")

        # Intentar usar la primera columna del df como nombres si está disponible
        labels = df.iloc[:, 0].astype(str).tolist() if df is not None else None

        result_df = blocks_to_dataframe(bibd, labels)

        st.subheader("Bloques del diseño")
        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar CSV del Diseño",
            csv,
            "bibd_design.csv",
            "text/csv",
        )

    except Exception as e:
        st.error(str(e))


import streamlit as st
import pandas as pd
from itertools import combinations
from collections import Counter

st.title("Modelo BIBD")

df = st.session_state.get("df")  # Dataset largo: Catador_ID, Variedad_Codigo, Puntaje_SCA


st.header("¿Entendiendo el BIBD?")

st.markdown("""
            Supongamos que tenemos un conjunto de \(v\) variedades de café especial que queremos evaluar mediante catas realizadas por \(b\) catadores. Cada catador puede evaluar solo \(k\) variedades en una sesión de cata, lo que significa que no todos los catadores evaluarán todas las variedades.
            Puede ocurrir que algunas variedades sean evaluadas por catadores más estrictos o con diferentes preferencias, lo que podría sesgar los resultados si no se controla adecuadamente. Para mitigar este sesgo, podemos utilizar un Diseño Balanceado de Bloques Incompletos
            que nos permite mitigar el efecto del catador al asegurar que cada par de variedades sea evaluado juntas un número equilibrado de veces en diferentes bloques (catadores).""")

st.header("Preliminares")

st.subheader("Teoremas")

st.markdown(r"""
### **Teorema 1 (Descomposición ortogonal)**  
Sea $V$ un espacio vectorial de dimensión finita con producto interno.  
Entonces, para cualquier subespacio $W \subseteq V$,

$$
V = W \oplus W^\perp
$$

donde
            
$$
W^\perp = \{ v \in V : \langle v, w \rangle = 0 \; \forall\, w \in W \}.
$$

En este caso $\oplus$ denota la suma directa de subespacios, es decir, si $V = W + H$ , $W \cap H = {0}$, entonces $V = W \oplus H$

En particular, todo vector $v \in V$ admite una **única** descomposición

$$
v = w + w^\perp
$$

con $w \in W$ y $w^\perp \in W^\perp$.

---

### **Definición 1 (Proyección ortogonal)**  
Sea $V$ un espacio vectorial con producto interno.  
Una transformación lineal $T : V \to W$ se llama **proyección ortogonal** si cumple:

1. **Idempotencia**:  
$$
T^2 = T,
$$

2. **Autoadjunta (simétrica)**:  
$$
T = T^{*}.
$$

En este caso, existen subespacios $W$ y $H$ tales que

$$
V = W \oplus H
$$

y además:

$$
\operatorname{R}(T) = W, \qquad \ker(T) = H.
$$

Para todo $v \in V$,
            
Donde $R(T)$ es la imagen (rango) de $T$ y $\ker(T)$ es el núcleo (espacio nulo) de $T$.

$$
T(v) = w
$$

es la **proyección ortogonal** de $v$ sobre el subespacio $W$ y tiene la propiedad:
$$
\|v - T(v)\| \leq \|v - z\| \quad \forall z \in W.
$$



### **Teorema 2 (Fórmula de la proyección en el rango de una transformación)**  

Sea $A \in \mathbb{R}^{n \times m}$ una matriz con:

$$
rank(A) = n
$$

Entonces, para cualquier $v \in \mathbb{R}^{m}$, si tomamos el vector

$$
w = (A^{*}A)^{-1}A^{*}v.
$$

Entonces, dada la norma euclidiana, $w$ es el único vector tal que:
$\|v - Aw\| \leq \|v - Az\|$ para cualquier $z \in \mathbb{R}^{n}$.
            
Para este caso decimos $A(A^{*}A)^{-1}A^{*} = P_{T}$ es la proyección ortogonal de $V$ sobre $R(A)$. 
""")

st.subheader("Demostración teorema 2")

st.markdown(r"""
Sea $v \in \mathbb{R}^{m}$, entonces por el Teorema 1, existe una descomposición única:
$$
v = Aw + h
$$
con $w \in \mathbb{R}^{n}$ y $h \in R(A)^{\perp}$. Por lo tanto, $v - Aw = h \in R(A)^{\perp}$ así, por definición de ortogonalidad:
$$
0 = \langle Az, v - Aw \rangle_{m} = (v - Aw)^{*}Az = (A^{*}(v - Aw))^{*}z = \langle z, A^{*}(v - Aw) \rangle_{n} \quad \forall z \in \mathbb{R}^{n}.
$$
Donde $ \langle \cdot , \cdot \rangle_{m}$ y $ \langle \cdot , \cdot \rangle_{n}$ son los productos internos en $\mathbb{R}^{m}$ y $\mathbb{R}^{n}$ respectivamente.
Por definición de producto interno, se tiene que:
$$
A^{*}(v - Aw) = 0
$$
Como $rank(A) = n$, entonces $A^{*}A$ es invertible, por lo tanto despejando $w$ se obtiene:
$$
w = (A^{*}A)^{-1}A^{*}v.
$$
Entonces si tomamos $T = A(A^{*}A)^{-1}A^{*}$, se tiene que:
$$
T(v) = Aw
$$
es la proyección ortogonal de $v$ sobre $R(A)$ ya que T es idempotente y autoadjunta.
""")

st.header("Entendiendo el ANOVA tradicional")

st.markdown(r"""
Se tiene una tabla de datos de $p$ poblaciones y $n_i$ observaciones numéricas por población para un total de  
$N = \sum_{k=1}^p n_k$ observaciones. Se quiere determinar si existen diferencias significativas entre las medias de las poblaciones.

Para esto se plantea el siguiente modelo lineal:

$$
Y  = \mu 1_N + X\tau + \epsilon
$$

donde:

- $Y \in \mathbb{R}^{N}$ es el vector de observaciones.  
- $\mu \in \mathbb{R}$ es la media global.  
- $1_N \in \mathbb{R}^{N}$ es el vector de unos.  
- $X \in \mathbb{R}^{N \times p}$ es la matriz de diseño de efectos fijos para las poblaciones ($X_{ij}=1$ si la observación $i$ está en la población $j$, 0 en otro caso).  
- $\tau \in \mathbb{R}^{p}$ es el vector de efectos de las poblaciones.  
- $\epsilon \in \mathbb{R}^{N}$ es el vector de errores aleatorios, con $\epsilon \sim N(0, \sigma^2 I_N)$.

Es decir, este modelo asume que cada observación $Y_i$ se puede expresar como la suma de una media global $\mu$, un efecto específico de la población $\tau_j$ a la que pertenece la observación, y un término de error aleatorio $\epsilon_i$.

Queremos conocer la variabilidad de las observaciones debida a las diferencias entre las medias de las poblaciones en comparación con la variabilidad debida al error aleatorio.  
Para esto, encontramos la variabilidad explicada por los efectos de las poblaciones.

Fíjese que:

$$
X1_p = 1_N
$$

Es decir, $1_N \in R(X)$. Por lo tanto, por el **Teorema 1**, podemos escribir:

$$
R(X) = \operatorname{span}\{1_N\} \oplus \left(\operatorname{span}\{1_N\}\right)^{\perp}
$$

Entonces, en términos de proyecciones ortogonales, podemos escribir:

$$
P_{X} = P_{1_N} + P_{X|\mu}
$$

Donde $P_{X}$ es la proyección ortogonal al espacio de todos los efectos de las poblaciones,  
$P_{1_N}$ es la proyección ortogonal al espacio de la media global, y  
$P_{X|\mu}$ es la proyección ortogonal al espacio de los efectos de las poblaciones ajustados por la media global.

Por el **Teorema 2**, sabemos que:

$$
P_{X} = X(X^{*}X)^{-1}X^{*}
$$

y, por un cálculo sencillo, se puede ver que:

$$
P_{1_N} = \frac{1}{N} 1_N 1_N^{*}
$$

Por lo tanto, se tiene que:

$$
P_{X|\mu} 
= X(X^{*}X)^{-1}X^{*} - \frac{1}{N}1_N1_N^{*}
$$

Como la varianza explicada por los efectos de las poblaciones ajustados por la media global viene dada por la forma cuadrática:

$$
SS_B = Y^{*} P_{X|\mu} Y
$$
            
Y los estimadores de los efectos de las poblaciones ajustados por la media global vienen dados por:
$$
\hat{\tau} = P_{X|\mu} Y
""")

st.header("Entendiendo el ANOVA para BIBD")

st.markdown(r"""
A diferencia del caso anterior, las observaciones no solo tienen un efecto de la población (variedad de café), sino que también tienen un efecto adicional debido a los bloques (catadores).  
Por lo tanto, el modelo lineal se extiende para incluir ambos efectos:

$$
Y  = \mu 1_N + X\tau + Z\beta + \epsilon
$$

donde:

- $Z \in \mathbb{R}^{N \times b}$ es la matriz de diseño de efectos fijos para los bloques (catadores) ($Z_{ij}=1$ si la observación $i$ está en el bloque $j$, 0 en otro caso).  
- $\beta \in \mathbb{R}^{b}$ es el vector de efectos de los bloques (catadores).  
- Los demás términos son como en el modelo anterior.

En este caso ya no podemos proyectar directamente sobre el espacio generado por $X$ debido a la presencia de los efectos de los bloques $Z$.  
Sin embargo, podemos ajustar los efectos de las variedades de café teniendo en cuenta los efectos de los catadores.  
Para esto, consideramos la proyección ortogonal al espacio generado por $Z$, es decir, debemos encontrar la proyección ortogonal de los efectos de la población ajustados por los efectos de los bloques.

Para esto, vamos a proyectar cada tratamiento (variedad de café) sobre el complemento ortogonal del espacio generado por los bloques (catadores). Así, notemos que:

$$
V = R(Z) \oplus R(Z)^{\perp}
$$

Entonces, por el Teorema 1, y por la definición de proyección ortogonal, podemos escribir:

$$
I = P_{V} = P_{Z} + P_{Z^{\perp}}
$$

Despejando $P_{Z^{\perp}}$, se tiene que:

$$
P_{Z^{\perp}} = I - P_{Z}
$$

Donde $P_{Z} = Z(Z^{*}Z)^{-1}Z^{*}$ es la proyección ortogonal sobre el espacio generado por los bloques (catadores).

Ahora, para proyectar los efectos de las variedades de café ajustados por los efectos de los bloques, podemos escribir:

$$
X|Z = P_{Z^{\perp}}\, X = (I - P_{Z})\, X
$$

Donde $P_{X|Z} = (X|Z)((X|Z)^{*}(X|Z))^{-1}(X|Z)^{*}$ es la proyección ortogonal de los efectos de las variedades de café ajustados por los efectos de los bloques (catadores).

---

Pero todavía nos falta ajustar por la media global. Para esto, notemos que:

$$
Z 1_b = 1_N
$$

Entonces, al proyectar sobre el complemento ortogonal de $R(Z)$, también se elimina la media global, es decir:

$$
P_{X|Z,\mu} = P_{X|Z}
$$

Finalmente, la varianza explicada por los efectos de las variedades de café ajustados por los efectos de los bloques y la media global viene dada por la forma cuadrática:

$$
SS_B = Y^{*} P_{X|Z} Y
$$

Y los estimadores de los efectos de las variedades de café ajustados por los efectos de los bloques y la media global vienen dados por:

$$
\hat{\tau} = P_{X|Z} Y
$$
            
Por ahora no hemos mencionado las condiciones del BIBD. Más adelante veremos cómo estas condiciones simplifican los cálculos anteriores.

## Condiciones del BIBD
Las condiciones del BIBD son las siguientes:
- Cada bloque (catador) evalúa exactamente \(k\) tratamientos (variedades de café).
- Cada tratamiento (variedad de café) es evaluado por exactamente \(r\) bloques (catadores).
- Cada par de tratamientos (variedades de café) es evaluado conjuntamente por exactamente \(\lambda\) bloques (catadores).
            Como resultado de estas condiciones, se cumplen las siguientes relaciones entre los parámetros del diseño:
$$
            bk = vr, \quad r(k - 1) = \lambda (v - 1)
$$
Estas condiciones aseguran que el diseño sea balanceado y que cada par de variedades de café sea evaluado juntas un número equilibrado de veces, lo que ayuda a mitigar el efecto del catador en los resultados de la cata.
            
### Identidades de las matrices de diseño en un BIBD

Bajo las condiciones del BIBD, las matrices de diseño $X$ (tratamientos) y $Z$ (bloques) satisfacen las siguientes identidades fundamentales:

---

#### 1. Matriz de incidencia tratamiento–bloque
$$
N = X^{*} Z
$$

---

#### 2. Concurrencia entre tratamientos
$$
NN^{*} = r I_v + \lambda (J_v - I_v)
$$

---

#### 3. Incidencia de tratamientos y bloques por separado
$$
X^{*}X = r I_v
$$
$$
Z^{*}Z = k I_b
$$

---

#### 4. Proyector sobre el espacio de los bloques
$$
P_Z = \frac{1}{k} Z Z^{*}
$$

---

#### 5. Interacción entre tratamientos y bloques
$$
X^{*} P_Z X
= \frac{1}{k} X^{*} Z Z^{*} X
= \frac{1}{k} N N^{*}
$$

Usando la identidad anterior:
$$
X^{*} P_Z X
= \frac{r}{k} I_v + \frac{\lambda}{k} (J_v - I_v)
$$

---

### Resultado final: matriz de información ajustada por bloques

La matriz de información de tratamientos ajustada por bloques es:
$$
C_\tau = X^{*} M_Z X
= X^{*}X - X^{*}P_Z X
$$

Sustituyendo:
$$
C_\tau
= rI_v - \left( \frac{r}{k} I_v + \frac{\lambda}{k} (J_v - I_v) \right)
$$

Agrupando términos:
$$
C_\tau = (r - \lambda)I_v + \lambda J_v
$$

Esta es la forma cuadrática clásica del BIBD utilizada para obtener la suma de cuadrados de tratamientos ajustada por bloques:
$$
\text{SC}_{\tau\mid Z} = Y^{*} P_{X\mid Z} Y
$$

donde
$$
P_{X\mid Z} = M_Z X (C_\tau)^{-1} X^{*} M_Z.
$$

""")

