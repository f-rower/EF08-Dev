import multiprocessing
#
# def spawn(num):
#     print('Spawned {}' .format(num))
#
# if __name__ == '__main__':
#     for i in range(55):
#         p=multiprocessing.Process(target = spawn, args=(i,))
#         p.start()

def spaaw():
    while 1:
        print(1)
def speew():
    while 1:
        print (2)


if __name__ == '__main__':
    p1 = multiprocessing.Process(spaaw())
    p2 = multiprocessing.Process(speew())
    p1.start()
    p2.start()