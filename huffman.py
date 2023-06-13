from heapq import heappush, heappop, heapify
from collections import defaultdict
import pickle


class HuffmanNode:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_table(data):
    freq_table = defaultdict(int)  # Dictionary to store character frequencies
    for char in data:  # Iterate over each character in the data
        freq_table[char] += 1  # Increment the frequency count for the character
    return freq_table


def build_huffman_tree(freq_table):
    heap = [[weight, HuffmanNode(char, weight)] for char, weight in freq_table.items()]  # Create a min heap with frequency and corresponding node
    heapify(heap)  # Convert the list into a heap data structure
    while len(heap) > 1:  # Continue until there is only one node left in the heap
        lo = heappop(heap)  # Pop the node with the lowest frequency
        hi = heappop(heap)  # Pop the node with the second lowest frequency
        merged_node = HuffmanNode(None, lo[0] + hi[0])  # Create a new node with the combined frequency
        merged_node.left = lo[1]  # Set the left child of the merged node
        merged_node.right = hi[1]  # Set the right child of the merged node
        heappush(heap, [merged_node.freq, merged_node])  # Push the merged node back into the heap
    return heap[0][1]  # Return the root node of the Huffman tree


def build_encoding_table(node, code=''):
    encoding_table = {}  # Dictionary to store character encodings
    if node.value:  # If the node represents a character (leaf node)
        encoding_table[node.value] = code  # Assign the code to the character
    else:  # If the node is not a leaf node
        encoding_table.update(build_encoding_table(node.left, code + '0'))  # Recursively build the encoding table for the left subtree
        encoding_table.update(build_encoding_table(node.right, code + '1'))  # Recursively build the encoding table for the right subtree
    return encoding_table


def compress_huffman(data):
    freq_table = build_frequency_table(data)  # Build the frequency table for the input data
    huffman_tree = build_huffman_tree(freq_table)  # Build the Huffman tree using the frequency table
    encoding_table = build_encoding_table(huffman_tree)  # Build the encoding table from the Huffman tree

    compressed_data = ''  # String to store the compressed data
    for char in data:  # Iterate over each character in the data
        compressed_data += encoding_table[char]  # Append the encoding of the character to the compressed data

    return compressed_data, huffman_tree


def decompress_huffman(compressed_data, huffman_tree):
    decompressed_data = ''  # String to store the decompressed data
    current_node = huffman_tree  # Start from the root of the Huffman tree
    for bit in compressed_data:  # Iterate over each bit in the compressed data
        if bit == '0':  # If the bit is '0', traverse to the left child
            current_node = current_node.left
        else:  # If the bit is '1', traverse to the right child
            current_node = current_node.right
        if current_node.value:  # If the current node represents a character (leaf node)
            decompressed_data += current_node.value  # Append the character to the decompressed data
            current_node = huffman_tree  # Reset the current node to the root of the Huffman tree

    return decompressed_data
