"""Exact computer-assisted first-variation proof for all two-facet cuts in 8D.

This proves a local derivative assertion, not the global simplex inequality.
It reconstructs integer polynomials, never uses numerical optimization, and
checks every coefficient. Requires python-flint==0.9.0. The analytic race
recurrence and normalization are proved in minimality.tex.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import prod
from pathlib import Path
import argparse
import json
import flint
from flint import fmpz_mpoly_ctx, ctx as flint_context
from check_unrestricted import exponential_statistics

ROOT=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:
        raise ValueError(message)


def race_moments(a,c):
    """Independent rational recurrence for P(X>Y), E(X-Y)_+."""
    a=tuple(map(F,a));c=tuple(map(F,c))
    need(a and c and min(a+c)>0,'Race means must be positive')
    @lru_cache(None)
    def go(i,j):
        if i==len(a):return F(1),sum(c[j:],F(0))
        if j==len(c):return F(0),F(0)
        p,A=go(i+1,j);q,B=go(i,j+1)
        weight=c[j]/(a[i]+c[j])
        return weight*p+(1-weight)*q,weight*A+(1-weight)*B
    return go(0,0)


def construct(n,k):
    need(type(n) is int and type(k) is int and n>=2 and 1<=k<=n//2,
         'Invalid sign case')
    l=n-k
    context=fmpz_mpoly_ctx.get(tuple('x'+str(i) for i in range(n)))
    x=context.gens();one=context.constant(1);zero=context.constant(0)
    a=[sum(x[:i+1],zero) for i in range(k)]
    c=[sum(x[k:k+j+1],zero) for j in range(l)]
    @lru_cache(None)
    def go(i,j):
        if i==k:return one,sum(c[j:],zero)
        if j==l:return zero,zero
        P,A=go(i+1,j);Q,B=go(i,j+1)
        top=c[j]*prod((a[i]+c[v] for v in range(j+1,l)),start=one)
        left=a[i]*prod((a[u]+c[j] for u in range(i+1,k)),start=one)
        return top*P+left*Q,top*A+left*B
    P,A=go(0,0)
    D=prod((u+v for u in a for v in c),start=one)
    B=sum(c,zero)-sum(a,zero)
    dispersion=sum(((l+2*i-k-1)*u for i,u in enumerate(a,1)),zero)+sum(
                   ((k+2*j-l-1)*v for j,v in enumerate(c,1)),zero)
    full=(n+1)*D*(A-P*B)-P*(D-P)*dispersion
    removed_factor=one
    if k==1:
        N=(n+1)*sum(c,zero)*D-(D-a[0]**l)*dispersion
        removed_factor=a[0]**l
        need(full==removed_factor*N,'One-negative factor cancellation failed')
    else:
        N=full
    return dict(context=context,polynomial=N,denominator=D,probability_numerator=P,
                moment_numerator=A,mean=B,dispersion=dispersion,removed_factor=removed_factor)


def coefficient_obligation(polynomial):
    coefficients=polynomial.coeffs()
    need(coefficients and min(coefficients)>0,'A polynomial coefficient is not positive')
    return dict(nonzero_coefficients=len(coefficients),degree=int(polynomial.total_degree()),
                minimum_coefficient=str(min(coefficients)),negative_coefficients=0)


def controls():
    rows=[]
    for k in range(1,5):
        for scale in (1,3,7):
            a=[F(scale*(i+1)+i*i) for i in range(k)]
            c=[F(scale*(j+2)+j*j+F(1,2)) for j in range(8-k)]
            p,A=race_moments(a,c)
            b=[-u for u in a]+c
            residue=exponential_statistics(b)
            need(p==residue['p'] and A==(residue['mean_abs']+sum(b))/2,
                 'Race recurrence disagrees with independent residue formula')
            need(residue['simplex_ratio_derivative']<0,'Uncentred rational control failed')
            rows.append(dict(negative_coefficients=k,scale=scale,
                             positive_probability=str(p),positive_part_mean=str(A),
                             derivative=str(residue['simplex_ratio_derivative'])))
    b=[-5,-3,-2,-1,1,2,3,5]
    values=exponential_statistics(b)
    nine_derivative=-values['mean_abs']+(values['D']+sum(map(abs,b)))/20
    need(nine_derivative==F(2509,20160)>0,'Dimension-nine positive control failed')
    return dict(independent_race_residue_comparisons=rows,
                dimension_nine_zero_padded_derivative=str(nine_derivative))


def check(sign_cases=(1,2,3,4),progress=False):
    need(flint.__version__=='0.9.0','Use the pinned python-flint version')
    flint_context.threads=4
    rows=[]
    for k in sign_cases:
        built=construct(8,k)
        obligation=coefficient_obligation(built['polynomial'])
        # At a_i=A>0, c_j=C>0, gaps other than x_0,x_k vanish.
        # Positivity plus a nonzero specialization proves strictness even
        # when coefficients within either sign class repeat.
        specialization=built['polynomial'](*[int(i in (0,k)) for i in range(8)])
        need(specialization>0,'Repeated-level specialization vanished')
        row=dict(negative_coordinates=k,positive_coordinates=8-k,**obligation,
                 positive_factor_removed='a_1^7' if k==1 else '1',
                 repeated_level_value_at_one=str(specialization))
        rows.append(row)
        if progress:print('Checked sign case '+str(k)+': '+str(obligation['nonzero_coefficients'])+
                          ' positive coefficients',flush=True)
        del built
    return dict(status='PASS: exact computer-assisted local first-variation proof',
                all_two_facet_first_variations_nonpositive=list(sign_cases)==[1,2,3,4],
                strict_case='Both signs present and all eight coefficients nonzero; repeated values allowed',
                zero_coefficients='Nonpositive derivative by continuity',
                same_sign_case='An affine simplex with constant ratio one',
                global_minimality_proved=False,unrestricted_dimension_eight_bound_proved=False,
                arithmetic='Exact integer multivariate polynomial coefficients; no floating point',
                software=dict(python_flint=flint.__version__,source='https://python-flint.readthedocs.io/en/latest/fmpz_mpoly.html'),
                sign_cases=rows,total_coefficients=sum(r['nonzero_coefficients'] for r in rows),
                controls=controls(),
                limitation='A local derivative theorem does not control finite deformations or arbitrary bodies, and is not proof-assistant formalized.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--check-report',action='store_true')
    parser.add_argument('--sign-case',type=int,choices=[1,2,3,4])
    args=parser.parse_args()
    result=check((args.sign_case,) if args.sign_case else (1,2,3,4),progress=True)
    if args.check_report:
        need(result==json.loads((ROOT/'all-cuts-verification.json').read_text()),'Frozen report mismatch')
    encoded=json.dumps(result,indent=2)+'\n'
    if args.report:args.report.write_text(encoded,encoding='utf-8',newline='\n')
    print(encoded,end='')


if __name__=='__main__':main()
