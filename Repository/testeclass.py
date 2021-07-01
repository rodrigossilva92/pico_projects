class Test():
    def __init__(self):
        print("constructing")


    def __del__(self):
        print("destructing")


tst = Test()