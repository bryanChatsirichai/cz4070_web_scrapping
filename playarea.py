arr  = ['abc','123','http']

info = ''
website = ''

for str in arr:
    if str[0:4] == 'http':
        website = str
    else:
        info = info + str + '\n'

print(website)
print(info)