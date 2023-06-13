import os
import struct

def binary_to_pcd(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    # Parse binary data to extract x, y, z, intensity values
    num_floats = len(data) // 4
    num_points = num_floats // 4
    fmt = '<' + 'ffff'*num_points
    points = struct.unpack(fmt, data)
    # Write data to output PCD file
    with open(output_file, 'w') as f:
        f.write('# .PCD v0.7 - Point Cloud Data file format\n')
        f.write('VERSION 0.7\n')
        f.write('FIELDS x y z intensity\n')
        f.write('SIZE 4 4 4 4\n')
        f.write('TYPE F F F F\n')
        f.write('COUNT 1 1 1 1\n')
        f.write(f'WIDTH {num_points}\n')
        f.write('HEIGHT 1\n')
        f.write('VIEWPOINT 0 0 0 1 0 0 0\n')
        f.write(f'POINTS {num_points}\n')
        f.write('DATA ascii\n')
        '''for point in points:
            f.write(f'{point}\n')'''
        for i in range(num_points):
            point = points[i*4:i*4+4]
            x, y, z, intensity = point
            f.write(f'{x:.3f} {y:.3f} {z:.3f} {intensity}\n')
    print(f'Successfully converted {input_file} to PCD format and saved to {output_file}')

def main():
    binary_folder = './binary/'
    output_folder = './from_binary/'
    os.makedirs(output_folder, exist_ok=True)
    for file in os.listdir(binary_folder):
        if file.endswith('.bin'):
            input_file = os.path.join(binary_folder, file)
            output_file = os.path.join(output_folder, file[:-4] + '.pcd')
            binary_to_pcd(input_file, output_file)

if __name__ == '__main__':
    main()
