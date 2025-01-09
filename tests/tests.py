def format_value(value):
    """Format the value to have one decimal place."""
    if isinstance(value, int):
        # If the number is an integer, convert it to float and format
        return f"{value // 10}.{value % 10}"
    elif isinstance(value, float):
        # If the number is a float, format to one decimal place
        return f"{value:.1f}"
    return value  # Return as is if not a number

number = input("Enter a number")