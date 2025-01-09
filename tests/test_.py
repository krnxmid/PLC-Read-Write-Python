import ast

# The string to be converted
str_value = "['tag_1', '-2140071000']"

# Convert the string into a list
converted_list = ast.literal_eval(str_value)

# Output the result
print(converted_list[0])
