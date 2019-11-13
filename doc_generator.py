import inspect
import importlib
import pandas as pd


# Get all the functions of a library
def get_functions(module):
    function_list = [o[0] for o in inspect.getmembers(module) if inspect.isfunction(o[1])]
    # drop all functions starting with "_" e.g. __init__ or 'private functions'
    function_list = list(filter(lambda x: (x.startswith("_") is False), function_list))
    return function_list


def get_class_functions(module):
    function_list = []
    class_list = [o[0] for o in inspect.getmembers(module) if inspect.isclass(o[1])]
    for c in class_list:
        c_func = [o[0] for o in inspect.getmembers(getattr(module, c)) if inspect.isfunction(o[1])]
        # drop all functions starting with "_" e.g. __init__ or 'private functions'
        c_filter = list(filter(lambda x: (x.startswith("_") is False), c_func))
        c_final = []
        for f in c_filter:
            c_final.append([c, f])
        function_list.extend(c_final)
    return function_list


# if library name and function is giving, returns docstring
def get_doc(module, function):
    return inspect.getdoc(getattr(module, function))


def generate_docs(imports):
    docs = pd.DataFrame()
    for module in imports:
        docs = docs.append(generate_doc(module), ignore_index=True)
    return docs


def generate_doc(imp):
    docs = pd.DataFrame()
    try:
        # check if library is installed
        base = imp.split(".")
        check = importlib.util.find_spec(base[0])
        if check is None:
            raise ImportError('Module is not installed')
        mod = importlib.import_module(imp)
        functions = get_functions(mod)
        for func in functions:
            doc = get_doc(mod, func)
            row = {"package": imp, "method": func, "doc": doc}
            docs = docs.append(row, ignore_index=True)

        cfunctions = get_class_functions(mod)
        for cfunc in cfunctions:
            c = cfunc[0]
            f = cfunc[1]
            mc = getattr(mod,c)
            doc = get_doc(mc, f)
            row = {"package": imp+"."+c, "method": f, "doc": doc}
            docs = docs.append(row, ignore_index=True)
    except ImportError as e:
        print(e)
    return docs
