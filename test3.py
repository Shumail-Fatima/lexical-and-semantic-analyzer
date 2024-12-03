import re
def lexical_analyzer(input_string):
    # Define regular expression patterns
    inp = input_string
    identifier_pattern = re.compile('^([.])([a-zA-A]|[0-9])*([a-zA-Z])$')   #  .(l+d)*l
    constant_pattern = re.compile(r'^\d+$')

    # Define dictionaries for keywords and data types
    keywords = {'otherwise','check','hoop','premise'}
    data_types = {'nume'}
    logical_operators = {'&&','||','=!'}
    doublechar_conditional_op = {'==','<=','>='}

    # Initialize list to store tokens
    tokens = []

    input_tokens = inp.split()
    for token in input_tokens:
        # Check if token is a keyword
        if token in keywords:
            tokens.append(('keyword', token))
        # Check if token is a data type
        elif token in data_types:
            tokens.append(('datatype', token))
        # Check if token is a logical_operator
        elif token in logical_operators:
            tokens.append(('logical operator', token))
         # Check if token is a 
        elif token in doublechar_conditional_op:
            tokens.append(('doublechar conditional operator', token))
        # Check if token is an identifier
        elif identifier_pattern.match(token):
            tokens.append(('identifier', token))
        # Check if token is a constant
        elif constant_pattern.match(token):
            tokens.append(('constant', int(token)))
        # Check if token is an operator or symbol
        else:
            # Split token into individual characters
            for char in token:
                # Check if character is an operator
                if char in {'=', '+', '-', '*', '/', '<', '>'}:
                    tokens.append(('operator', char))
                # Check if character is a symbol
                elif char in {'(', ')', ',',':','[',']'}:
                    tokens.append(('symbol', char))
                # If not, raise exception for invalid character
                else:
                    raise Exception(f'Invalid character: {char}')

    return tokens

f = open("prompt.txt")
txt = f.read()
tokens = lexical_analyzer(txt)

for i in range (len(tokens)):
    print(tokens[i],'\n')