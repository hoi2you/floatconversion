# Streamlit App: Float16 Conversion Visual Guide
import streamlit as st
import numpy as np
import math

st.set_page_config(page_title="Float16 Hand Conversion", layout="centered")
st.title("✍️ Float16 Conversion Walkthrough")

# --- Input ---
decimal_input = st.text_input("Enter a decimal number to convert to float16:", "-0.15625")

try:
    val = float(decimal_input)
    f16 = np.float16(val)
    bits = np.frombuffer(f16.tobytes(), dtype=np.uint16)[0]
    sign = (bits >> 15) & 0x1
    exponent = (bits >> 10) & 0x1F
    mantissa = bits & 0x3FF

    # Step 1: Sign Bit
    st.header("Step 1: Determine the Sign Bit")
    st.markdown(f"The number is {'negative' if sign else 'positive'}, so the sign bit is **{sign}**.")

    # Step 2: Absolute value for further steps
    abs_val = abs(val)
    if abs_val == 0.0:
        st.header("Step 2: Zero Value")
        st.markdown("This is a zero. All bits are 0. No further breakdown needed.")
    else:
        # Step 3: Convert to binary
        st.header("Step 2: Convert the Number to Binary")
        int_part = int(abs_val)
        frac_part = abs_val - int_part

        int_bin = bin(int_part)[2:] if int_part != 0 else "0"
        frac_bin = ""
        frac = frac_part
        while len(frac_bin) < 15 and frac > 0:
            frac *= 2
            bit = int(frac)
            frac_bin += str(bit)
            frac -= bit

        st.markdown(f"Integer part `{int_part}` → binary: `{int_bin}`")
        st.markdown(f"Fractional part `{frac_part}` → binary: `.{frac_bin}`")
        full_bin = int_bin + "." + frac_bin
        st.markdown(f"Combined binary: `{full_bin}`")

        # Step 4: Normalize the binary
        st.header("Step 3: Normalize the Binary Form")
        if int_part != 0:
            shift = len(int_bin) - 1
            normalized = int_bin[0] + "." + int_bin[1:] + frac_bin
        else:
            first_one_index = frac_bin.find("1") + 1
            shift = -first_one_index
            normalized = frac_bin[first_one_index-1:] if first_one_index > 0 else "0"

        st.markdown(f"Normalized form: `1.{normalized}` × 2^{shift}")

        # Step 5: Calculate exponent with bias
        st.header("Step 4: Calculate Exponent with Bias (bias = 15)")
        biased_exp = shift + 15
        if biased_exp <= 0:
            biased_exp_bin = "00000"  # subnormal
            status = "Subnormal"
        elif biased_exp >= 31:
            biased_exp_bin = "11111"  # Inf or NaN
            status = "Overflow"
        else:
            biased_exp_bin = f"{biased_exp:05b}"
            status = "Normal"
        st.markdown(f"Exponent = shift ({shift}) + 15 = {biased_exp} → binary: `{biased_exp_bin}`")
        st.markdown(f"This is a **{status}** number.")

        # Step 6: Extract mantissa
        st.header("Step 5: Extract Mantissa")
        mantissa_str = (normalized.replace(".", "") + "0000000000")[:10]
        st.markdown(f"Mantissa (first 10 bits after leading 1): `{mantissa_str}`")

        # Step 7: Final bits
        st.header("Step 6: Assemble the 16-bit Float")
        full_bits = f"{sign}{biased_exp_bin}{mantissa_str}"
        hex_val = f"0x{int(full_bits, 2):04x}"

        st.markdown(f"**Final 16-bit Representation**: `{full_bits}`")
        st.markdown(f"**Hex Representation**: `{hex_val}`")

except Exception as e:
    st.error("Invalid input. Please enter a valid decimal number.")