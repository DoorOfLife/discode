import regex
from random import randrange


def is_list_access(typ):
    if typ in ["RAND_LIST_ACCESS", "INDEX_LIST_ACCESS", "VARIABLE_LIST_ACCESS"]:
        return True
    else:
        return False

def escape_data_comma(data):
    return data.replace(",", "%%%c%%%")

def unescape_data_comma(data):
    return data.replace('%%%c%%%', ",")

def format_literal(literal):
    return escape_data_comma(literal.strip('"'))


class Interpreter:
    variables = dict()
    output_var_name = "$$OUTPUT$$"

    def execute(self, script, param):

        self.variables["in"] = param

        statements = script.splitlines()
        for line in statements:
            self.execute_statement(line)
            if self.output_var_name in self.variables.keys():
                return self.variables[self.output_var_name]
        return "<No return statement>"

    def execute_statement(self, statement):
        typ = self.determine_statement_type(statement)
        if typ == "ASSIGNMENT":
            self.execute_assignment(statement)
        elif typ == "RETURN":
            self.execute_return_statement(statement)

        return

    def determine_statement_type(self, statement):
        if regex.match('^\s*\S+\s*=\s*\S+\s*$', statement):
            return "ASSIGNMENT"
        elif statement.startswith("return "):
            return "RETURN"
        elif regex.match('^\$\S+\[rand\]\s*$', statement):
            return "RAND_LIST_ACCESS"
        elif regex.match('^\$\S+\[\d+\]\s*$', statement):
            return "INDEX_LIST_ACCESS"
        elif regex.match('^\$\S+\[\$\S+\]\s*$', statement):
            return "VARIABLE_LIST_ACCESS"
        elif regex.match('^\S+\(\S*\)\s*$', statement):
            return "FUNCTION_CALL"
        elif regex.match('^.+\+.+$', statement):
            return "ADDITION"
        elif statement.startswith("$"):
            return "VARIABLE_EXPANSION"
        elif regex.match('^\".*\"$', statement):
            return "LITERAL"
        elif len(statement) == 0:
            return "VOID"
        return "UNDEFINED"

    def execute_assignment(self, statement):
        tokens = statement.split('=')
        if len(tokens) < 2:
            return

        variable = tokens[0].strip()
        value = tokens[1].strip()

        typ = self.determine_statement_type(value)
        if is_list_access(typ):
            value = self.format_variable_reference(value)
            tokenized_list_val = self.expand_list_index_param(value)
            value = self.variables[tokenized_list_val[0]][tokenized_list_val[1]]
        elif typ == "FUNCTION_CALL":
            value = self.execute_function_call(value)
        elif typ == "VARIABLE_EXPANSION":
            value = self.variables[self.dereference_variable_ref(value)]
        elif typ == "ADDITION":
            value = self.execute_combine(value)
        elif typ == "LITERAL":
            value = format_literal(value)
        elif typ == "VOID":
            value = None

        typ = self.determine_statement_type(variable)
        if is_list_access(typ):
            variable = self.format_variable_reference(variable)
            tokenized_list_var = self.expand_list_index_param(variable)
            self.variables[tokenized_list_var[0]][tokenized_list_var[1]] = value
        elif typ == "VARIABLE_EXPANSION":
            self.variables[self.dereference_variable_ref(variable)] = value
        elif typ == "UNDEFINED":
            self.variables[variable] = value

    def expand_list_index_param(self, statement):
        list_name_and_index = self.expand_params(statement, '[', ']')
        if list_name_and_index[1] in ["rand", "void"]:
            list_name_and_index[1] = randrange(0, len(self.variables[list_name_and_index[0]]))
        return list_name_and_index

    def expand_function_params(self, function_call):
        func_and_params = self.expand_params(function_call, '(', ')')
        if regex.match('^\S+\.\S+\(\S*\)\s*$', func_and_params[0]):
            object_function_call = func_and_params[0].split(".")
            dereferenced_value = self.dereference_variable_ref(object_function_call[0])
            func_and_params.insert(1, dereferenced_value)
            func_and_params[0] = object_function_call[1]
        return func_and_params

    def expand_params(self, statement, open_char, close_char):
        tokens = statement.split(open_char)
        ref_no_dollar_sign = tokens[0]
        inner_statement = tokens[1].strip(close_char)
        # if there's an inner function call or literal anywhere, those must be expanded first
        while True:
            match = regex.search('\S+\(\S*\)', inner_statement)
            if match is None:
                break
            expanded_params = self.expand_function_params(match.group())
            # now replace the expanded params with the match
            inner_statement = inner_statement[0, match.start()] + expanded_params + inner_statement[match.end():]

        # now all commas should be non-nested, so expand each item
        inner_tokens = inner_statement.split(',')
        ref_and_tokens = [ref_no_dollar_sign]
        for inner_token in inner_tokens:
            inner_token = inner_token.strip()
            typ = self.determine_statement_type(inner_statement)
            if typ == "UNDEFINED":
                ref_and_tokens.append(inner_token)
            elif is_list_access(typ):
                inner_token = self.expand_list_index_param(inner_token)
                var_index = self.format_variable_reference(inner_token[0])
                val_index = inner_token[1]
                try:
                    ref_and_tokens.append(self.variables[var_index][int(val_index)])
                except IndexError:
                    ref_and_tokens.append(None)
            elif typ == "VARIABLE_EXPANSION":
                ref_and_tokens.append(self.dereference_variable_ref(inner_token))
            elif typ == "FUNCTION_CALL":
                ref_and_tokens.append(self.execute_function_call(inner_token))
            elif typ == "ADDITION":
                ref_and_tokens.append(self.execute_combine(inner_token))
            elif typ == "LITERAL":
                ref_and_tokens.append(format_literal(inner_token))
            elif typ == "VOID":
                ref_and_tokens.append("void")
        return ref_and_tokens

    def execute_combine(self, statement):
        tokens = statement.split("+")
        result_string = ""
        for token in tokens:
            token = token.strip()
            typ = self.determine_statement_type(token)
            if is_list_access(typ):
                tokenized_list = self.expand_list_index_param(token)
                result_string += self.variables[tokenized_list[0]][tokenized_list[1]]
            elif typ == "VARIABLE_EXPANSION":
                var_val = self.dereference_variable_ref(token)
                if isinstance(var_val, list):
                    for val in var_val:
                        result_string += val
                else:
                    result_string += var_val
            elif typ == "LITERAL":
                result_string += format_literal(token)
            elif typ == "FUNCTION_CALL":
                result_string += self.execute_function_call(token)
            else:
                result_string += token

        return result_string

    def execute_function_call(self, statement):
        function_and_params = self.expand_function_params(statement)
        func = function_and_params[0]

        if func == 'split':
            return self._func_split(function_and_params)
        else:
            return ""

    def _func_split(self, params):
        # We expect a piece of text (string) to operate on, and a separator
        return params[1].split(params[2])

    @staticmethod
    def format_variable_reference(statement):
        return statement.strip('$')

    def execute_return_statement(self, value):
        self.variables[self.output_var_name] = value

    def variable_assignment(self, variable, value):
        self.variables[variable] = value

    def dereference_variable_ref(self, value):
        ref = value.strip('$').strip()
        if ref in self.variables.keys():
            return self.variables[ref]
        else:
            return ""

    # todo: handle if value is a list
    def add_value_to_variable(self, variable, value):
        if variable in self.variables.keys():
            if isinstance(self.variables[variable], str):
                self.variables[variable] = [self.variables[variable], value]
            else:
                self.variables[variable].append(value)
        else:
            self.variables[variable] = value
