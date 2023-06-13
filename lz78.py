def compression_lz78(data):
    """Compress a string to a list of output symbols."""

    # Build the dictionary.
    dict_size = 256  # Initial size of the dictionary
    # Creating a dictionary where each character is mapped to its corresponding integer value
    dictionary = dict((chr(i), i) for i in range(dict_size))

    current_substring = ""  # Current substring
    compressed_symbols = []  # List to store the compressed symbols
    for character in data:  # Iterate over each character in the input string
        next_substring = current_substring + character  # Concatenate current substring and current character

        if next_substring in dictionary:  # Check if next_substring is in the dictionary
            current_substring = next_substring  # Update current_substring to next_substring if it exists in the dictionary
        else:
            # Add tuple (code for current_substring, character) to the compressed_symbols list
            # to represent the compressed symbol
            compressed_symbols.append((dictionary[current_substring], character))

            # Add next_substring to the dictionary with the next available code
            dictionary[next_substring] = dict_size
            # Update current_substring to the current character since we start processing a new substring
            dict_size += 1
            current_substring = character

    if current_substring:
        # Append tuple (code for current_substring, "") to the compressed_symbols list
        # to signify the end of the input data
        compressed_symbols.append((dictionary[current_substring], ""))

    return compressed_symbols


def decompression_lz78(data):
    """Decompress a list of output symbols to a string."""

    dict_size = 256  # Initial size of the dictionary
    # Creating a dictionary where each integer value is mapped to its corresponding character
    dictionary = dict((i, chr(i)) for i in range(dict_size))

    decompressed_data = ""  # String to store the decompressed data
    # Get the character corresponding to the code of the first tuple in data
    current_character = dictionary[data.pop(0)[0]]
    # Append current_character to the decompressed_data string
    decompressed_data += current_character

    for code, character in data:
        if code in dictionary:  # If the code exists in the dictionary
            next_entry = dictionary[code]
        elif code == dict_size:  # If the code represents a new substring
            next_entry = current_character + current_character[0]  # Create the next_entry by concatenating current_character with its first character
        else:
            # Raise an exception if the compressed code is invalid
            raise ValueError('Bad compressed code: %s' % code)

        # Append the next_entry to the decompressed_data string
        decompressed_data += next_entry
        # Add the new entry current_character + next_entry[0] to the dictionary with the next available code
        dictionary[dict_size] = current_character + next_entry[0]
        dict_size += 1
        # Update current_character to the current entry for the next iteration
        current_character = next_entry

    return decompressed_data
