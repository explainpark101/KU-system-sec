from watchfiles import watch

for changes in watch('.'):
    status, path = list(changes)[0]
    print(status == 2)