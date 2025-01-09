import struct

def combine_16bit_to_32bit(high_word, low_word):
    '''For combining 16 bit and 32 bit registers'''
    
    # Shift the low word by 16 bytes to accomodate for high word to make a 32 but value
    result = (low_word << 16) | high_word
    return result

def unsigned_to_signed(value):
    '''For converting unsigned to signed value'''
    
    signed_value = struct.unpack('i', struct.pack('I', value))[0]
    return signed_value

def split_32bit_to_16bit(value):
    '''For splitting a 32 bit register'''
    signed_32bit = struct.pack('i', value)
    
    # Split the 32 bit value to get low word, high word
    high_word, low_word = struct.unpack('hh', signed_32bit)
    return high_word, low_word
    
def split_16bit_to_8bit(value):
    """Split a 16-bit integer into two 8-bit integers."""
    
    # Get the lower 8 bits
    low_word = value & 0xFF         
    # Get the upper 8 bits
    high_word = (value >> 8) & 0xFF   
    return low_word, high_word

def convert_16bit_to_ascii(value):
    """Convert a 16-bit integer to two ASCII characters."""
    
    # Handling error just in case of a invalid value
    if not (0 <= value <= 0xFFFF):
        raise ValueError("Value must be a 16-bit integer (0 to 65535).")
    
    # Get the low and high words
    low_word, high_word = split_16bit_to_8bit(value)
    
    # Convert bytes to characters
    char1 = chr(low_word)
    char2 = chr(high_word)
    
    return char1, char2
