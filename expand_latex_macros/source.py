import regex as re

def remove_macro_specific_commands(input_string):
    # Removes \ensuremath{...} which is often used within macros
    pattern = r"\\ensuremath\s*({(?:[^{}]*+|(?1))*})"
    while re.search(pattern, input_string):
        match = re.search(pattern, input_string)[1][1:-1].replace("\\", "\\\\")
        input_string = re.sub(pattern, match, input_string)
    
    # Removes \xspace, which is usually used to fix spacing issues within macros
    pattern = r"\\xspace"
    while re.search(pattern, input_string):
        input_string = re.sub(pattern, "", input_string)
    
    return input_string

def parse_macros(latex_source):
    # Find all \def definitions with or without arguments
    pattern = r"\\def\s*\\(\w+)\s*(?:#\d\s*)*\s*({(?:[^{}]*+|(?2))*})"
    matches = re.findall(pattern, latex_source)
    command_mappings = {f"\\{name}" : remove_macro_specific_commands(definition[1:-1]) for name, definition in matches}

    # Find all \newcommand definitions
    pattern = r"\\newcommand\*?\s*{?\s*\\(\w+)\s*}?\s*(?:\[\s*\d+\s*\])*\s*({(?:[^{}]*+|(?2))*})"
    matches = re.findall(pattern, latex_source)
    command_mappings.update({f"\\{name}" : remove_macro_specific_commands(definition[1:-1]) for name, definition in matches})

    return command_mappings

def sub_command_for_def(string, command, definition):
    # Check if command definition uses args
    # If yes args
    if re.search(r"#\d+", definition):
        pattern = re.escape(command) + r"((?:\s*\{[^}]+\})+)"
        args = re.findall(pattern, string)
        pattern = r"\{([^}]+)\}"
        expanded_args = []
        for arg in args:
            expanded_args.append(re.findall(pattern, arg))
        for i, arg in enumerate(args):
            command_call = command + arg
            sub_for_args = {}
            for j, expanded_arg in enumerate(expanded_args[i]):
                sub_for_args[f"#{j+1}"] = expanded_arg
            pattern = re.compile("|".join(re.escape(key) for key in sub_for_args.keys()))
            subbed_definition = pattern.sub(lambda match: sub_for_args[match.group(0)], definition)
            string = string.replace(command_call, subbed_definition)
        return string
    # If no args
    else:
        pattern = re.escape(command) + r"\b"
        definition = definition.replace('\\', '\\\\')
        return re.sub(pattern, definition, string)

def expand_nested_macros(command_mappings, verbose=False):
    # since some user-defined commands may make reference to other user-defined
    # commands, loop through the dictionary until all commands are expanded back into raw LaTeX
    changed = True
    while changed:
        # assume no changes need to be made
        changed = False

        recursive_commands = []
        for command in command_mappings:
            definition = command_mappings[command]
            # find all LaTeX commands present in the definition
            pattern = r"\\(\w+)"
            nested_commands = re.findall(pattern, definition)
            # Sort by inverse length to prevent accidental replacements of \\command_longname by \\command
            nested_commands.sort(key=lambda string : 1.0 / len(string))
            for nested_command in nested_commands:
                nested_command = f"\\{nested_command}"
                # This module cannot handle recursive commands
                if nested_command == command:
                    if verbose:
                        print(f"Cannot handle recursively defined macro {command}. Not attempting.")
                    recursive_commands.append(command)
                # replace all nested user-defined commands
                elif nested_command in command_mappings.keys():
                    nested_definition = command_mappings[nested_command]
                    definition = sub_command_for_def(definition, nested_command, nested_definition)
                    changed = True
            if changed:
                command_mappings[command] = definition
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
        definition = command_mappings[command]
        latex_source = sub_command_for_def(latex_source, command, definition)
    return latex_source

def expand_latex_macros(latex_source, *args, **kwargs):
    verbose = kwargs.get('verbose', True)
    macros_source = latex_source
    for extra_macros_source in args:
        macros_source += open(extra_macros_source).read()
    command_mappings = expand_nested_macros(parse_macros(macros_source), verbose=verbose)
    return sub_macros_for_defs(latex_source, command_mappings)