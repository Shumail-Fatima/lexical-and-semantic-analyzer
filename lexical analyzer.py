import re
import pandas as pd

# Define token patterns including comments, access modifiers, and annotations
patterns = {
    'KEYWORD': r'\bwhen\b|\botherwise\b|\bthen\b|\bhoop\b|\bwhile\b|\bcontinue\b|\bbreak\b|\bmatch\b|\bselect\b|\bdefault\b|\bfunc\b|\byield\b|\binherit\b|\boverride\b|\babstract\b|\bcurrent\b|\bsuper\b|\bstatic\b',
    'ACCESS_MODIFIER': r'\bonly\b|\ball\b|\bfamily\b|\bpackage\b',
    'ANNOTATION': r'@override\b',
    'CONSTANT': r'\bfix\b',
    'DATA_TYPE': r'\bint\b|\bdouble\b|\bbool\b|\bstring\b|\bvoid\b',
    'COMMENT': r'//.*',  # Pattern for comments
    'RELATIONAL_OPERATOR': r'==|!=|<=|>=|<|>',
    'ARITHMETIC_ASSIGNMENT_OPERATOR': r'\+=|-=|\*=|/=|%=',
    'ASSIGNMENT_OPERATOR': r'=',
    'INCREMENT_DECREMENT_OPERATOR': r'\+\+|--',
    'LOGICAL_OPERATOR': r'&&|\|\|',
    'ARITHMETIC_OPERATOR': r'[+\-*/%]',
    'FLOAT': r'[+-]?\d+\.\d+',  # Float pattern for decimal numbers
    'Int': r'[+-]?\d+',  # Integer pattern for whole numbers
    'CHAR': r"'(?:\\.|[^\\'])'",
    'STRING': r'"(?:\\.|[^"\\])*"',  # Include escape sequences
    'Bool': r'\btrue\b|\bfalse\b',
    'ESCAPE_SEQUENCE': r'\\[\'"\\bfnrt]',
    'RANGE_OPERATOR': r'\…',  # Range operator pattern
    'PUNCTUATOR': r'[\[\]{}();:,]',
    'WHITESPACE': r'\s+',
    'NEWLINE': r'\n',
    'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*',
}

# Combine patterns into a single regex
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in patterns.items())

def tokenize(code):
    tokens = []
    line_no = 1
    current_position = 0

    # Normalize newlines in the code
    code = re.sub(r'\r\n?', '\n', code)

    # Iterate over each match in the code
    for match in re.finditer(token_regex, code):
        start_pos = match.start()
        end_pos = match.end()

        # Update line number for newlines before the current token
        while current_position < start_pos:
            if code[current_position] == '\n':
                line_no += 1
            current_position += 1

        # Process matched token
        for name, value in match.groupdict().items():
            if value:
                if name == 'WHITESPACE' or name == 'COMMENT':
                    continue
                elif name == 'NEWLINE':
                    line_no += 1
                else:
                    # Handle special cases
                    if value == '::':
                        tokens.append({
                            'class part': 'punctuator',
                            'value part': ':',
                            'line no': line_no
                        })
                        tokens.append({
                            'class part': 'punctuator',
                            'value part': ':',
                            'line no': line_no
                        })
                    else:
                        token_class_part = name.replace('_', ' ').lower()
                        if name == 'STRING':
                            # Handle escape sequences in strings
                            value = value.encode('unicode_escape').decode('unicode_escape')
                        # Convert keywords to lowercase
                        if token_class_part == 'keyword':
                            value = value.lower()
                        # Special handling for annotations
                        if name == 'ANNOTATION':
                            token_class_part = 'annotation'
                        # Special handling for access modifiers
                        if name == 'ACCESS_MODIFIER':
                            token_class_part = 'access modifier'
                        tokens.append({
                            'class part': token_class_part,
                            'value part': value,
                            'line no': line_no
                        })

    return tokens

def print_function(tokens):
    # Add token numbers
    for i, token in enumerate(tokens):
        token['token no'] = i + 1

    # Convert tokens to a DataFrame for better presentation
    df = pd.DataFrame(tokens)

    # Reorder columns
    df = df[['token no', 'class part', 'value part', 'line no']]

    # Function to format the DataFrame rows into fixed-width columns
    def format_row(row):
        return "| {:<8} | {:<15} | {:<12} | {:<8} |".format(row['token no'], row['class part'], row['value part'], row['line no'])

    # Header of the table
    header = "| Token No | Class Part     | Value Part  | Line No  |"
    separator = "+---------+----------------+-------------+----------+"

    # Print the table
    print(separator)
    print(header)
    print(separator)

    # Print each row
    for _, row in df.iterrows():
        print(format_row(row))
        print(separator)

# Open and read the code from a file
with open('LexicalTextFile.txt', 'r') as file:
    code = file.read()

tokens = tokenize(code)
print_function(tokens)