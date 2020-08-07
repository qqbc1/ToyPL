import sys

from main import run

def shell():
    while True:
        text = input("toypl > ")
        if text == 'exit':
            print('bye')
            break
        result, error = run('<stdin>', text)
        if error:
            print(error.as_string())
        elif result:
            print(result.elements[-1])

def exec_fn(fn_path):
    try:
        with open(fn_path, 'r') as f:
            script = f.read()
    except Exception as e:
        print(f'Faild to load script {fn_path}, error: {e}')
        raise

    result, error = run(fn_path, script)
    if error:
        print(error.as_string())
    elif result:
        print(result.elements[-1])

if len(sys.argv) > 1:
    fn_path = sys.argv[1]
    exec_fn(fn_path)
else:
    shell()
