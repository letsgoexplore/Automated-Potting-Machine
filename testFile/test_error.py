from regex import A


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


a = 1
try:
    if a:
        raise MyError(2*2)
except MyError as e:
    print('My exception occurred, value:', e.value)
else:
    print(a)
finally:
    print('end')
