import os
import json
import fnmatch

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        return None

def parse_gitignore(gitignore_path):
    ignore_patterns = []
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
    except FileNotFoundError:
        pass
    return ignore_patterns

def is_ignored(file_path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def dir_to_json(directory):
    result = {}
    ignore_patterns = []
    for root, dirs, files in os.walk(directory):
        gitignore_path = os.path.join(root, '.gitignore')
        ignore_patterns.extend(parse_gitignore(gitignore_path))

        relative_path = os.path.relpath(root, directory)
        if relative_path == ".":
            relative_path = ""
        sub_result = result
        if relative_path:
            for part in relative_path.split(os.sep):
                sub_result = sub_result.setdefault(part, {})

        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, directory)
            if not is_ignored(relative_file_path, ignore_patterns):
                file_content = read_file(file_path)
                if file_content is not None:
                    sub_result[file] = file_content
    return result

def main():
    directory = r'.'
    json_data = dir_to_json(directory)
    json_output = os.path.join(directory, 'output.json')

    with open(json_output, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    print(f"JSON data has been written to {json_output}")

if __name__ == "__main__":
    main()
