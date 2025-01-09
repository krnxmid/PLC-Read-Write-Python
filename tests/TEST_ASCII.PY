
def convert_string_to_ascii_32bit():
    
    def combine_16bit_to_32bit(high_word, low_word):
        '''For combining 16 bit and 32 bit registers'''
        result = (low_word << 16) | high_word
        return result
    
    def split_16bit_to_8bit(value):
        """Split a 16-bit integer into two 8-bit integers."""
        low_byte = value & 0xFF          # Get the lower 8 bits
        high_byte = (value >> 8) & 0xFF   # Get the upper 8 bits
        return low_byte, high_byte

    def convert_16bit_to_ascii(value):
        """Convert a 16-bit integer to two ASCII characters."""
        if not (0 <= value <= 0xFFFF):
            raise ValueError("Value must be a 16-bit integer (0 to 65535).")

        low_byte, high_byte = split_16bit_to_8bit(value)

        # Convert bytes to characters
        char1 = chr(low_byte)
        char2 = chr(high_byte)

        return char1, char2
    
    def combine_8bit_to_16bit(high_word, low_word):
        '''For combining x2 8 bit into 16 bit registers'''
        result = (low_word << 8) | high_word
        return result

    text = input("Enter your text: ")
    list = []
    for char in text:
        list.append(char)
    digits = []
    for i in list:
        ascii_character = ord(i)
        digits.append(ascii_character)
        print(ascii_character)

    bit1 = combine_8bit_to_16bit(digits[0], digits[1])
    bit2 = combine_8bit_to_16bit(digits[2], digits[3])

    combined_32 = combine_16bit_to_32bit(bit1, bit2)
    return combined_32
convert_string_to_ascii_32bit()