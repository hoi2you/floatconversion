# NOTE: This script requires Streamlit and NumPy. Install them with:
# pip install streamlit numpy

import streamlit as st
import numpy as np

# --- Functions for Float16 Conversion ---
def float16_to_components(val):
    f16 = np.float16(val)
    bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
    s = (bits >> 15) & 0x1
    e = (bits >> 10) & 0x1F
    m = bits & 0x3FF
    
    bias = 15
    actual_exp = e - bias

    if e == 0 and m == 0:
        classification = "Zero"
    elif e == 0:
        classification = "Subnormal"
    elif e == 0x1F:
        classification = "Inf or NaN"
    else:
        classification = "Normal"

    return {
        "sign": s,
        "exponent_raw": e,
        "exponent_actual": actual_exp,
        "mantissa": m,
        "binary": f"{bits:016b}",
        "hex": f"0x{bits:04x}",
        "classification": classification,
        "float16": float(f16)
    }

# --- Streamlit Interface ---
st.set_page_config(page_title="Float16 Visualizer", layout="centered")
st.title("🧮 Float16 Visual Conversion")

val_input = st.text_input("Enter a decimal value to convert to Float16:", "1.5")

if val_input:
    try:
        val = float(val_input)
        components = float16_to_components(val)

        st.markdown("---")
        st.subheader("Step-by-Step Conversion")

        st.markdown(f"**Decimal Input:** `{val}`")
        st.markdown(f"**Float16 Output:** `{components['float16']}`")
        st.markdown(f"**Binary Representation:** `{components['binary']}`")
        st.markdown(f"**Hex Representation:** `{components['hex']}`")

        col1, col2, col3 = st.columns(3)
        col1.metric("Sign Bit", components['sign'])
        col2.metric("Exponent (Raw)", f"{components['exponent_raw']:05b}")
        col3.metric("Mantissa", f"{components['mantissa']:010b}")

        st.markdown(f"**Exponent (Actual):** `{components['exponent_actual']}`")
        st.markdown(f"**Classification:** `{components['classification']}`")

        # Visual layout
        st.markdown("---")
        st.subheader("Bit Breakdown")
        bit_str = components['binary']

        # Highlighted bit groups
        st.markdown(
            f"""
            <div style='font-family: monospace; font-size: 1.2em;'>
            <span style='color: red;'>Sign:</span> {bit_str[0]} &nbsp;
            <span style='color: green;'>Exponent:</span> {bit_str[1:6]} &nbsp;
            <span style='color: blue;'>Mantissa:</span> {bit_str[6:]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("""
        ### Float Construction Formula
        \[ \text{value} = (-1)^{\text{sign}} \times 2^{\text{exponent}} \times (1 + \text{mantissa fraction}) \]
        """)

        if components['classification'] == "Normal":
            mantissa_val = components['mantissa'] / 1024
            st.latex(f"(-1)^{{{components['sign']}}} \\times 2^{{{components['exponent_actual']}}} \\times (1 + {mantissa_val:.4g})")
        elif components['classification'] == "Subnormal":
            mantissa_val = components['mantissa'] / 1024
            st.latex(f"(-1)^{{{components['sign']}}} \\times 2^{{-14}} \\times {mantissa_val:.4g}")
        elif components['classification'] == "Zero":
            st.latex("0")
        else:
            st.markdown("Special value: Inf or NaN")

    except Exception:
        st.error("Please enter a valid decimal number.")