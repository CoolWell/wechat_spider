# -*- coding: utf-8 -*-
__author__ = 'Passion'
f = open(r'C:\Users\Passion\Desktop\8.txt')
w = open(r'C:\Users\Passion\Desktop\88.txt', 'w')
num=1
line = f.readline()
while (len(line) != 0):
    print(line)
    if(num%2 ==0):
        w.write(line)
    num=num+1
    line = f.readline()
f.close()
w.close()