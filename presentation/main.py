d = {}

a = d[2]

for i in range(5):
    d[i] = i

print(a) #2 is expected

b = [1, 2, 3, 4, 5]
a = b
b[2] = 7
print(a[2]) #2 is expected