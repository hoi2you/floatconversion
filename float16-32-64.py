import streamlit as st
import numpy as np

# --- Setup ---
st.set_page_config(page_title="Float16 & Float32 Toolkit", layout="centered")
st.title("🧮 Float16 & Float32 Toolkit")

# --- Sidebar Format & Tool Selector ---
precision = st.sidebar.selectbox("Floating Point Format", ["Float16", "Float32"])
page = st.sidebar.selectbox("Select Tool", [
    "Converter",
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Square Root"
])

# --- Config Based on Precision ---
if precision == "Float16":
    dtype = np.float16
    bitwidth = 16
    exp_bits = 5
    man_bits = 10
    bias = 15
    bits_type = np.uint16
else:
    dtype = np.float32
    bitwidth = 32
    exp_bits = 8
    man_bits = 23
    bias = 127
    bits_type = np.uint32

# --- Helpers ---
def float_to_bits(val):
    return np.frombuffer(np.array(val, dtype=dtype).tobytes(), dtype=bits_type)[0]

def bits_to_float(bits):
    byte_len = bitwidth // 8
    return np.frombuffer(bits.to_bytes(byte_len, byteorder='little'), dtype=dtype)[0]

def is_hex(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return all(c in "0123456789abcdef" for c in s)

def breakdown(bits):
    s = (bits >> (exp_bits + man_bits)) & 0x1
    e = (bits >> man_bits) & ((1 << exp_bits) - 1)
    m = bits & ((1 << man_bits) - 1)
    exp_val = e - bias
    mantissa_val = m / (1 << man_bits)
    mantissa = 1 + mantissa_val if 0 < e < (1 << exp_bits) - 1 else mantissa_val

    if e == 0 and m == 0:
        formula = "0"
    elif e == 0:
        formula = f"{'-1' if s else '1'} × 2^{1 - bias} × {mantissa:.4g}"
    elif e == (1 << exp_bits) - 1:
        formula = "Inf or NaN"
    else:
        formula = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"

    return s, e, m, formula, f"{bits:0{bitwidth}b}"

# --- UI Output ---
def show_result(result):
    bits = float_to_bits(result)
    s, e, m, formula, binary = breakdown(bits)
    st.markdown("---")
    st.markdown(f"### Result: `{float(result):.6g}`  |  Hex: `0x{bits:0{bitwidth//4}x}`")
    st.markdown(f"**Binary:** `{binary}`")
    st.text(f"Sign     : {s}")
    st.text(f"Exponent : {e:0{exp_bits}b}")
    st.text(f"Mantissa : {m:0{man_bits}b}")
    st.markdown(f"**Float formula:** {formula}")

# --- Converter ---
if page == "Converter":
    user_input = st.text_input(f"Enter a decimal or {bitwidth}-bit hex (e.g. 1.345 or 0x3f80):", "")
    if user_input.strip():
        try:
            if user_input.startswith("0x") or is_hex(user_input):
                hex_str = user_input[2:] if user_input.startswith("0x") else user_input
                bits = int(hex_str, 16)
                val = bits_to_float(bits)
                st.markdown(f"**Decimal:** `{float(val):.6g}`")
                show_result(val)
            else:
                val = dtype(float(user_input))
                show_result(val)
        except Exception:
            st.error("Invalid input.")

# --- Binary Operation Block ---
def binary_op(label, op_func):
    col1, col2 = st.columns(2)
    with col1:
        a_str = st.text_input("Enter first number (decimal or hex):", key=label + "_a")
    with col2:
        b_str = st.text_input("Enter second number (same format):", key=label + "_b")

    if a_str and b_str:
        is_hex_mode = (a_str.startswith("0x") or is_hex(a_str)) and (b_str.startswith("0x") or is_hex(b_str))
        try:
            a = bits_to_float(int(a_str[2:], 16) if a_str.startswith("0x") else int(a_str, 16)) if is_hex_mode else dtype(float(a_str))
            b = bits_to_float(int(b_str[2:], 16) if b_str.startswith("0x") else int(b_str, 16)) if is_hex_mode else dtype(float(b_str))
            result = op_func(a, b)
            show_result(result)
        except ZeroDivisionError:
            st.error("Division by zero.")
        except Exception:
            st.error("Invalid input or conversion failed.")

# --- Arithmetic Pages ---
if page == "Addition":
    binary_op("add", lambda a, b: dtype(a + b))
elif page == "Subtraction":
    binary_op("sub", lambda a, b: dtype(a - b))
elif page == "Multiplication":
    binary_op("mul", lambda a, b: dtype(a * b))
elif page == "Division":
    binary_op("div", lambda a, b: dtype(a / b) if b != 0 else np.nan)
elif page == "Square Root":
    x_str = st.text_input("Enter number (decimal or hex):", key="sqrt")
    if x_str:
        try:
            x = bits_to_float(int(x_str[2:], 16) if x_str.startswith("0x") else int(x_str, 16)) if is_hex(x_str) else dtype(float(x_str))
            if x < 0:
                st.error("Cannot take square root of negative number.")
            else:
                result = dtype(np.sqrt(x))
                show_result(result)
        except Exception:
            st.error("Invalid input.")