def format_value(value):
    # Convert the input to a string to handle it easily
    FRICTIONAL_DIGIT = 2
    value_str = str(value).strip()
    
    # Check if the value is a float
    if '.' in value_str:
        # Split the string into whole and fractional parts
        whole_part, fractional_part = value_str.split('.')
        
        # Keep only the first digit of the fractional part
        if len(fractional_part) > FRICTIONAL_DIGIT:
            fractional_part = fractional_part[0:FRICTIONAL_DIGIT]  # Keep only the first digit
        elif len(fractional_part) <= FRICTIONAL_DIGIT and len(fractional_part) != 0:
            required_zeros = FRICTIONAL_DIGIT - len(fractional_part)
            zeros = "0"*required_zeros
            fractional_part = fractional_part+zeros
            
        # Combine the whole part and the truncated fractional part
        result = whole_part + fractional_part
    else:
        # If it's an integer, just add a zero at the end
        
        result = value_str + '0'*FRICTIONAL_DIGIT
    
    return int(result)
while True:
    number = input("Enter your number: ")
    print(format_value(number))