import re

# Patterns for semantic checks
patterns = {
    "override": re.compile(r"^@override\s*$"),
    "variable": re.compile(r"^(int|double|string|bool)\s+([a-zA-Z][a-zA-Z0-9]*)\s*=\s*([\d\.]+|true|false|\".*\")\s*$"),
    "constant": re.compile(r"^fix\s+(int|double|string|bool)\s+([a-zA-Z][a-zA-Z0-9]*)\s*=\s*([\d\.]+|true|false|\".*\")\s*$"),
    "if_statement": re.compile(r"^When\s+([a-zA-Z][a-zA-Z0-9]*)\s*[<>=!]+\s*\d+\s*\{\s*$"),
    "then_statement": re.compile(r"^then\s+([a-zA-Z][a-zA-Z0-9]*)\s*[<>=!]+\s*\d+\s*\{\s*$"),
    "else_statement": re.compile(r"^otherwise\s*\{\s*$"),
    "for_loop": re.compile(r"^hoop\s*\(\s*([a-zA-Z][a-zA-Z0-9]*)\s*…\s*(\d+)\s*,\s*steps:\s*(\d+)\s*\)\s*\{"),
    "while_loop": re.compile(r"^while\s*\(\s*([a-zA-Z][a-zA-Z0-9]*)\s*…\s*(\d+)\)\s*\{"),
    "function": re.compile(r"^(func|Func)\s+[a-zA-Z][a-zA-Z0-9]*\s*\(\s*((int|double|string|bool)\s+[a-zA-Z][a-zA-Z0-9]*\s*=\s*([\d\.]+|true|false|\".*\")\s*,?\s*)*\)\s+(int|double|string|bool|void)?\s*\{"),
    "array": re.compile(r"^(only|all|family|package)?\s+(int|double|string|bool)\s+([a-zA-Z][a-zA-Z0-9]*)\s*=\s*\[(.*?)\]\s*$"),
    "array_access": re.compile(r"([a-zA-Z][a-zA-Z0-9]*)\s*\[(\d+)\]\s*"),
    "class_declaration": re.compile(r"^(only|family|all|package)?\s*class\s+([A-Z][a-zA-Z0-9]*)\s*(inherit\s+([A-Z][a-zA-Z0-9]*))?\s*\{"),
    "abstract_class": re.compile(r"^abstract\s+class\s+([A-Z][a-zA-Z0-9]*)\s*\{"),
    "switch": re.compile(r"^switch\s*\(\s*([a-zA-Z][a-zA-Z0-9]*)\s*\)\s*\{"),
    "case": re.compile(r"^case\s+([\d\.]+|true|false|\".*\")\s*:\s*$"),
    "abstract_method": re.compile(r"^abstract\s+(all|family|only|package)?\s+[a-zA-Z][a-zA-Z0-9]*\s*\(.*\)\s*\{"),
    "comment": re.compile(r"^//.*$"),
    "constructor": re.compile(r"^\s*[a-zA-Z][a-zA-Z0-9]*\s*\(\s*(string\s+[a-zA-Z][a-zA-Z0-9]*\s*=\s*\".*\")?\s*\)\s*\{"),
    "function": re.compile(r"^(func|Func)\s+([a-zA-Z][a-zA-Z0-9]*)\s*\(\s*((int|double|string|bool)\s+[a-zA-Z][a-zA-Z0-9]*\s*=\s*([\d\.]+|true|false|\".*\")\s*,?\s*)*\)\s*(int|double|string|bool|void)?\s*\{")
}

# Data structures to track variable types, constants, functions, classes, and arrays
variables = {}
constants = {}
functions = {}
classes = {}
current_class = None
abstract_methods = {}
arrays = {}  # To keep track of arrays and their types and lengths
switch_cases = {}
switch_expression = None
condition_sequences = []

# Scope tracking
scope_stack = [{}]  # A stack of dictionaries to manage scope levels

def add_to_scope(var_name, var_type, is_constant=False):
    if is_constant:
        constants[var_name] = var_type
    else:
        variables[var_name] = var_type
    scope_stack[-1][var_name] = var_type

def check_variable_redeclaration(variable_name, line_num):
    """Check if a variable is already declared in the current scope."""
    if variable_name in scope_stack[-1]:
        print(f"Semantic Error: Line {line_num} - Variable '{variable_name}' redeclared in the current scope.")

