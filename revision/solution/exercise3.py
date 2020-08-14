n=10
fib=[0,1]
for i in range(n-2) :
    fib.append(fib[i]+fib[i+1])
fib.reverse()
print(fib)