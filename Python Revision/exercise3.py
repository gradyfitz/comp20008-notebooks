
def fib(n):
    return n if n <= 1 else fib(n-1) + fib(n-2)

n = 10

nums = [fib(i) for i in range(n)][::-1] # or [fib(i) for i in range(n, -1, -1)]
print(nums)
