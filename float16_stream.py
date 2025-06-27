import streamlit as st
import numpy as np

# --- Shared Functions ---
def is_hex16(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return len(s) == 4 and all(c in "0123456789abcdef" for c in s)

def parse_hex16(s):
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

    return s, e, m, formula, f"{float16_to_bits(np.float16(bits)):016b}"

# --- Streamlit App ---
st.set_page_config(page_title="Float16 Toolkit", layout="centered")
st.title("🧮 Float16 Toolkit")

page = st.sidebar.selectbox("Select Tool", [
    "Float16 Converter",
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Square Root"
])

# --- Converter ---
if page == "Float16 Converter":
    user_input = st.text_input("Enter a decimal or 16-bit hex (e.g. 1.345 or 0xbd6c):", "")

    if user_input.strip():
        try:
            bits = None
            result = ""
            val = None

            if any(c in user_input for c in ".0123456789e") and not user_input.startswith("0x"):
                val = float(user_input)
                f16 = np.float16(val)
                bits = float16_to_bits(f16)
                result = f"Hex: 0x{bits:04x}"

            elif user_input.startswith("0x") or is_hex16(user_input):
                hex_str = user_input[2:] if user_input.startswith("0x") else user_input
                if len(hex_str) == 4:
                    val = parse_hex16(user_input)
                    bits = float16_to_bits(val)
                    result = f"Decimal: {float(val):.4g}"
                else:
                    st.warning("Hex input must be 4 digits.")

            if bits is not None:
                s, e, m, formula, binary = breakdown(bits)
                st.markdown("---")
                st.markdown(f"**{result}**")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:05b}")
                st.text(f"Mantissa : {m:010b}")
                st.markdown(f"**Float breakdown:** {formula}")

        except Exception:
            st.error("Invalid input.")

# --- Binary Operation Template ---
def float16_binary_op(label, op_func):
    col1, col2 = st.columns(2)
    with col1:
        a_str = st.text_input("Enter first number (decimal or 0xABCD):", key=label+"a")
    with col2:
        b_str = st.text_input("Enter second number (same format):", key=label+"b")

    if a_str and b_str:
        a_is_hex = is_hex16(a_str)
        b_is_hex = is_hex16(b_str)

        if a_is_hex != b_is_hex:
            st.error("Both inputs must be the same format (either both hex or both decimal).")
        else:
            try:
                a = parse_hex16(a_str) if a_is_hex else np.float16(float(a_str))
                b = parse_hex16(b_str) if b_is_hex else np.float16(float(b_str))
                result = op_func(a, b)
                result_bits = float16_to_bits(result)
                s, e, m, formula, binary = breakdown(result_bits)

                st.markdown("---")
                st.markdown(f"### Result: `{float(result):.6g}`  |  Hex: `0x{result_bits:04x}`")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:05b}")
                st.text(f"Mantissa : {m:010b}")
                st.markdown(f"**Float formula:** {formula}")

            except ZeroDivisionError:
                st.error("Division by zero.")
            except Exception:
                st.error("Invalid input or conversion failed.")

if page == "Addition":
    float16_binary_op("add", lambda a, b: np.float16(a + b))

if page == "Subtraction":
    float16_binary_op("sub", lambda a, b: np.float16(a - b))

if page == "Multiplication":
    float16_binary_op("mul", lambda a, b: np.float16(a * b))

if page == "Division":
    float16_binary_op("div", lambda a, b: np.float16(a / b))

# --- Square Root ---
if page == "Square Root":
    x_str = st.text_input("Enter number (decimal or 0xABCD):", "")
    if x_str:
        try:
            x = parse_hex16(x_str) if is_hex16(x_str) else np.float16(float(x_str))
            if x < 0:
                st.error("Square root of a negative number is not a real value.")
            else:
                result = np.float16(np.sqrt(x))
                result_bits = float16_to_bits(result)
                s, e, m, formula, binary = breakdown(result_bits)

                st.markdown("---")
                st.markdown(f"### √ Result: `{float(result):.6g}`  |  Hex: `0x{result_bits:04x}`")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:05b}")
                st.text(f"Mantissa : {m:010b}")
                st.markdown(f"**Float formula:** {formula}")
        except Exception:
            st.error("Invalid input or conversion failed.")
