import struct

# Original value
combined_value = int(input("Enter number: "))

# Pack the signed value into 4 bytes (32-bit signed integer)
packed = struct.pack('i', combined_value)

# Unpack it as two 16-bit signed integers (high and low words)
low_word, high_word = struct.unpack('hh', packed)

print(f"Combined Value: {combined_value}")
print(f"Low Word: {low_word}")
print(f"High Word: {high_word}")