def check_assignment_type(variable_type, assigned_value, line_num):
    """Check if the assigned value is compatible with the variable type."""
    if variable_type == "int" and not re.match(r"^\d+$", assigned_value):
        print(f"Semantic Error: Line {line_num} - Value '{assigned_value}' is not a valid integer.")
    elif variable_type == "double" and not re.match(r"^\d+\.\d+$", assigned_value):
        print(f"Semantic Error: Line {line_num} - Value '{assigned_value}' is not a valid double.")
    elif variable_type == "bool" and assigned_value not in ["true", "false"]:
        print(f"Semantic Error: Line {line_num} - Value '{assigned_value}' is not a valid boolean.")
    elif variable_type == "string" and not re.match(r"^\".*\"$", assigned_value):
        print(f"Semantic Error: Line {line_num} - Value '{assigned_value}' is not a valid string.")

def check_abstract_method_implementation(class_name, line_num):
    """Check if all abstract methods are implemented in a subclass."""
    if class_name in abstract_methods and abstract_methods[class_name]:
        for method in abstract_methods[class_name]:
            print(f"Semantic Error: Line {line_num} - Class '{class_name}' does not implement abstract method '{method}'.")

def enforce_const_immutability(variable_name, line_num):
    """Check if there is an attempt to reassign a constant."""
    if variable_name in constants:
        print(f"Semantic Error: Line {line_num} - Cannot reassign constant '{variable_name}'.")

def enforce_naming_rules(identifier, line_num):
    """Ensure identifier naming rules are followed."""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", identifier):
        print(f"Semantic Error: Line {line_num} - Invalid identifier name '{identifier}'.")

def check_array_bounds(array_name, index, line_num):
    """Check if the array index is within the bounds."""
    if array_name in arrays:
        if index < 0 or index >= len(arrays[array_name]):
            print(f"Semantic Error: Line {line_num} - Index '{index}' out of bounds for array '{array_name}'.")

def check_array_type(array_name, element_type, line_num):
    """Check if the type of elements matches the array type."""
    if array_name in arrays:
        expected_type = arrays[array_name]["type"]
        if expected_type != element_type:
            print(f"Semantic Error: Line {line_num} - Type mismatch for array '{array_name}'. Expected '{expected_type}', got '{element_type}'.")

# Helper to check if return type is valid
def check_return_type(return_type, returned_value, line_num):
    """Check if the returned value is compatible with the function's return type."""
    if return_type == "int" and not re.match(r"^\d+$", returned_value):
        print(f"Semantic Error: Line {line_num} - Return value '{returned_value}' is not a valid integer.")
    elif return_type == "double" and not re.match(r"^\d+\.\d+$", returned_value):
        print(f"Semantic Error: Line {line_num} - Return value '{returned_value}' is not a valid double.")
    elif return_type == "bool" and returned_value not in ["true", "false"]:
        print(f"Semantic Error: Line {line_num} - Return value '{returned_value}' is not a valid boolean.")
    elif return_type == "string" and not re.match(r"^\".*\"$", returned_value):
        print(f"Semantic Error: Line {line_num} - Return value '{returned_value}' is not a valid string.")
    elif return_type == "void" and returned_value is not None:
        print(f"Semantic Error: Line {line_num} - Void function should not return a value.")




