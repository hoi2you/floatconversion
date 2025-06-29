# Streamlit Decimal to Float16 Visualizer
import streamlit as st
import numpy as np
import math

st.set_page_config(page_title="Float16 Visualizer", layout="centered")
st.title("🔍 Decimal to Float16 Conversion Visualizer")

# --- Input ---
decimal_input = st.text_input("Enter a decimal number:", "1.5")

try:
    val = float(decimal_input)
    f16 = np.float16(val)
    bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
    sign = (bits >> 15) & 0x1
    exponent = (bits >> 10) & 0x1F
    mantissa = bits & 0x3FF

    st.markdown("---")
    st.header("Step-by-Step Breakdown")

    # --- Step 1: Sign Bit ---
    st.subheader("1. Sign Bit")
    st.write(f"The number is {'negative' if sign else 'positive'}, so the sign bit is `{sign}`.")

    # --- Step 2: Convert to Binary Scientific Notation ---
    st.subheader("2. Normalize to Binary Scientific Notation")
    abs_val = abs(val)
    if abs_val == 0.0:
        st.write("The value is zero. All bits are zero.")
        norm_str = "0"
    else:
        exp = int(np.floor(np.log2(abs_val)))
        normalized = abs_val / (2 ** exp)
        norm_str = f"{normalized:.5f} × 2^{exp}"
        st.write(f"We write {val} as approximately **{norm_str}**.")

    # --- Step 3: Apply Bias (15 for Float16) ---
    st.subheader("3. Apply Exponent Bias (15 for Float16)")
    biased_exp = exponent
    unbiased_exp = biased_exp - 15
    st.write(f"Encoded exponent = `{biased_exp:05b}` → Unbiased exponent = `{unbiased_exp}`")
    st.write("This creates a \"window\" where the number resides: the power-of-two scale.")

    # --- Step 4: Mantissa (Fractional Part) ---
    st.subheader("4. Mantissa (Fractional Part)")
    if exponent == 0:
        st.write("This is a subnormal number. The leading bit is not assumed to be 1.")
    elif exponent == 0x1F:
        st.write("This is either Inf or NaN. The mantissa is not meaningful.")
    else:
        st.write(f"Mantissa bits: `{mantissa:010b}`")
        frac_val = 1 + mantissa / (2 ** 10)
        st.write(f"Actual mantissa value used = `{frac_val}`")

    # --- Step 5: Final Bits ---
    st.subheader("5. Final 16-bit Layout")
    bit_string = f"{sign}{exponent:05b}{mantissa:010b}"
    st.code(bit_string, language="")

    # Colorful layout
    st.markdown(f"""
    <div style='font-family: monospace; font-size: 16px;'>
        <span style='color: red;'>Sign</span>: <code>{sign}</code>
        &nbsp;&nbsp;
        <span style='color: green;'>Exponent</span>: <code>{exponent:05b}</code>
        &nbsp;&nbsp;
        <span style='color: blue;'>Mantissa</span>: <code>{mantissa:010b}</code>
    </div>
    <br>
    <b>Hex Representation:</b> <code>0x{bits:04x}</code>
    """, unsafe_allow_html=True)

    # Special checks
    if exponent == 0 and mantissa != 0:
        st.warning("⚠️ This is a subnormal number.")
    elif exponent == 0x1F:
        st.warning("⚠️ This is a special value: Infinity or NaN.")

except Exception:
    st.error("Invalid decimal input.")