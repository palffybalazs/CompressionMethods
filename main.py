import struct
import os
import time
import sys
import binascii
import numpy as np
import pickle

from lz78 import compression_lz78, decompression_lz78
from lz77 import compression_lz77, decompression_lz77
from huffman import compress_huffman, decompress_huffman

def add_header(new_contents, counter):
    pcd = f"""\
# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z intensity
SIZE 4 4 4 4
TYPE F F F F
COUNT 1 1 1 1
WIDTH {counter}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {counter}
DATA ascii
"""

    # Append data
    for line in new_contents:
        pcd += f"{line}"
    #1print("New contents: " + str(pcd[:3000]))
    return pcd

def remove_zeros(data):
    lines = data.split("\n")

    # iterate over the lines and remove any that contain "0 0 0 0"
    new_lines = [line for line in lines if "0 0 0 0" not in line]
    new = []
    counter = 0
    for line in new_lines:
        if line != "" and line[0].isdigit() and line != "#":
            counter += 1
            # separate the string by space
            line = line.split(" ")
            # keep only two digits after the decimal point and remove square brackets and quotes
            line = [f"{float(x):.2f}" if i < len(line)-1 else str(int(float(x))) for i, x in enumerate(line)]
            #line = [f"{float(x):.2f}" for x in line]
            new.append(" ".join(line))
    # join the remaining lines back together
    pcd = "\n".join(new)
    return pcd, counter


def cal_differences(lines, counter):
    # Split the lines into a list of strings by the newline character
    new_lines = lines.split("\n")
    # Initialize an empty list to store the data
    data = []
    # Iterate through each line
    for line in new_lines:
        # Check if the line is not empty, starts with a digit, and is not a comment
        if line != "" and line[0].isdigit() and line != "#":
            # Split the line by spaces and append it to the data list
            line = line.split(" ")
            data.append(line)
    # Initialize an empty list to store the result
    result = []
    # Initialize a counter for the row number
    counter_row = 0
    # Initialize a variable to store the previous values
    prev_values = None
    # Iterate through each row of data
    for row in data:
        # Initialize an empty list to store the current values
        curr_values = []
        # Check if the row has 4 values
        if len(row) == 4:
            # Increment the row counter
            counter_row += 1
            # Iterate through each value in the row
            for i, val in enumerate(row):
                # Check if there are previous values and the current index is within bounds
                if prev_values is not None and i <= len(row) - 1:
                    # Calculate the difference between the current value and the previous value
                    diff = (float(val)) - (float(prev_values[i]))
                    # Round the difference to 2 decimal places and append it to the current values list
                    curr_values.append(round(diff, 2))
                else:
                    # If there are no previous values or the index is out of bounds, append the current value as is
                    curr_values.append(float(val))
            # Set the previous values to the current row
            prev_values = row
            # Convert the last value of the current values list to an integer
            curr_values[3] = int(curr_values[3])
            # Append the current values to the result list
            result.append(curr_values)
            # Increment the row counter
            counter_row += 1
    # Create a temporary list to store the formatted rows
    tmp = []
    # Iterate through each row in the result list
    for row in result:
        # Join the values in the row with spaces and append it to the temporary list
        tmp.append(' '.join([str(val) for val in row]))
    # Join the rows in the temporary list with newline characters and assign it to the variable "pcd"
    pcd = "\n".join(tmp)
    # Return the formatted PCD data
    return pcd


