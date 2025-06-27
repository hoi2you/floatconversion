import streamlit as st
import numpy as np

# --- Shared Functions ---
def is_hex32(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return len(s) == 8 and all(c in "0123456789abcdef" for c in s)

def parse_hex32(s):
    hex_str = s[2:] if s.startswith("0x") else s
    b = bytes.fromhex(hex_str)
    return np.frombuffer(b[::-1], dtype=np.float32)[0]

def float32_to_bits(f32):
    return np.frombuffer(f32.tobytes(), dtype=np.uint32)[0]

def breakdown32(bits):
    s = (bits >> 31) & 0x1
    e = (bits >> 23) & 0xFF
    m = bits & 0x7FFFFF
    exp_val = e - 127
    mantissa_val = m / (2 ** 23)
    mantissa = 1 + mantissa_val if 0 < e < 0xFF else mantissa_val

    if e == 0 and m == 0:
        formula = "0"
    elif e == 0:
        formula = f"{'-1' if s else '1'} × 2^-126 × {mantissa:.4g}"
    elif e == 0xFF:
        formula = "Inf or NaN"
    else:
        formula = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"

    return s, e, m, formula, f"{bits:032b}"

# --- Streamlit App ---
st.set_page_config(page_title="Float32 Toolkit", layout="centered")
st.title("🧮 Float32 Toolkit")

page = st.sidebar.selectbox("Select Tool", [
    "Float32 Converter",
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Square Root"
])

# --- Converter ---
if page == "Float32 Converter":
    user_input = st.text_input("Enter a decimal or 32-bit hex (e.g. 3.14159 or 0x40490fdb):", "")

    if user_input.strip():
        try:
            bits = None
            result = ""
            val = None

            if any(c in user_input for c in ".0123456789e") and not user_input.startswith("0x"):
                val = float(user_input)
                f32 = np.float32(val)
                bits = float32_to_bits(f32)
                result = f"Hex: 0x{bits:08x}"

            elif user_input.startswith("0x") or is_hex32(user_input):
                hex_str = user_input[2:] if user_input.startswith("0x") else user_input
                if len(hex_str) == 8:
                    val = parse_hex32(user_input)
                    bits = float32_to_bits(val)
                    result = f"Decimal: {float(val):.6g}"
                else:
                    st.warning("Hex input must be 8 digits.")

            if bits is not None:
                s, e, m, formula, binary = breakdown32(bits)
                st.markdown("---")
                st.markdown(f"**{result}**")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:08b}")
                st.text(f"Mantissa : {m:023b}")
                st.markdown(f"**Float breakdown:** {formula}")

        except Exception:
            st.error("Invalid input.")

# --- Binary Operation Template ---
def float32_binary_op(label, op_func):
    col1, col2 = st.columns(2)
    with col1:
        a_str = st.text_input("Enter first number (decimal or 0xXXXXXXXX):", key=label+"a")
    with col2:
        b_str = st.text_input("Enter second number (same format):", key=label+"b")

    if a_str and b_str:
        a_is_hex = is_hex32(a_str)
        b_is_hex = is_hex32(b_str)

        if a_is_hex != b_is_hex:
            st.error("Both inputs must be the same format (either both hex or both decimal).")
        else:
            try:
                a = parse_hex32(a_str) if a_is_hex else np.float32(float(a_str))
                b = parse_hex32(b_str) if b_is_hex else np.float32(float(b_str))
                result = op_func(a, b)
                result_bits = float32_to_bits(result)
                s, e, m, formula, binary = breakdown32(result_bits)

                st.markdown("---")
                st.markdown(f"### Result: `{float(result):.6g}`  |  Hex: `0x{result_bits:08x}`")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:08b}")
                st.text(f"Mantissa : {m:023b}")
                st.markdown(f"**Float formula:** {formula}")

            except ZeroDivisionError:
                st.error("Division by zero.")
            except Exception:
                st.error("Invalid input or conversion failed.")

if page == "Addition":
    float32_binary_op("add32", lambda a, b: np.float32(a + b))

if page == "Subtraction":
    float32_binary_op("sub32", lambda a, b: np.float32(a - b))

if page == "Multiplication":
    float32_binary_op("mul32", lambda a, b: np.float32(a * b))

if page == "Division":
    float32_binary_op("div32", lambda a, b: np.float32(a / b))

# --- Square Root ---
if page == "Square Root":
    x_str = st.text_input("Enter number (decimal or 0xXXXXXXXX):", "")
    if x_str:
        try:
            x = parse_hex32(x_str) if is_hex32(x_str) else np.float32(float(x_str))
            if x < 0:
                st.error("Square root of a negative number is not a real value.")
            else:
                result = np.float32(np.sqrt(x))
                result_bits = float32_to_bits(result)
                s, e, m, formula, binary = breakdown32(result_bits)

                st.markdown("---")
                st.markdown(f"### √ Result: `{float(result):.6g}`  |  Hex: `0x{result_bits:08x}`")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:08b}")
                st.text(f"Mantissa : {m:023b}")
                st.markdown(f"**Float formula:** {formula}")
        except Exception:
            st.error("Invalid input or conversion failed.")
