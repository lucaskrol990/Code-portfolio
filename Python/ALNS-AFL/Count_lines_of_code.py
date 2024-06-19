import os

def count_lines_of_code(directory):
    total_lines = 0
    # Define file extensions to include
    include_extensions = ['.py']
    # Define directories to exclude
    exclude_dirs = ['venv', '.git', '__pycache__']

    for root, dirs, files in os.walk(directory):
        # Exclude certain directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            # Check if file has the desired extension
            if file.endswith(tuple(include_extensions)):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        # Exclude blank lines
                        if line.strip():
                            total_lines += 1
    return total_lines

# Provide the directory path where your PyCharm project is located
pycharm_directory = "C:/Users/lucas/OneDrive/Documenten/RUG/Msc Year 2/TOM thesis/Code"

total_lines_of_code = count_lines_of_code(pycharm_directory)
print("Total lines of code (excluding external libraries and blank lines):", total_lines_of_code)