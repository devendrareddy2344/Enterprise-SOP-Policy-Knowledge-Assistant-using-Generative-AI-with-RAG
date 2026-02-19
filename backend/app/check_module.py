import importlib, sys
spec = importlib.util.find_spec('langchain_community.vectorstores')
print('spec:', spec)
if spec:
    module = importlib.import_module('langchain_community.vectorstores')
    print('module attributes:', dir(module)[:20])
    print('FAISS attr:', hasattr(module, 'FAISS'))
else:
    print('module not found')
