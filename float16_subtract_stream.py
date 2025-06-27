import streamlit as st
import numpy as np

st.set_page_config(page_title="Float16 Subtractor", layout="centered")
st.markdown("<h2 style='text-align:center;'>Float16 Subtractor</h2><hr>", unsafe_allow_html=True)

def is_hex16(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return len(s) == 4 and all(c in "0123456789abcdef" for c in s)

def parse_hex16(s):
    s = s.strip().lower()
    hex_str = s[2:] if s.startswith("0x") else s
    b0 = int(hex_str[0:2], 16)
    b1 = int(hex_str[2:4], 16)
    raw_bytes = bytes([b1, b0])
    return np.frombuffer(raw_bytes, dtype=np.float16)[0]

def float16_to_bits(f16):
    return np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]

def breakdown(bits):
    s = (bits >> 15) & 0x1
    e = (bits >> 10) & 0x1F
    m = bits & 0x3FF
    exp_val = e - 15
    mantissa_val = m / 1024
    mantissa = 1 + mantissa_val if 0 < e < 0x1F else mantissa_val

    if e == 0 and m == 0:
        formula = "0"
    elif e == 0:
        formula = f"{'-1' if s else '1'} × 2^-14 × {mantissa:.4g}"
    elif e == 0x1F:
        formula = "Inf or NaN"
    else:
        formula = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"

    return s, e, m, formula

# --- Streamlit UI ---

col1, col2 = st.columns(2)
with col1:
    a_str = st.text_input("Enter first number (decimal or 0xABCD):", "")
with col2:
    b_str = st.text_input("Enter second number (same format as first):", "")

if a_str and b_str:
    a_is_hex = is_hex16(a_str)
    b_is_hex = is_hex16(b_str)

    if a_is_hex != b_is_hex:
        st.error("Both inputs must be the same format (either both hex or both decimal).")
    else:
        try:
            if a_is_hex:
                a = parse_hex16(a_str)
                b = parse_hex16(b_str)
                a_bits = float16_to_bits(a)
                b_bits = float16_to_bits(b)
            else:
                a = np.float16(float(a_str))
                b = np.float16(float(b_str))
                a_bits = float16_to_bits(a)
                b_bits = float16_to_bits(b)

            result = np.float16(a - b)
            result_bits = float16_to_bits(result)
            binary = f"{result_bits:016b}"
            s, e, m, formula = breakdown(result_bits)

            st.markdown("---")
            st.markdown(f"### ➖ Result: `{float(result):.6g}`  &nbsp;&nbsp;|&nbsp;&nbsp; Hex: `0x{result_bits:04x}`")
            st.markdown(f"**Binary:** `{binary}`")
            st.markdown("**Bit Breakdown:**")
            st.text(f"Sign     : {s}")
            st.text(f"Exponent : {e:05b}")
            st.text(f"Mantissa : {m:010b}")
            st.markdown(f"**Float formula:** {formula}")

        except Exception:
            st.error("Invalid input or conversion failed.")