def semantic_analyzer(code):
    global current_class, switch_cases, switch_expression, condition_sequences
    #global current_class
    lines = code.splitlines()

    in_condition_block = False 

    for line_num, line in enumerate(lines, start=1):
        line = line.strip()

        # Ignore comments
        if patterns["comment"].match(line):
            continue

        # Variable declarations
        match = patterns["variable"].match(line)
        if match:
            var_type, var_name, assigned_value = match.groups()
            if var_name:
                enforce_naming_rules(var_name, line_num)
            check_variable_redeclaration(var_name, line_num)
            check_assignment_type(var_type, assigned_value, line_num)
            add_to_scope(var_name, var_type)
            continue


         # Check for valid access modifiers
        access_modifier_match = re.match(r"^(only|all|family|package)?\s*", line)
        if access_modifier_match:
            modifier = access_modifier_match.group(1)
            if modifier:
                # Check if access modifier is used in the appropriate context
                if not (
                    patterns["variable"].match(line) or
                    patterns["constant"].match(line) or
                    patterns["class_declaration"].match(line) or
                    patterns["function"].match(line) or
                    patterns["abstract_method"].match(line)
                ):
                    print(f"Semantic Error: Line {line_num} - '{modifier}' access modifier used incorrectly.")


        
         # Start of a When conditional block
        if patterns["if_statement"].match(line):
            if in_condition_block:
                print(f"Semantic Error: Line {line_num} - 'When' statement found before closing previous conditional block.")
            condition_sequences = ["When"]
            in_condition_block = True
            continue

        # Then statement in conditional sequence
        elif patterns["then_statement"].match(line):
            if not in_condition_block or "When" not in condition_sequences:
                print(f"Semantic Error: Line {line_num} - 'then' statement must follow a 'When' condition.")
            condition_sequences.append("then")
            continue

        # Otherwise statement in conditional sequence
        elif patterns["else_statement"].match(line):
            if not in_condition_block or ("When" not in condition_sequences and "then" not in condition_sequences):
                print(f"Semantic Error: Line {line_num} - 'otherwise' must follow a 'When' or 'then' condition.")
            condition_sequences.append("otherwise")
            in_condition_block = False  # End of the conditional sequence
            continue

        # End of conditional block
        elif line == "}":
            if in_condition_block and "otherwise" not in condition_sequences:
                print(f"Semantic Error: Line {line_num} - Conditional block missing 'otherwise' clause.")
            condition_sequences = []
            in_condition_block = False


        # Function declarations with parameter type checking
        match = patterns["function"].match(line)
        if match:
            return_type = match.group(6)  # Return type if specified
            function_name = match.group(2)
            param_list = match.group(3)

            enforce_naming_rules(function_name, line_num)

            # Check if function is already declared
            if function_name in functions:
                print(f"Semantic Error: Line {line_num} - Function '{function_name}' redeclared.")
            else:
                functions[function_name] = {
                    "return_type": return_type or "void",
                    "parameters": param_list or "",
                    "declared": True,
                    "has_return": False
                }
            continue

        # Check for return statements
        if line.startswith("yield") or line.startswith("return"):
            return_match = re.match(r"(yield|return)\s+(.*)", line)
            if return_match:
                return_statement, returned_value = return_match.groups()
                current_function = next(
                    (f for f, v in functions.items() if v["declared"] and not v["has_return"]),
                    None
                )

                if current_function:
                    expected_type = functions[current_function]["return_type"]
                    check_return_type(expected_type, returned_value, line_num)
                    functions[current_function]["has_return"] = True
            continue

        # Function scope ending (checking for missing return statements)
        if line == "}":
            for func, details in functions.items():
                if details["declared"] and details["return_type"] != "void" and not details["has_return"]:
                    print(f"Semantic Error: Function '{func}' missing return statement.")



        # Constant declarations
        match = patterns["constant"].match(line)
        if match:
            const_type, const_name, const_value = match.groups()
            if const_name:
                enforce_naming_rules(const_name, line_num)
            check_variable_redeclaration(const_name, line_num)
            check_assignment_type(const_type, const_value, line_num)
            add_to_scope(const_name, const_type, is_constant=True)
            continue

        # Array declarations
        match = patterns["array"].match(line)
        if match:
            visibility, array_type, array_name, elements = match.groups()
            # Set visibility to None if not provided
            if visibility is None:
                visibility = "default"  # or any default behavior you want
            enforce_naming_rules(array_name, line_num)
            check_variable_redeclaration(array_name, line_num)
            elements_list = [elem.strip() for elem in elements.split(",") if elem.strip()]
            arrays[array_name] = {"type": array_type, "elements": elements_list}
            for elem in elements_list:
                check_assignment_type(array_type, elem, line_num)
            add_to_scope(array_name, f"{array_type}[]")  # Register array in scope
            continue

        # Conditionals
        match = patterns["if_statement"].match(line)
        if match:
            condition_var = match.group(1)
            if condition_var not in variables:
                print(f"Semantic Error: Line {line_num} - Variable '{condition_var}' is undeclared.")
            continue

        # Loops
        match = patterns["for_loop"].match(line)
        if match:
            loop_var, range_end, step = match.groups()
            if loop_var not in variables:
                print(f"Semantic Error: Line {line_num} - Variable '{loop_var}' is undeclared.")
            continue

        match = patterns["while_loop"].match(line)
        if match:
            while_var, range_end = match.groups()
            if while_var not in variables:
                print(f"Semantic Error: Line {line_num} - Variable '{while_var}' is undeclared.")
            continue

        # Function declarations
        match = patterns["function"].match(line)
        if match:
            function_name = match.group(2)
            if function_name:
                enforce_naming_rules(function_name, line_num)
                if function_name in functions:
                    print(f"Semantic Error: Line {line_num} - Function '{function_name}' redeclared.")
                functions[function_name] = True
            else:
                print(f"Semantic Error: Line {line_num} - Function name missing.")
            continue

        # Class declarations
        match = patterns["class_declaration"].match(line)
        if match:
            visibility, class_name, _, inheritance = match.groups()
            if class_name:
                enforce_naming_rules(class_name, line_num)
                if class_name in classes:
                    print(f"Semantic Error: Line {line_num} - Class '{class_name}' redeclared.")
                classes[class_name] = inheritance
                current_class = class_name
            else:
                print(f"Semantic Error: Line {line_num} - Class name missing.")
            continue

        # Abstract class declarations
        match = patterns["abstract_class"].match(line)
        if match:
            class_name = match.group(1)
            if class_name:
                enforce_naming_rules(class_name, line_num)
                if class_name in classes:
                    print(f"Semantic Error: Line {line_num} - Abstract class '{class_name}' redeclared.")
                abstract_methods[class_name] = []
                current_class = class_name
            else:
                print(f"Semantic Error: Line {line_num} - Abstract class name missing.")
            continue

        # Abstract method declarations
        match = patterns["abstract_method"].match(line)
        if match:
            method_name = match.group(0)
            if method_name:
                enforce_naming_rules(method_name, line_num)
                if current_class in abstract_methods:
                    abstract_methods[current_class].append(method_name)
            else:
                print(f"Semantic Error: Line {line_num} - Abstract method name missing.")
            continue

        # Constant reassignment enforcement
        words = line.split()
        if len(words) >= 3 and words[1] == "=":
            variable_name = words[0]
            enforce_const_immutability(variable_name, line_num)

        # Array access and bounds checking
        array_match = patterns["array_access"].search(line)
        if array_match:
            array_name = array_match.group(1)
            index = int(array_match.group(2))
            check_array_bounds(array_name, index, line_num)

        # Reset class context at end of a class declaration
        if line == "}":
            if current_class and current_class in abstract_methods:
                check_abstract_method_implementation(current_class, line_num)
            current_class = None

        # Switch statement
        match = patterns["switch"].match(line)
        if match:
            switch_expression = match.group(1)
            if switch_expression in scope_stack[-1]:
                switch_cases.clear()  # Reset for new switch
                continue
            else:
                print(f"Semantic Error: Line {line_num} - Switch variable '{switch_expression}' is undeclared.")
                continue

        # Case statement
        match = patterns["case"].match(line)
        if match:
            case_value = match.group(1)
            if switch_expression:
                if case_value in switch_cases:
                    print(f"Semantic Error: Line {line_num} - Duplicate case value '{case_value}'.")
                else:
                    switch_cases[case_value] = True  # Add the case value
            else:
                print(f"Semantic Error: Line {line_num} - Case '{case_value}' without a valid switch.")
            continue