def retrieve_original_data(lines):
    # Split the lines into a list of strings by the newline character
    new_lines = lines.split("\n")
    # Initialize an empty list to store the data
    data = []
    # Iterate through each line
    for line in new_lines:
        # Check if the line is not empty and not a comment
        if line != "" and line != "#":
            # Split the line by spaces and append it to the data list
            line = line.split(" ")
            data.append(line)

    # Initialize an empty list to store the result
    result = []
    # Initialize a variable to store the previous values
    prev_values = None
    # Initialize a counter for the row number
    counter_row = 0
    # Iterate through each row of data
    for row in data:
        # Initialize an empty list to store the current values
        curr_values = []
        # Iterate through each value in the row
        for i, val in enumerate(row):
            # Check if there are previous values and the current index is within bounds
            if prev_values is not None and i <= len(row) - 1:
                # Calculate the original data based on the previous value and the current value
                if float(val) > 0:
                    original_data = float(val) + float(prev_values[i])
                else:
                    original_data = float(prev_values[i]) - abs(float(val))
                # Round the original data to 2 decimal places and append it to the current values list
                curr_values.append(round(original_data, 2))
            else:
                # If there are no previous values or the index is out of bounds, append the current value as is
                curr_values.append(round(float(val), 2))
        curr_values[3] = int(curr_values[3])
        # Set the previous values to the current values
        prev_values = curr_values
        # Append the current values to the result list
        result.append(curr_values)
        # Increment the row counter
        counter_row += 1
    # Create a temporary list to store the formatted rows
    tmp = []
    # Iterate through each row in the result list
    for row in result:
        # Join the values in the row with spaces and append it to the temporary list
        tmp.append(' '.join([str(val) for val in row]))
    # Join the rows in the temporary list with newline characters and assign it to the variable "original_data"
    original_data = "\n".join(tmp)
    # Add a header to the original data using the number of rows in the result list
    original_data = add_header(original_data, len(result))
    # Return the formatted original data
    return original_data

def compression(to_compress, compressed, compression_algorithm):
    # Create the compressed folder if it doesn't already exist
    if not os.path.exists(compressed):
        os.makedirs(compressed)
    print("Compressing files...")

    # Iterate through all files in the to_compress folder
    for filename in os.listdir(to_compress):
        # Measure time of compression
        start = time.time()
        print(filename)
        # Get the size of the original file
        original_size = os.path.getsize(os.path.join(to_compress, filename))
        print("Original size: " + str(original_size) + " bytes")
        if filename.endswith(".pcd"):
            with open(os.path.join(to_compress, filename), "r") as f:
                # Read in the contents of the PCD file
                contents = f.read()
                # Remove any lines that contain "0 0 0 0" and get the counter for removed lines
                contents, counter = remove_zeros(contents)
                # Calculate differences between consecutive lines
                contents = cal_differences(contents, counter)
                new_size = None
                # Check the selected compression algorithm
                if compression_algorithm == "lz78":
                    # Compress the contents using LZ78
                    compressed_contents = compression_lz78(contents)
                    filename = filename[:-4]
                    with open(os.path.join(compressed, filename + "." + compression_algorithm), "w") as f2:
                        compressed_contents = ' '.join([f'{code}:{char}' for code, char in compressed_contents])
                        f2.write(compressed_contents)
                    new_size = os.path.getsize(os.path.join(compressed, filename + "." + compression_algorithm))

                elif compression_algorithm == "lz77":
                    # Compress the contents using LZ77
                    compressed_contents = compression_lz77(contents)
                    filename = filename[:-4]
                    with open(os.path.join(compressed, filename + "." + compression_algorithm), "w") as f2:
                        f2.write(str(compressed_contents))
                    new_size = os.path.getsize(os.path.join(compressed, filename + "." + compression_algorithm))

                elif compression_algorithm == "huff":
                    # Compress the contents using Huffman coding
                    compressed_contents, huffman_tree = compress_huffman(contents)
                    # Save the Huffman tree to a file
                    with open('huffman_tree.pickle', 'wb') as file:
                        pickle.dump(huffman_tree, file)
                    filename = filename[:-4]
                    with open(os.path.join(compressed, filename + "." + compression_algorithm), "w") as f2:
                        f2.write(str(compressed_contents))
                    new_size = os.path.getsize(os.path.join(compressed, filename + "." + compression_algorithm))

                elif compression_algorithm == "hul8":
                    # Compress the contents using Huffman coding and LZ78
                    compressed_contents, huffman_tree = compress_huffman(contents)
                    # Save the Huffman tree to a file
                    with open('huffman_tree_78.pickle', 'wb') as file:
                        pickle.dump(huffman_tree, file)
                    compressed_contents = compression_lz78(compressed_contents)
                    filename = filename[:-4]
                    with open(os.path.join(compressed, filename + "." + compression_algorithm), "w") as f2:
                        compressed_contents = ' '.join([f'{code}:{char}' for code, char in compressed_contents])
                        f2.write(compressed_contents)
                    new_size = os.path.getsize(os.path.join(compressed, filename + "." + compression_algorithm))

                elif compression_algorithm == "hul7":
                    # Compress the contents using Huffman coding and LZ77
                    compressed_contents, huffman_tree = compress_huffman(contents)
                    # Save the Huffman tree to a file
                    with open('huffman_tree_77.pickle', 'wb') as file:
                        pickle.dump(huffman_tree, file)
                    compressed_contents = compression_lz77(compressed_contents)
                    filename = filename[:-4]
                    with open(os.path.join(compressed, filename + "." + compression_algorithm), "w") as f2:
                        f2.write(str(compressed_contents))
                    new_size = os.path.getsize(os.path.join(compressed, filename + "." + compression_algorithm))

                print("New size: " + str(new_size) + " bytes")
        end = time.time()
        print("Compression time: " + str(end - start))
        break
    print("Done compressing files.")
    return counter


