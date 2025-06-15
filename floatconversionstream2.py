import streamlit as st
import numpy as np

st.set_page_config(page_title="Float16 Converter", layout="centered")
st.markdown("<h2 style='text-align:center;'>Float16 Converter</h2><hr>", unsafe_allow_html=True)

user_input = st.text_input("Enter a decimal or 16-bit hex (e.g. 1.345 or 0xbd6c):", "")

if user_input.strip():
    try:
        bits = None
        result = ""

        # Decimal input
        if any(c in user_input for c in ".0123456789e") and not user_input.startswith("0x"):
            val = float(user_input)
            f16 = np.float16(val)
            bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
            result = f"Hex: 0x{bits:04x}"

        # Hex input
        elif user_input.startswith("0x") or all(c in "0123456789abcdef" for c in user_input.replace("0x", "")):
            hex_str = user_input[2:] if user_input.startswith("0x") else user_input
            if len(hex_str) == 4:
                b0 = int(hex_str[0:2], 16)
                b1 = int(hex_str[2:4], 16)
                raw_bytes = bytes([b1, b0])
                f16 = np.frombuffer(raw_bytes, dtype=np.float16)[0]
                rounded_val = round(float(f16), 4)
                result = f"Decimal: {rounded_val:.4g}"
                bits = int(hex_str, 16)
            else:
                st.warning("Hex input must be 4 digits.")
                bits = None

        # Show results
        if bits is not None:
            s = (bits >> 15) & 0x1
            e = (bits >> 10) & 0x1F
            m = bits & 0x3FF
            exp_val = e - 15
            binary = f"{bits:016b}"
            mantissa_val = m / 1024
            mantissa = 1 + mantissa_val if 0 < e < 0x1F else mantissa_val

            # Float breakdown
            if e == 0 and m == 0:
                breakdown = "0"
            elif e == 0:
                breakdown = f"{'-1' if s else '1'} × 2^-14 × {mantissa:.4g}"
            elif e == 0x1F:
                breakdown = "Inf or NaN"
            else:
                breakdown = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"

            st.markdown("---")
            st.markdown(f"**{result}**")
            st.markdown(f"**Binary:** `{binary}`")
            st.markdown(f"**Bit Breakdown:**")
            st.text(f"Sign     : {s}")
            st.text(f"Exponent : {e:05b}")
            st.text(f"Mantissa : {m:010b}")
            st.markdown(f"**Float breakdown:** {breakdown}")

    except Exception as e:
        st.error("Invalid input.")