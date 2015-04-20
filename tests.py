from multiprocessing import Pool

def f((x, y)):
    print x+y
    return x*x

if __name__ == '__main__':
    pool = Pool(processes=2)                                # start 4 worker processes
    print pool.map(f, zip(range(10), range(10,20)))          # prints "[0, 1, 4,..., 81]"
    print pool.map(f, zip(range(10), 1))