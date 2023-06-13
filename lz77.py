def compression_lz77(data):
    # Initialize an empty list to store compressed data
    compressed_data = []
    # Set the size of the sliding window and lookahead buffer
    window_size = 1000
    lookahead_buffer_size = 20
    i = 0
    while i < len(data):
        # Determine the start and end indices of the search window and lookahead buffer
        search_window_start = max(0, i - window_size)
        search_window = data[search_window_start:i]
        lookahead_buffer_end = min(i + lookahead_buffer_size, len(data))
        lookahead_buffer = data[i:lookahead_buffer_end]
        # Find the longest match between the search window and lookahead buffer
        offset, length = find_longest_match(search_window, lookahead_buffer)
        # Get the next character after the match
        next_character = data[i + length] if i + length < len(data) else ""
        # Add the compressed entry to the list
        compressed_data.append((offset, length, next_character))
        # Move the index based on the length of the match
        i += length + 1

    return compressed_data


def find_longest_match(search_window, lookahead_buffer):
    # Initialize the best offset and length to 0
    best_offset = 0
    best_length = 0

    for i in range(1, len(lookahead_buffer) + 1):
        # Get the current window from the lookahead buffer
        current_window = lookahead_buffer[:i]
        # Find the last occurrence of the current window in the search window
        offset = search_window.rfind(current_window)
        # If a match is found
        if offset != -1:
            length = len(current_window)
            # Update the best offset and length if the current match is longer
            if length > best_length:
                best_offset = len(search_window) - offset
                best_length = length

    return best_offset, best_length


def decompression_lz77(compressed_data):
    # Initialize an empty string to store the decompressed data
    decompressed_data = ""
    # Convert the compressed data to an array
    compressed_data = eval(str(compressed_data))
    # Iterate over each entry in the compressed data
    for entry in compressed_data:
        offset, length, next_character = entry
        # If the length is 0, simply add the next character to the decompressed data
        if length == 0:
            decompressed_data += next_character
        else:
            # Retrieve the substring from the decompressed data based on the offset
            start_index = len(decompressed_data) - offset
            # Repeat the substring for the length of the match and add the next character
            for _ in range(length):
                decompressed_data += decompressed_data[start_index]
                start_index += 1
            decompressed_data += next_character

    return decompressed_data
