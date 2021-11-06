import hashlib


def md5(input):
    input = str(input)
    md5 = hashlib.md5()
    md5.update(input.encode('utf-8'))
    hash = md5.hexdigest()[8:-8]
    return hash
