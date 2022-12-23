string = input('Please input your cookie: ')
string = string.replace('"', '\'')
with open('cookie.txt', 'wt') as f:
    f.write(string)
print('Your cookie has been saved to cookie.txt')