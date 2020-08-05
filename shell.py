from main import run

while True:
    text = input("basic > ")
    if text == 'exit':
        print('bye')
        break
    # text = '100 * 3 + (6.0 - 2 * 1.2)'
    result, error = run('<stdin>', text)
    if error:
        print(error.as_string())
    else:
        print(result)