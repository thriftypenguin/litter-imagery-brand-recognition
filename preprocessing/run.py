import os
import subprocess


def run_script(script_path):
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    print(f"Running {script_path}...")
    if result.returncode == 0:
        print(f"{script_path} ran successfully.")
    else:
        print(f"Error running {script_path}: {result.stderr}")

def replace_line(file_name, line_number, new_line):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    if 0 < line_number <= len(lines):
        lines[line_number - 1] = new_line + '\n'

    with open(file_name, 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    base_dir = 'preprocessing'
    scripts = [os.path.join(base_dir, 'rewrite_experimental.py'), os.path.join(base_dir, 'rewrite_yolov7_utils_general.py'), os.path.join(base_dir, 'rewrite_yolov7_utils_plots.py')]

    for script in scripts:
        run_script(script)
