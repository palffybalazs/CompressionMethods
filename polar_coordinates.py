import os
import math

folder_path = "./to_compress/"
output_path = "./polar_coordinates/"

def cartesian_to_polar(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    theta = math.atan2(y, x)
    phi = math.atan2(math.sqrt(x**2 + y**2), z)
    return (r, theta, phi)

for filename in os.listdir(folder_path):
    if filename.endswith(".pcd"):
        with open(folder_path + filename, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.startswith("FIELDS x y z"):
                new_lines.append("FIELDS r theta phi intensity\n")
            if not line.startswith("#") and line[0].isdigit():
                x, y, z, intensity = map(float, line.strip().split())
                r, theta, phi = cartesian_to_polar(x, y, z)
                new_line = "{:.6f} {:.6f} {:.6f} {:.0f}\n".format(r, theta, phi, intensity)
                new_lines.append(new_line)
        with open(output_path + filename[:-4] + "_polar.pcd", 'w') as f:
            f.writelines(new_lines)
