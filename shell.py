import basic

while True:
    text = input("basic > ")
    if text == 'exit':
        print('bye')
        break
    # text = '1 + 3 * 2'
    result, error = basic.run('<stdin>', text)
    if error:
        print(error.as_string())
    else:
        print(result)