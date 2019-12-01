import ast
import pandas as pd
import numpy as np


class Matchmaker(ast.NodeVisitor):
    def __init__(self):
        self.mods = pd.DataFrame(columns=['name', 'asname', 'from'])
        self.calls = pd.DataFrame(columns=['line', 'obj', 'name'])
        self.assign = pd.DataFrame(columns=['line', 'var', 'call_obj', 'call_name'])
        self.matchs = pd.DataFrame(columns=['line', 'function', 'package', 'class'])

    def visit_Import(self, node):
        for alias in node.names:
            self.mods = self.mods.append({'name': alias.name, 'asname': alias.asname}, ignore_index=True)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.mods = self.mods.append({'name': alias.name, 'asname': alias.asname, 'from': node.module},
                                         ignore_index=True)
        self.generic_visit(node)

    def visit_Call(self, node):
        if type(node.func).__name__ == 'Name':
            self.calls = self.calls.append({'line': node.lineno, 'name': node.func.id}, ignore_index=True)
        # Take care of multiple function called in one line
        elif type(node.func).__name__ == 'Attribute':
            call = node.func
            count = 0
            while count == 0:
                try:
                    if type(call.value).__name__ == 'Name':
                        self.calls = self.calls.append({'line': node.lineno, 'name': node.func.attr, 'obj': call.value.id},
                                                       ignore_index=True)
                        count = 1
                    else:
                        call = call.value.func
                except AttributeError:
                    break
        self.generic_visit(node)

    def visit_Assign(self, node):
        if type(node.value).__name__ == 'Call':
            for name in node.targets:
                call_0 = node.value.func
                # Take care of multiple function called in one line
                if type(call_0).__name__ == 'Name':
                    self.assign = self.assign.append({'line': node.lineno, 'var': name.id, 'call_name': call_0.id},
                                                     ignore_index=True)
                elif type(call_0).__name__ == 'Attribute':
                    call = call_0
                    count = 0
                    while count == 0:
                        try:
                            if type(call.value).__name__ == 'Name':
                                self.assign = self.assign.append(
                                    {'line': node.lineno, 'var': name.id, 'call_obj': call.value.id,
                                    'call_name': call.attr}, ignore_index=True)
                                count = 1
                            else:
                                call = call.value.func
                        except AttributeError:
                            break
        self.generic_visit(node)

    # This function takes a row of self.assign a and the function name c to match with the modules
    def a_match(self, a, c):
        if a['call_obj'] is not np.nan:
            isname = self.mods[self.mods.name.isin([a['call_obj']])]
            isas = self.mods[self.mods.asname.isin([a['call_obj']])]
            isfrom = self.mods[self.mods['from'].isin([a['call_obj']])]
            if not isname.empty:
                mod = list(isname['name'])
                if a['call_name'][0].isupper():
                    self.matchs = self.matchs.append(
                        {'line': c['line'], 'function': c['name'], 'package': mod[0], 'class': a['call_name']},
                        ignore_index=True)
                else:
                    self.matchs = self.matchs.append(
                        {'line': c['line'], 'function': c['name'], 'package': mod[0]},
                        ignore_index=True)
            elif not isas.empty:
                mod = list(isas['name'])
                if a['call_name'][0].isupper():
                    self.matchs = self.matchs.append(
                        {'line': c['line'], 'function': c['name'], 'package': mod[0], 'class': a['call_name']},
                        ignore_index=True)
                else:
                    self.matchs = self.matchs.append(
                        {'line': c['line'], 'function': c['name'], 'package': mod[0]},
                        ignore_index=True)
            elif not isfrom.empty:
                mod = list(isfrom['from'])
                modc = list(isfrom['name'])
                self.matchs = self.matchs.append(
                    {'line': c['line'], 'function': c['name'], 'package': mod[0], 'class': modc[0]},
                    ignore_index=True)
            else:
                return 0
            return 1

        else:
            self.matchs = self.matchs.append({'line': a['line'], 'function': c, 'class': a['call_name']},
                                             ignore_index=True)

    def match(self, call):
        if call['obj'] is not np.nan:
            isname = self.mods[self.mods['name'].isin([call['obj']])]
            isas = self.mods[self.mods['asname'].isin([call['obj']])]
            isfrom = self.mods[self.mods['from'].isin([call['obj']])]
            if not isname.empty:
                mod = list(isname['name'])
                self.matchs = self.matchs.append({'line': call['line'], 'function': call['name'], 'package': mod[0]},
                                                 ignore_index=True)
            elif not isas.empty:
                mod = list(isas['name'])
                self.matchs = self.matchs.append({'line': call['line'], 'function': call['name'], 'package': mod[0]},
                                                 ignore_index=True)
            elif not isfrom.empty:
                mod = list(isfrom['from'])
                modc = list(isfrom['name'])
                self.matchs = self.matchs.append(
                    {'line': call['line'], 'function': call['name'], 'package': mod[0], 'class': modc[0]},
                    ignore_index=True)
            else:
                # Matching the function call object with list of assigned variables
                # Filter out Assignments that came after the function call
                before = self.assign[self.assign['line'] < call['line']]
                isobj = before[before['var'].isin([call['obj']])]
                if not isobj.empty:
                    for index, a in isobj.sort_values(by='line', axis=0, ascending=False).iterrows():
                        r = self.a_match(a, call)
                        # If module name was found exit the loop
                        if r == 1:
                            break

        else:
            self.matchs = self.matchs.append({'line': call['line'], 'function': call['name']}, ignore_index=True)

    def matching(self):
        self.calls.apply(lambda x: self.match(x), axis=1)
        return self.matchs

    def get_Import(self):
        return self.mods

    def get_Call(self):
        return self.calls

    def get_Assign(self):
        return self.assign

    def get_Match(self):
        return self.matchs
