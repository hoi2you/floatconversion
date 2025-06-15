import streamlit as st
import numpy as np

st.set_page_config(page_title="Float16 Converter", layout="centered")
st.title("🔢 Float16 Converter")

user_input = st.text_input("Enter decimal or 16-bit hex (e.g., 1.345 or 0xbd6c):", "")

if user_input.strip():
    try:
        display_mode = None
        result = ""
        bits = None

        # Try interpreting as float
        if any(c in user_input for c in ".0123456789e") and not user_input.startswith("0x"):
            val = float(user_input)
            f16 = np.float16(val)
            bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
            result = f"0x{bits:04x}"
            display_mode = "float"

        # Try interpreting as hex
        elif user_input.startswith("0x") or all(c in "0123456789abcdef" for c in user_input.replace("0x", "")):
            hex_str = user_input[2:] if user_input.startswith("0x") else user_input
            if len(hex_str) == 4:
                b0 = int(hex_str[0:2], 16)
                b1 = int(hex_str[2:4], 16)
                raw_bytes = bytes([b1, b0])
                f16 = np.frombuffer(raw_bytes, dtype=np.float16)[0]
                result = f"{round(float(f16), 4):.4g}"
                bits = int(hex_str, 16)
                display_mode = "hex"
            else:
                st.warning("Hex input must be 4 digits (e.g. 0xbd6c)")
    except Exception:
        st.error("Invalid input")

    if bits is not None:
        s = (bits >> 15) & 0x1
        e = (bits >> 10) & 0x1F
        m = bits & 0x3FF

        # Bit pattern
        binary = f"{bits:016b}"
        formatted = f"{s}  {e:05b}  {m:010b}"

        # Float breakdown
        sign_val = -1 if s else 1
        exp_val = e - 15

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

        st.subheader("🔍 Result")
        st.code(result, language="text")

        st.subheader("🧬 Bit Pattern")
        st.markdown(f"`{binary}`")
        st.text(formatted)

        st.subheader("🧠 Float Breakdown")
        st.text(breakdown)