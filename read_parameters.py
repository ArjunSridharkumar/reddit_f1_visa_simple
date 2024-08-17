def load_parameters(file_path):
    parameters = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            parameters[key] = value
    return parameters

# Usage
# parameters = load_parameters('parameters.txt')
# print(parameters)
