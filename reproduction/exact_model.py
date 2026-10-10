"""Exact producer formulas; the geometric checker does not import this file."""
from fractions import Fraction as F
from math import factorial, prod

SEEDS = {
    "seed-eight": (8, [1, 2, 3, 4], 10),
    "seed-twelve": (12, [17, 24, 32, 41, 53, 69], 100),
}

FINITE_SEEDS = {
    "seed-nine": (9, [1, 2, 3, 5], 100),
    "seed-ten": (10, [16, 51, 91, 142, 217], 1000),
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def g(n):
    return F(n**n, factorial(n)) if n else F(1)

def simplex(n):
    return (n+1)*g(n)

def volume_factor(positive):
    a = list(map(F, positive)); m = len(a)
    require(m >= 1 and len(set(a)) == m and all(0 < x < 1 for x in a), "Invalid tilts")
    return sum((a[i]**(2*m-2) / ((1+a[i])*prod(a[i]**2-a[j]**2 for j in range(m) if i!=j)) for i in range(m)), F(0))

def state(n, positive):
    a=sorted(map(F,positive));m=len(a);z=n-2*m
    require(z>=0,"Too many tilt coordinates")
    I=volume_factor(a)
    S=1+sum(a)
    P=n+1+sum((z+2*j+1)*x for j,x in enumerate(a))
    return dict(dimension=n, I=I, R=g(n)*I*P, a=S/P, H=P/S, Q=I*S,
                horizontal_minor_sum=P, lifted_minor_sum=S)

def recursive_levels(seed, last):
    current=dict(seed)
    rows=[]
    for j in range(last+1):
        n,R,a=current['dimension'],current['R'],current['a']
        rows.append(dict(level=j,dimension=n,R=R,a=a))
        if j<last:
            factor=2*a*g(4*n+1)/g(2*n)**2
            current=dict(dimension=4*n+1,R=R**4*factor,a=a/2)
    return rows
