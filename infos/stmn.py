# -*- coding: utf-8 -*-

# stmn: string manager (color, boldness...)

def s_red(s):
    return "\033[91m{}\033[0m".format(s)

def s_green(s):
    return "\033[92m{}\033[0m".format(s)

def s_blue(s):
    return "\033[94m{}\033[0m".format(s)

def s_yellow(s):
    return "\033[93m{}\033[0m".format(s)
    
def s_bold(s):
    return "\033[1m{}\033[0m".format(s)


if __name__ == '__main__':
    s1 = b'\xe2\x80\x98harsh, bitter\xe2\x80\x99'
    s2 = "\xe2\x80\x98harsh, bitter\xe2\x80\x99"
    b1 = bytes(s2, 'raw_unicode_escape')

    print(s1)
    print(s1.decode('utf-8'))

    print(b1)
    print(b1.decode('utf-8'))
    