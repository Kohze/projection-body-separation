"""Exact all-offset hyperplane bound for the one/two-negative family in 8D.

Reconstructs all 46 ordered-cone polynomials and verifies rational AM-GM
certificates. No numerical optimizer is imported. This does not prove the
full ten-facet bound or global minimality. See README.txt for the analysis.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
from math import prod
from pathlib import Path
import argparse,hashlib,json
import flint
from flint import fmpz_mpoly_ctx,ctx

ROOT=Path(__file__).resolve().parent

def construct(m,k,pattern=None):
    l=m-k;cxt=fmpz_mpoly_ctx.get(tuple('x'+str(i) for i in range(m)))
    x=cxt.gens();zero=cxt.constant(0);one=cxt.constant(1)
    if pattern:
        if len(pattern)!=m or pattern.count('A')!=k or pattern.count('C')!=l:raise ValueError('Invalid ordering')
        levels=[sum(x[:i+1],zero) for i in range(m)]
        a=[level for level,side in zip(levels,pattern) if side=='A']
        c=[level for level,side in zip(levels,pattern) if side=='C']
    else:
        a=[sum(x[:i+1],zero) for i in range(k)]
        c=[sum(x[k:k+j+1],zero) for j in range(l)]
    @lru_cache(None)
    def go(i,j):
        if i==k-1 and j==l-1:return one
        first=c[j]*prod((a[i]+c[v] for v in range(j+1,l)),start=one)
        second=a[i]*prod((a[u]+c[j] for u in range(i+1,k)),start=one)
        top=go(i+1,j) if i+1<k else zero
        right=go(i,j+1) if j+1<l else zero
        return first*top+second*right
    H=go(0,0);go.cache_clear()
    L=prod((u+v for u in a for v in c),start=one)
    D=sum(((l+2*i-k-1)*u for i,u in enumerate(a,1)),zero)+sum(
          ((k+2*j-l-1)*v for j,v in enumerate(c,1)),zero)
    return (m-1)*L-D*H

def verify(p,certificate):
    """Independently expand each three-term square in sparse rational arithmetic."""
    coefficients=p.coeffs()
    negative=[tuple(map(int,p.monomial(i))) for i,v in enumerate(coefficients) if v<0]
    changes={}
    for item in certificate:
        if item.get('type')=='circuit':
            center=tuple(item['center']);lower=tuple(item['lower']);upper=tuple(item['upper'])
            demand=F(item['demand']);A=F(item['lower_coefficient']);B=F(item['upper_coefficient']);t=item['upper_distance']
            if any(len(e)!=10 or any(type(v) is not int or v<0 for v in e) for e in (center,lower,upper)):
                raise ValueError('Invalid circuit exponent')
            if type(t) is not int or not 1<=t<=100 or min(demand,A,B)<=0:
                raise ValueError('Invalid circuit coefficient')
            if any(t*lower[i]+upper[i]!=(t+1)*center[i] for i in range(10)):
                raise ValueError('Circuit exponent balance failed')
            if (A*F(t+1,t))**t*(B*(t+1))<demand**(t+1):
                raise ValueError('Circuit AM-GM coefficient bound failed')
            for e,v in [(center,demand),(lower,-A),(upper,-B)]:changes[e]=changes.get(e,F(0))+v
            continue
        if item.get('type')=='amgm':
            center=tuple(item['center']);demand=F(item['demand'])
            terms=[(tuple(r['monomial']),F(r['weight'])) for r in item['terms']]
            if len(center)!=10 or any(type(v) is not int or v<0 for v in center) or demand<=0:
                raise ValueError('Invalid AM-GM center')
            if not terms or any(len(e)!=10 or any(type(v) is not int or v<0 for v in e) or w<=0 for e,w in terms):
                raise ValueError('Invalid AM-GM term')
            if sum((w for e,w in terms),F(0))!=1 or any(
                sum((w*e[i] for e,w in terms),F(0))!=center[i] for i in range(10)):
                raise ValueError('AM-GM exponent balance failed')
            changes[center]=changes.get(center,F(0))+demand
            for e,w in terms:changes[e]=changes.get(e,F(0))-demand*w
            continue
        weight=F(item['weight']);ratio=F(item['ratio']);power=item['power']
        base=tuple(item['monomial']);i,j=item['variables']
        if weight<=0 or ratio<=0 or type(power) is not int or power<=0:
            raise ValueError('Invalid square scale')
        if len(base)!=10 or any(type(v) is not int or v<0 for v in base):
            raise ValueError('Invalid monomial')
        if type(i) is not int or type(j) is not int or not 0<=i<j<10:
            raise ValueError('Invalid square variables')
        ep=list(base);em=list(base);center=list(base)
        ep[i]+=2*power;em[j]+=2*power;center[i]+=power;center[j]+=power
        for exponent,coefficient in [(ep,-weight*ratio*ratio),(em,-weight),(center,2*weight*ratio)]:
            key=tuple(exponent);changes[key]=changes.get(key,F(0))+coefficient
    residual={e:F(2*int(p[e]))+changes.get(e,F(0)) for e in set(negative)|changes.keys()}
    if any(v<0 for v in residual.values()):raise ValueError('Square certificate leaves a negative coefficient')
    return dict(blocks=len(certificate),amgm_blocks=sum(r.get('type')=='amgm' for r in certificate),
                circuit_blocks=sum(r.get('type')=='circuit' for r in certificate),modified_coefficients=len(changes),
                minimum_modified_residual=str(min(residual.values(),default=F(0))))

def cases():
    result=[(1,None)]
    for positions in combinations(range(10),2):
        result.append((2,''.join('A' if i in positions else 'C' for i in range(10))))
    if len(result)!=46 or len(set(result))!=46:raise ValueError('Incomplete cone list')
    return result


def density(a,c):
    """Independent closed density from one/two negative exponential phases."""
    a=tuple(map(F,a));c=tuple(map(F,c))
    if not a or not c or min(a+c)<=0 or len(a)>2:raise ValueError('Invalid density input')
    if len(a)==1:return prod((a[0]/(a[0]+v) for v in c),start=F(1))/a[0]
    def h(u):return prod((u/(u+v) for v in c),start=F(1))
    if a[0]==a[1]:return h(a[0])/a[0]*sum((v/(a[0]+v) for v in c),F(0))
    return (h(a[1])-h(a[0]))/(a[1]-a[0])


def run(verbose=False):
    if flint.__version__!='0.9.0':raise ValueError('Use pinned python-flint==0.9.0')
    source=ROOT/'low-sign-hyperplane-certificates.json'
    archive=json.loads(source.read_text())
    if archive['ambient_coordinates']!=10 or archive['dimension']!=8:
        raise ValueError('Certificate archive has the wrong dimension')
    supplied=archive['cases'];rows=[];used=set()
    for k,word in cases():
        p=construct(10,k,word);co=p.coeffs();minimum=int(min(co));proof=None
        if minimum<0:
            if word not in supplied:raise ValueError('Missing certificate for '+str(word))
            proof=verify(p,supplied[word]);used.add(word)
        a=[i+1 for i,v in enumerate(word) if v=='A'] if word else [1]
        c=[i+1 for i,v in enumerate(word) if v=='C'] if word else list(range(1,10))
        b=[-v for v in a]+c
        D=sum(abs(u-v) for i,u in enumerate(b) for v in b[i+1:])
        L=prod(u+v for u in a for v in c)
        actual=int(p(*([1]*10)));expected=L*(9-D*density(a,c))
        if expected!=actual:raise ValueError('Independent partial-fraction control failed')
        rows.append(dict(negative_coordinates=k,absolute_ordering=word,
            nonzero_coefficients=len(co),minimum_coefficient=str(minimum),
            exact_certificate_blocks=0 if proof is None else proof['blocks'],
            independent_density_control=str(density(a,c)),polynomial_control=str(actual)))
        if verbose:print('PASS',len(rows),'of 46',word or 'one-negative case',flush=True)
        del p,co
    if used!=set(supplied):raise ValueError('Archive includes an unused or unknown certificate')
    return dict(status='PASS',ambient_coordinates=10,dimension=8,
        statement='D(b)*density(sum b_i Exp_i,0) <= 9 when either sign occurs at most twice',
        expected_cases=46,verified_cases=len(rows),
        polynomial_coefficients=sum(r['nonzero_coefficients'] for r in rows),
        exact_certificate_blocks=sum(r['exact_certificate_blocks'] for r in rows),
        python_flint=flint.__version__,certificate_data_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        full_ten_facet_bound_proved=False,unrestricted_minimality_proved=False,cases=rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-report',action='store_true')
    parser.add_argument('--report',type=Path)
    parser.add_argument('--verbose',action='store_true')
    args=parser.parse_args();result=run(args.verbose)
    if args.check_report and result!=json.loads((ROOT/'low-sign-hyperplane-verification.json').read_text()):
        raise ValueError('Delivered report differs from complete exact replay')
    if args.report:args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