def decompression(to_decompress, decompressed, compression_algorithm):
    # Create the decompressed folder if it doesn't already exist
    if not os.path.exists(decompressed):
        os.makedirs(decompressed)
    print("Decompressing files...")
    # Iterate through all files in the to_decompress folder
    for filename in os.listdir(to_decompress):
        # Measure time of compression
        start = time.time()
        print(filename)
        # Get the size of the original file
        original_size = os.path.getsize(os.path.join(to_decompress, filename))
        print("Original size: " + str(original_size) + " bytes")
        if filename.endswith("." + compression_algorithm):
            with open(os.path.join(to_decompress, filename), "r") as f:
                # Read in the contents of the compressed file
                compressed_string = f.read().strip()
                # Parse the compressed data into a list of tuples

                if compression_algorithm == "lz78":
                    # Decompress the data using LZ78
                    compressed_data = []
                    for pair in compressed_string.split():
                        pair_list = pair.split(":")
                        if len(pair_list) == 2:
                            code, char = pair_list
                            compressed_data.append((int(code), char))
                    decompressed_contents = decompression_lz78(compressed_data)

                elif compression_algorithm == "lz77":
                    # Decompress the data using LZ77
                    decompressed_contents = decompression_lz77(compressed_string)

                elif compression_algorithm == "huff":
                    # Decompress the data using Huffman
                    with open('huffman_tree.pickle', 'rb') as file:
                        huffman_tree = pickle.load(file)
                    decompressed_contents = decompress_huffman(compressed_string, huffman_tree)

                elif compression_algorithm == "hul8":
                    # Decompress the data using Huffman and LZ78
                    compressed_data = []
                    for pair in compressed_string.split():
                        pair_list = pair.split(":")
                        if len(pair_list) == 2:
                            code, char = pair_list
                            compressed_data.append((int(code), char))
                    with open('huffman_tree.pickle', 'rb') as file:
                        huffman_tree = pickle.load(file)
                    decompressed_contents = decompression_lz78(compressed_data)
                    decompressed_contents = decompress_huffman(decompressed_contents, huffman_tree)

                # Retrieve the original data from the decompressed contents
                decompressed_contents = retrieve_original_data(decompressed_contents)

                filename = filename[:-5]
                with open(os.path.join(decompressed, filename + ".pcd"), "w") as f2:
                    f2.write(decompressed_contents)
                new_size = os.path.getsize(os.path.join(decompressed, filename + ".pcd"))
                print("New size: " + str(new_size) + " bytes")
        else:
            print("File is not compressed with " + compression_algorithm)
            continue
        end = time.time()
        print("Decompression time: " + str(end - start))
    print("Done decompressing files.")

def main():
    # Read in arg comp or decomp from command line to determine whether to compress or decompress
    action = sys.argv[1]
    if len(sys.argv) == 3:
        algorithm = sys.argv[2]
    else:
        algorithm = ""

    print("Action: " + action, " with Algorithm: " + algorithm)
    to_compress = "./to_compress_1000/"
    compressed = "./compressed_1000/"
    decompressed = "./decompressed_1000/"
    if action == "comp":
        print("Compressing files in " + to_compress + " and saving to " + compressed)
        # Call the compression function
        compression(to_compress, compressed, algorithm)
    elif action == "decomp":
        print("Decompressing files in " + compressed + " and saving to " + decompressed)
        # Call the decompression function
        decompression(compressed, decompressed, algorithm)

if __name__ == "__main__":
    # Call the main function
    main()
