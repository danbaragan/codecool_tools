# don't use with generators
def batcher(seq, batch_size=1):
    last = len(seq)
    for start in range(0, last, batch_size):
        yield seq[start:min(start+batch_size, last)]
