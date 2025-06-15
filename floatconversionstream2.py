import streamlit as st
import numpy as np

st.set_page_config(page_title="Float16 Converter", layout="centered")

st.title("🔢 Float16 Converter")
st.markdown("Enter a **decimal number** (e.g. `1.345`) or a **16-bit hex** value (e.g. `0xbd6c`).")

user_input = st.text_input("Input:", "")

if user_input.strip():
    try:
        display_mode = None
        result = ""
        bits = None

        # Try float input
        if any(c in user_input for c in ".0123456789e") and not user_input.startswith("0x"):
            val = float(user_input)
            f16 = np.float16(val)
            bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
            result = f"**Hex:** `0x{bits:04x}`"
            display_mode = "float"

        # Try hex input
        elif user_input.startswith("0x") or all(c in "0123456789abcdef" for c in user_input.replace("0x", "")):
            hex_str = user_input[2:] if user_input.startswith("0x") else user_input
            if len(hex_str) == 4:
                b0 = int(hex_str[0:2], 16)
                b1 = int(hex_str[2:4], 16)
                raw_bytes = bytes([b1, b0])
                f16 = np.frombuffer(raw_bytes, dtype=np.float16)[0]
                rounded_val = round(float(f16), 4)
                result = f"**Decimal:** `{rounded_val:.4g}`"
                bits = int(hex_str, 16)
                display_mode = "hex"
            else:
                st.warning("Hex input must be exactly 4 digits (e.g. `0xbd6c`)")
    except Exception:
        st.error("Invalid input")

    if bits is not None:
        # Extract IEEE 754 fields
        s = (bits >> 15) & 0x1
        e = (bits >> 10) & 0x1F
        m = bits & 0x3FF

        binary = f"{bits:016b}"
        formatted = f"{s}  {e:05b}  {m:010b}"
        sign_val = -1 if s else 1
        exp_val = e - 15

        # Breakdown
        if e == 0 and m == 0:
            breakdown = "0"
        elif e == 0:
            mant = m / 1024
            breakdown = f"{sign_val} × 2⁻¹⁴ × {mant:.4g}"
        elif e == 0x1F:
            breakdown = "Inf or NaN"
        else:
            mant = 1 + (m / 1024)
            breakdown = f"{sign_val} × 2^{exp_val} × {mant:.4g}"

        st.markdown("---")

        st.markdown("### 🧾 Result")
        st.markdown(result)

        st.markdown("### 🧬 Bit Pattern")
        st.markdown(f"<div style='font-family:Courier; font-size:18px;'>{formatted}</div>", unsafe_allow_html=True)
        st.markdown(f"`{binary}`", unsafe_allow_html=True)

        st.markdown("### 🧠 Float Breakdown")
        st.markdown(f"<div style='font-family:Courier; font-size:17px;'>{breakdown}</div>", unsafe_allow_html=True)