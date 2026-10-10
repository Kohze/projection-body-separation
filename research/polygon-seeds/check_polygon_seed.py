"""Reconstruct the rational polygon-section seed and its infinite growth bounds.

Standard library only; optimizer outputs are not inputs. The analytic argument
connecting the finite identities to geometry is in proof.txt and the paper.
"""
from fractions import Fraction as F
from itertools import combinations
from math import comb, factorial
from pathlib import Path
import argparse,hashlib,json,sys

if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def det(a,b):return a[0]*b[1]-a[1]*b[0]


def subtract(a,b):return tuple(x-y for x,y in zip(a,b))


def check(data):
    need(data.get('schema')=='rational-polygon-section-seed-v1','Unknown seed schema')
    n=data['dimension'];B=[tuple(map(F,b)) for b in data['columns']];m=len(B)
    need(n==15 and m==n+3 and all(len(b)==2 for b in B),'Wrong seed dimensions')
    base=[(F(10),F(0)),(F(7),F(4)),(F(4),F(7))];orbit=[]
    for j in range(6):
        for x,y in base:
            for _ in range(j):x,y=-y,x+y
            orbit.append((x,y))
    need(B==orbit,'Specified rational orbit changed')
    need(len(set(B))==m and set(B)=={(-x,-y) for x,y in B},'Antipodal symmetry failed')
    # After deleting any column, two independent antipodal pairs remain.
    for removed in range(m):
        remaining=set(B[:removed]+B[removed+1:])
        paired=[b for b in remaining if tuple(-x for x in b) in remaining]
        need(any(det(a,b)!=0 for a,b in combinations(paired,2)),'A coordinate facet lacks full dimension')
    triples=list(combinations(range(m),3));pairs=list(combinations(range(m),2))
    triangle={J:det(subtract(B[J[1]],B[J[0]]),subtract(B[J[2]],B[J[0]])) for J in triples}
    need(all(triangle.values()),'Affinely collinear triple')
    D=sum(map(abs,triangle.values()),F(0));E=sum((abs(det(B[i],B[j])) for i,j in pairs),F(0))
    terms=[];polynomial={};gradient=[F(0),F(0)]
    for i,j in pairs:
        determinant=det(B[i],B[j])
        if not determinant:continue
        theta=((B[j][1]-B[i][1])/determinant,(B[i][0]-B[j][0])/determinant)
        alpha=F(1)
        other=[k for k in range(m) if k not in (i,j)]
        for k in other:
            alpha/=1-sum(x*y for x,y in zip(theta,B[k]))
        terms.append((i,j,determinant,theta,alpha))
        partial={(0,0):alpha}
        for k in other:
            updated={}
            for (a,b),coefficient in partial.items():
                for exponent,factor in (((a,b),F(1)),((a+1,b),B[k][0]),((a,b+1),B[k][1])):
                    updated[exponent]=updated.get(exponent,F(0))+coefficient*factor
            partial=updated
        for exponent,coefficient in partial.items():
            polynomial[exponent]=polynomial.get(exponent,F(0))+coefficient
    need({e:c for e,c in polynomial.items() if c}=={(0,0):F(1)},'Cleared Laplace-transform identity failed')
    rays=[]
    for k in range(1,100):
        h=(F(1),F(k,17))
        if any(det(h,b)==0 for b in B):continue
        f=F(0);g=[F(0),F(0)];selected=0
        for i,j,determinant,theta,alpha in terms:
            if min(det(h,B[j])/determinant,det(B[i],h)/determinant)<=0:continue
            contribution=alpha/abs(determinant);f+=contribution;selected+=1
            for coordinate in range(2):g[coordinate]-=contribution*theta[coordinate]
        need(f>0 and g==[0,0],'Density positivity or symmetry derivative failed')
        rays.append(dict(ray=list(map(str,h)),density=str(f),selected_terms=selected))
        if len(rays)==3:break
    need(len(rays)==3 and len({row['density'] for row in rays})==1,'Generic-ray cross-check failed')
    f=F(rays[0]['density']);a=E/D;R=F(n**n,factorial(n))*D*f
    for key,value in dict(D=D,E=E,density=f,a=a,R=R).items():
        need(F(data[key])==value,'Claimed seed state changed: '+key)
    d0=n;R0=R;a0=a
    need(16*a*a*(6*n+1)>9,'Analytic lower-tail hypothesis failed')
    need(121*a*a*(2*n+F(2,3))<49,'Analytic upper-tail hypothesis failed')
    need(7*R**3<3**(3*n+1),'Strict root growth hypothesis failed')
    need(data['last_level']==5,'Unexpected recurrence range')
    levels=[]
    for j in range(6):
        need(n==((3*d0+1)*4**j-1)//3 and a==a0/2**j,'Closed state recurrence failed')
        levels.append(dict(level=j,dimension=n,a=str(a)))
        if j<5:
            q=2*n
            multiplier=2*a*F((2*q+1)**(2*q),q**(2*q)*comb(2*q,q))
            need(3<multiplier<7,'Exact multiplier violates analytic tail bounds')
            R,n,a=R**4*multiplier,4*n+1,a/2
    lower,upper=F(data['limit_lower']),F(data['limit_upper'])
    need(F(289,100)<=lower<upper<=F(14451,5000),'Weakened or invalid claimed endpoints')
    exponent=3*n+1
    need(lower**exponent<3*R**3,'Lower root endpoint failed')
    need(7*R**3<upper**exponent,'Upper root endpoint failed')
    return dict(status='PASS',dimension=d0,facets=m,D=str(D),E=str(E),density=str(f),
        R=str(R0),a=str(a0),R_over_g=str(D*f),
        independent_pair_terms=len(terms),cleared_polynomial_coefficients=len(polynomial),
        density_ray_checks=rays,levels=levels,last_dimension=n,endpoint_exponent=exponent,
        limit_lower=str(lower),limit_upper=str(upper),strict_root_growth=True,
        analytic_argument='proof.txt; geometric identities and the inherited product-join calculus',
        floating_point_used=False,unrestricted_minimality_proved=False,global_optimality_proved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-report',action='store_true')
    parser.add_argument('--report',type=Path,default=ROOT/'verification.json')
    args=parser.parse_args()
    raw=(ROOT/'seed.json').read_bytes();result=check(json.loads(raw))
    result['seed_sha256']=hashlib.sha256(raw).hexdigest()
    encoded=json.dumps(result,indent=2)+'\n'
    if args.check_report:
        need(args.report.read_text()==encoded,'Saved report differs from reconstructed mathematics')
    else:args.report.write_text(encoded,encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],dimension=result['dimension'],
          facets=result['facets'],limit=(result['limit_lower'],result['limit_upper']),
          last_dimension=result['last_dimension'],floating_point_used=False)))


if __name__=='__main__':main()
