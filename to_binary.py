import os
import struct
# Function to convert ASCII file to binary file
def convert_ascii_to_binary(ascii_path, binary_path):
    # Open ASCII file for reading
    with open(ascii_path, 'r') as f:
        # Read all lines of the file
        lines = f.readlines()
    
    # Open binary file for writing
    with open(binary_path, 'wb') as f:
        # Write the PCD data as binary
        for line in lines[11:]:
            x, y, z, intensity = map(float, line.split())
            f.write(struct.pack('ffff', x, y, z, intensity))




# Convert all files in the to_compress folder to binary files in the binary folder
to_compress_dir = './to_compress_200/'
binary_dir = './binary/'

# Create the binary directory if it doesn't exist
if not os.path.exists(binary_dir):
    os.makedirs(binary_dir)

# Loop over all files in the to_compress directory
for file_name in os.listdir(to_compress_dir):
    # Check that the file is a PCD file
    if file_name.endswith('.pcd'):
        # Define the paths for the ASCII and binary files
        ascii_path = os.path.join(to_compress_dir, file_name)
        binary_path = os.path.join(binary_dir, file_name[:-4] + '.bin')
        
        # Convert the ASCII file to binary
        convert_ascii_to_binary(ascii_path, binary_path)
