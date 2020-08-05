from main import run

while True:
    text = input("basic > ")
    if text == 'exit':
        print('bye')
        break
    result, error = run('<stdin>', text)
    if error:
        print(error.as_string())
    elif result:
        print(result)