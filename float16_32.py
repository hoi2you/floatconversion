import streamlit as st
import numpy as np

# --- App Setup ---
st.set_page_config(page_title="Float16 & Float32 Toolkit", layout="centered")
st.markdown("<h2 style='text-align:center;'>Float16 & Float32 Toolkit</h2><hr>", unsafe_allow_html=True)

# --- Helper Functions ---
def float_to_bits(val, dtype):
    return np.frombuffer(np.array(val, dtype=dtype).tobytes(), dtype={np.float16: np.uint16, np.float32: np.uint32}[dtype])[0]

def bits_to_float(bits, dtype):
    byte_length = {np.float16: 2, np.float32: 4}[dtype]
    return np.frombuffer(bits.to_bytes(byte_length, byteorder='little'), dtype=dtype)[0]

def get_breakdown(bits, dtype):
    if dtype == np.float16:
        total_bits, exp_bits, man_bits, bias = 16, 5, 10, 15
    else:
        total_bits, exp_bits, man_bits, bias = 32, 8, 23, 127

    s = (bits >> (exp_bits + man_bits)) & 0x1
    e = (bits >> man_bits) & ((1 << exp_bits) - 1)
    m = bits & ((1 << man_bits) - 1)
    exp_val = e - bias
    mantissa_val = m / (1 << man_bits)
    mantissa = 1 + mantissa_val if 0 < e < (1 << exp_bits) - 1 else mantissa_val

    if e == 0 and m == 0:
        formula = "0"
    elif e == 0:
        formula = f"{'-1' if s else '1'} × 2^{1-bias} × {mantissa:.4g}"
    elif e == (1 << exp_bits) - 1:
        formula = "Inf or NaN"
    else:
        formula = f"{'-1' if s else '1'} × 2^{exp_val} × {mantissa:.4g}"

    return f"{bits:0{total_bits}b}", s, e, m, formula

def is_hex(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return all(c in "0123456789abcdef" for c in s)

# --- Sidebar ---
precision = st.sidebar.selectbox("Floating Point Format", ["Float16", "Float32"])
operation = st.sidebar.selectbox("Operation", ["Convert", "Addition", "Subtraction", "Multiplication", "Division", "Square Root"])

dtype = np.float16 if precision == "Float16" else np.float32
bitwidth = 16 if dtype == np.float16 else 32

# --- Main Logic ---
def show_result(result):
    bits = float_to_bits(result, dtype)
    binary, s, e, m, formula = get_breakdown(bits, dtype)
    st.markdown("---")
    st.markdown(f"### Result: `{float(result):.6g}`  &nbsp;&nbsp;|&nbsp;&nbsp; Hex: `0x{bits:0{bitwidth//4}x}`")
    st.markdown(f"**Binary:** `{binary}`")
    st.markdown("**Bit Breakdown:**")
    st.text(f"Sign     : {s}")
    st.text(f"Exponent : {e:0{bitwidth//4}b}")
    st.text(f"Mantissa : {m:0{bitwidth - 1 - (bitwidth // 4)}b}")
    st.markdown(f"**Float formula:** {formula}")

if operation == "Convert":
    user_input = st.text_input(f"Enter a decimal or {bitwidth}-bit hex value (e.g. 1.25 or 0x3c00):", "")
    if user_input:
        try:
            if user_input.startswith("0x") or is_hex(user_input):
                hex_str = user_input[2:] if user_input.startswith("0x") else user_input
                bits = int(hex_str, 16)
                val = bits_to_float(bits, dtype)
                st.markdown(f"**Decimal:** `{float(val):.6g}`")
                show_result(val)
            else:
                val = dtype(float(user_input))
                show_result(val)
        except:
            st.error("Invalid input.")

else:
    col1, col2 = st.columns(2)
    with col1:
        a_str = st.text_input("First number (dec or hex):", key="a")
    with col2:
        b_str = st.text_input("Second number (same format):", key="b")

    if a_str and b_str:
        is_hex_mode = (a_str.startswith("0x") or is_hex(a_str)) and (b_str.startswith("0x") or is_hex(b_str))
        try:
            if is_hex_mode:
                a = bits_to_float(int(a_str[2:], 16) if a_str.startswith("0x") else int(a_str, 16), dtype)
                b = bits_to_float(int(b_str[2:], 16) if b_str.startswith("0x") else int(b_str, 16), dtype)
            else:
                a = dtype(float(a_str))
                b = dtype(float(b_str))

            result = None
            if operation == "Addition":
                result = dtype(a + b)
            elif operation == "Subtraction":
                result = dtype(a - b)
            elif operation == "Multiplication":
                result = dtype(a * b)
            elif operation == "Division":
                if b == 0.0:
                    st.error("Division by zero.")
                else:
                    result = dtype(a / b)

            if result is not None:
                show_result(result)

        except:
            st.error("Invalid input.")

if operation == "Square Root":
    x_str = st.text_input("Enter number (decimal or hex):", key="sqrt")
    if x_str:
        is_hex_mode = x_str.startswith("0x") or is_hex(x_str)
        try:
            if is_hex_mode:
                x = bits_to_float(int(x_str[2:], 16) if x_str.startswith("0x") else int(x_str, 16), dtype)
            else:
                x = dtype(float(x_str))

            if x < 0:
                st.error("Cannot take square root of negative number.")
            else:
                result = dtype(np.sqrt(x))
                show_result(result)

        except:
            st.error("Invalid input.")