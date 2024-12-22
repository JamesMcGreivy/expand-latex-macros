import regex as re

def parse_macros_noarg(latex_source):
    # Find all \def definitions without arguments
    pattern = r"\\def\s*\\(\w+)\s*({(?:[^{}]*+|(?2))*})"
    matches = re.findall(pattern, latex_source)
    command_mappings = {f"\\{name}" : definition[1:-1] for name, definition in matches}

    # Find all \newcommand definitions without arguments
    pattern = r"\\newcommand\s*{\s*\\(\w+)\s*}\s*({(?:[^{}]*+|(?2))*})"
    matches = re.findall(pattern, latex_source)
    command_mappings.update({f"\\{name}" : definition[1:-1] for name, definition in matches})

    return command_mappings

def expand_nested_macros(command_mappings):
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
                    print(f"Cannot handle recursively defined macro {command}. Not attempting.")
                    recursive_commands.append(command)
                # replace all nested user-defined commands
                elif nested_command in command_mappings.keys():
                    definition = definition.replace(nested_command, 
                    command_mappings[nested_command])
                    changed = True
            if changed:
                command_mappings[command] = definition
        [command_mappings.pop(command) for command in recursive_commands]
    return command_mappings

def sub_macros_for_defs(latex_source, command_mappings):
    # Remove all macro definitions from source
    pattern = r"\\def\s*\\(\w+)\s*({(?:[^{}]*+|(?2))*})"
    latex_source = re.sub(pattern, "", latex_source)
    pattern = r"\\newcommand\s*{\s*\\(\w+)\s*}\s*({(?:[^{}]*+|(?2))*})"
    latex_source = re.sub(pattern, "", latex_source)
    # Remove excessive newlines
    latex_source = re.sub(r'(?<!\\)(\n){2,}', r'\1', latex_source)

    for command in command_mappings:
        definition = command_mappings[command]
        pattern = re.escape(command) + r"\b"
        definition = definition.replace('\\', '\\\\')
        latex_source = re.sub(pattern, definition, latex_source)
    return latex_source

def expand_latex_macros(latex_source_path):
    latex_source = open(latex_source_path).read()
    command_mappings = expand_nested_macros(parse_macros_noarg(latex_source))
    return sub_macros_for_defs(latex_source, command_mappings)