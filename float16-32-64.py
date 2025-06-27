import streamlit as st
import numpy as np

# --- Shared Functions ---
def is_hex(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return all(c in "0123456789abcdef" for c in s)

def bits_to_float(bits, dtype):
    byte_length = {np.float16: 2, np.float32: 4, np.float64: 8}[dtype]
    return np.frombuffer(bits.to_bytes(byte_length, byteorder='little'), dtype=dtype)[0]

def float_to_bits(fval, dtype):
    return np.frombuffer(np.array(fval, dtype=dtype).tobytes(), dtype={np.float16: np.uint16, np.float32: np.uint32, np.float64: np.uint64}[dtype])[0]

def get_params(dtype):
    if dtype == np.float16:
        return 16, 5, 10, 15
    elif dtype == np.float32:
        return 32, 8, 23, 127
    else:
        return 64, 11, 52, 1023

def breakdown(bits, dtype):
    total_bits, exp_bits, man_bits, bias = get_params(dtype)
    s = (bits >> (exp_bits + man_bits)) & 0x1
    e = (bits >> man_bits) & ((1 << exp_bits) - 1)
    m = bits & ((1 << man_bits) - 1)
    exp_val = e - bias
    mantissa_val = m / (1 << man_bits)
    mantissa = 1 + mantissa_val if 0 < e < (1 << exp_bits) - 1 else mantissa_val

    if e == 0 and m == 0:
        formula = "0"
        status = "Zero"
    elif e == 0:
        formula = f"{'-1' if s else '1'} × 2^{1-bias} × {mantissa:.4g}"
        status = "Subnormal"
    elif e == (1 << exp_bits) - 1:
        formula = "Inf or NaN"
        status = "Overflow or NaN"
    else:
        formula = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"
        status = "Normal"

    return s, e, m, formula, f"{bits:0{total_bits}b}", status

# --- Streamlit App ---
st.set_page_config(page_title="Float Toolkit", layout="centered")
st.title("🧮 Float16 / Float32 / Float64 Toolkit")

precision = st.sidebar.selectbox("Precision", ["Float16", "Float32", "Float64"])
page = st.sidebar.selectbox("Select Tool", ["Converter", "Addition", "Subtraction", "Multiplication", "Division", "Square Root"])

dtype = {"Float16": np.float16, "Float32": np.float32, "Float64": np.float64}[precision]
bitwidth, exp_bits, man_bits, bias = get_params(dtype)

# --- Converter ---
if page == "Converter":
    user_input = st.text_input(f"Enter a decimal or {bitwidth}-bit hex (e.g. 1.345 or 0x3f800000):", "")
    if user_input.strip():
        try:
            if user_input.startswith("0x") or is_hex(user_input):
                hex_str = user_input[2:] if user_input.startswith("0x") else user_input
                bits = int(hex_str, 16)
                val = bits_to_float(bits, dtype)
                st.markdown(f"**Decimal:** `{float(val):.6g}`")
                result = val
            else:
                result = dtype(float(user_input))

            bits = float_to_bits(result, dtype)
            s, e, m, formula, binary, status = breakdown(bits, dtype)

            st.markdown("---")
            st.markdown(f"**Hex:** `0x{bits:0{bitwidth//4}x}`")
            st.markdown(f"**Binary:** `{binary}`")
            st.text(f"Sign     : {s}")
            st.text(f"Exponent : {e:0{exp_bits}b}")
            st.text(f"Mantissa : {m:0{man_bits}b}")
            st.markdown(f"**Float formula:** {formula}")
            st.markdown(f"**Status:** `{status}`")

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
            a = bits_to_float(int(a_str[2:], 16) if a_str.startswith("0x") else int(a_str, 16), dtype) if is_hex_mode else dtype(float(a_str))
            b = bits_to_float(int(b_str[2:], 16) if b_str.startswith("0x") else int(b_str, 16), dtype) if is_hex_mode else dtype(float(b_str))
            result = op_func(a, b)

            bits = float_to_bits(result, dtype)
            s, e, m, formula, binary, status = breakdown(bits, dtype)

            st.markdown("---")
            st.markdown(f"### Result: `{float(result):.6g}`  |  Hex: `0x{bits:0{bitwidth//4}x}`")
            st.markdown(f"**Binary:** `{binary}`")
            st.text(f"Sign     : {s}")
            st.text(f"Exponent : {e:0{exp_bits}b}")
            st.text(f"Mantissa : {m:0{man_bits}b}")
            st.markdown(f"**Float formula:** {formula}")
            st.markdown(f"**Status:** `{status}`")

        except ZeroDivisionError:
            st.error("Division by zero.")
        except Exception:
            st.error("Invalid input or conversion failed.")

if page == "Addition":
    binary_op("add", lambda a, b: dtype(a + b))
elif page == "Subtraction":
    binary_op("sub", lambda a, b: dtype(a - b))
elif page == "Multiplication":
    binary_op("mul", lambda a, b: dtype(a * b))
elif page == "Division":
    binary_op("div", lambda a, b: dtype(a / b))
elif page == "Square Root":
    x_str = st.text_input("Enter number (decimal or hex):", key="sqrt")
    if x_str:
        try:
            x = bits_to_float(int(x_str[2:], 16) if x_str.startswith("0x") else int(x_str, 16), dtype) if is_hex(x_str) else dtype(float(x_str))
            if x < 0:
                st.error("Cannot take square root of negative number.")
            else:
                result = dtype(np.sqrt(x))
                bits = float_to_bits(result, dtype)
                s, e, m, formula, binary, status = breakdown(bits, dtype)

                st.markdown("---")
                st.markdown(f"### √ Result: `{float(result):.6g}`  |  Hex: `0x{bits:0{bitwidth//4}x}`")
                st.markdown(f"**Binary:** `{binary}`")
                st.text(f"Sign     : {s}")
                st.text(f"Exponent : {e:0{exp_bits}b}")
                st.text(f"Mantissa : {m:0{man_bits}b}")
                st.markdown(f"**Float formula:** {formula}")
                st.markdown(f"**Status:** `{status}`")
        except Exception:
            st.error("Invalid input.")