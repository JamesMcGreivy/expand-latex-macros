import regex as re

# Removes \ensuremath{...} and \xspace from LaTeX macros.
def remove_macro_specific_commands(input_string):
    for pattern in [r"\\ensuremath{", r"\\mathrm\s*{", r"\\textrm\s*{", r"\\mbox\s*{"]:
        while re.search(pattern, input_string):
            match = re.search(pattern, input_string)
            command_start = match.start()
            command_end = match.end()
            end = find_matching_brace(input_string, command_end)
            if end:
                content = input_string[command_end:end]
                input_string = input_string[:command_start] + content + input_string[end + 1:]

    input_string = re.sub(r"\\xspace", "", input_string)
    input_string = re.sub(r"\\rm\s", "", input_string)
    input_string = re.sub(r"\\[,!;.:]", "", input_string)
    return input_string

# Finds the matching closing brace for a given opening brace index.
def find_matching_brace(text, start_index):
    brace_count = 1
    for i in range(start_index, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return i
    return None  # No matching brace found

# Counts the number of arguments (#1, #2, ...) in a \def macro.
def def_args_to_num_args(args):
    return len(re.findall(r"#\d", args))

# Counts the number of arguments from a \newcommand declaration.
def newcommand_args_to_num_args(args):
    match = re.search(r"\[(\d+)\]", args)
    return int(match.group(1)) if match else 0

# Extracts macro definitions using a stack-based approach for nested {} handling.
def extract_definitions(text, pattern, args_to_num_args):
    matches = {}
    for match in re.finditer(pattern, text):
        name, args = match.group(1), match.group(2)
        start = match.end()
        end = find_matching_brace(text, start)
        if end:
            definition = text[start:end]
            matches[f"\\{name}"] = {
                "num_args": args_to_num_args(args),
                "definition": remove_macro_specific_commands(definition)
            }
    return matches

# Parses \def and \newcommand macros from LaTeX source.
def parse_macros(latex_source):
    # Patterns for \def and \newcommand
    def_pattern = r"\\def\s*\\(\w+)\s*((?:#\d\s*)*)\s*{"
    newcommand_pattern = r"\\newcommand\*?\s*{?\s*\\(\w+)\s*}?\s*((?:\[\s*\d+\s*\])*)\s*{"
    command_mappings = extract_definitions(latex_source, def_pattern, def_args_to_num_args)
    command_mappings.update(extract_definitions(latex_source, newcommand_pattern, newcommand_args_to_num_args))
    return command_mappings

def sub_command_for_def(string, command, definition, num_args):
    # Check if command definition uses args
    
    # If yes args
    if num_args > 0:
        pattern = re.escape(command)
        for i in range(num_args):
            pattern += r"\s*({(?:[^{}]|(?" + f"{i+1}" + r"))*})"
       
        args = re.findall(pattern, string)
        for i, arg in enumerate(args):
            
            sub_for_args = {}
            if num_args > 1:
                for j, arg_j in enumerate(arg):
                    sub_for_args[f"#{j+1}"] = arg_j[1:-1]
            else:
                sub_for_args[f"#{1}"] = arg[1:-1]
            
            pattern = re.compile("|".join(re.escape(key) for key in sub_for_args.keys()))
            subbed_definition = pattern.sub(lambda match: sub_for_args[match.group(0)], definition)
            pattern = re.escape(command)
            for arg_j in arg:
                pattern += r"\s*" + re.escape(arg_j)
            subbed_definition = subbed_definition.replace('\\', '\\\\')
            string = re.sub(pattern, subbed_definition, string)
        
        return string
    
    # If no args
    else:
        pattern = re.escape(command) + r"\b"
        definition = definition.replace('\\', '\\\\')
        return re.sub(pattern, definition, string)

def expand_nested_macros(command_mappings):
    # since some user-defined commands may make reference to other user-defined
    # commands, loop through the dictionary until all commands are expanded back into raw LaTeX
    changed = True
    while changed:
        # assume no changes need to be made
        changed = False

        recursive_commands = []
        for command in command_mappings:
            definition = command_mappings[command]['definition']
            # find all LaTeX commands present in the definition
            pattern = r"\\(\w+)"
            nested_commands = re.findall(pattern, definition)
            # Sort by inverse length to prevent accidental replacements of \\command_longname by \\command
            nested_commands.sort(key=lambda string : 1.0 / len(string))
            for nested_command in nested_commands:
                nested_command = f"\\{nested_command}"
                # This module cannot handle recursive commands
                if nested_command == command:
                    #print(f"Cannot handle recursively defined macro {command}. Not attempting.")
                    recursive_commands.append(command)
                # replace all nested user-defined commands
                elif nested_command in command_mappings.keys():
                    nested_definition = command_mappings[nested_command]['definition']
                    nested_args = command_mappings[nested_command]['num_args']
                    definition = sub_command_for_def(definition, nested_command, nested_definition, nested_args)
                    changed = True
            if changed:
                command_mappings[command]['definition'] = definition
        [command_mappings.pop(command) for command in recursive_commands]
    return command_mappings

def sub_macros_for_defs(latex_source, command_mappings):
    # Remove all macro definitions from source
    pattern = r"\\def\s*\\(\w+)\s*(?:#\d\s*)*\s*({(?:[^{}]*+|(?2))*})"
    latex_source = re.sub(pattern, "", latex_source)
    pattern = r"\\newcommand\*?\s*{?\s*\\(\w+)\s*}?\s*(?:\[\s*\d+\s*\])*\s*({(?:[^{}]*+|(?2))*})"
    latex_source = re.sub(pattern, "", latex_source)
    # Remove excessive newlines
    latex_source = re.sub(r'(?<!\\)(\n\s*){2,}', r'\1', latex_source)

    for command in command_mappings:
        definition = command_mappings[command]['definition']
        args = command_mappings[command]['num_args']
        latex_source = sub_command_for_def(latex_source, command, definition, args)
    return latex_source

def expand_latex_macros(latex_source, extra_macro_sources=[], commands_dont_expand=[]):
    macros_source = latex_source
    for source in extra_macro_sources:
        macros_source += source
    command_mappings = parse_macros(macros_source)
    for command in commands_dont_expand:
        command_mappings.pop(command, None)
    command_mappings = expand_nested_macros(command_mappings)
    return sub_macros_for_defs(latex_source, command_mappings)