# Test input
sample_code = """@override
only bool var = [true,false,5]
fix int a = 25
a = 70
double b = 100
When b < 10 {
    // code
    b += 1
}
then b > 10 { 
    // code
}
otherwise {
    // code
}
hoop ( b … 200 , steps: 1 ){
    // code
}
while (b … 200){
    // code
b+= 2
}
double b = 2.5
bool c = true
string sole = "ss"
func name(int a = 1  , int b = 1 ) int {
    // code
yield 1.5
}
func name(int a = 1  , int b = 1 ) int {
    // code
}
only class Animal inherit Mamals{
    Animal(string pet = "lol"){
        // code
    }
    // code
}
abstract class Animal {
    abstract all talk(string pet = "cat") {
    //code
    }
}
only class Dog inherit Animal {
    abstract all talk(string pet = "dog") {
        // code
    }
}
class Animal {
    fix string name = "Lion"
    int age = 10
    override func makeSound() {
        // some code
    }
}
class Dog inherit Animal {
    func makeSound() {
        // implementation
    }
}
When age >= 5 {
    // some condition
}
hoop (i … 10, steps: 2) {
    // loop body
}

only class MyClass {
    func method() {
        switch x {
            case 5:
                // Do something
            case 10:
                // Do something else
            case 5: // Duplicate case
                // Do another thing
        }
    }
}
"""
semantic_analyzer(sample_code)
