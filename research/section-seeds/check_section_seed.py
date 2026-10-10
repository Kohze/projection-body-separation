"""Certify an explicit rational section seed by outward exact arithmetic.

Classical multivariate interpolation and spline-volume identities are explained
in proof.txt. Optimizer outputs are not inputs or acceptance premises.
"""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as F
from math import comb,factorial
import argparse,hashlib,json,sys

if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent

def determinant(raw):
    A=[list(row) for row in raw];size=len(A);sign=1;previous=1
    if not size:return 1
    for k in range(size-1):
        if A[k][k]==0:
            for j in range(k+1,size):
                if A[j][k]:A[k],A[j]=A[j],A[k];sign=-sign;break
            else:return 0
        pivot=A[k][k]
        for i in range(k+1,size):
            for j in range(k+1,size):
                numerator=A[i][j]*pivot-A[i][k]*A[k][j]
                value,remainder=divmod(numerator,previous)
                if remainder:raise ValueError('Non-exact Bareiss division')
                A[i][j]=value
            A[i][k]=0
        previous=pivot
    return sign*A[-1][-1]

def fixed_product(values,denominator,upper=False):
    value=denominator
    for factor in values:
        value=(value*factor+(denominator-1 if upper else 0))//denominator
    return value

def reconstruct(B,ray,lower,upper):
    m=len(B);r=len(B[0]);n=m-r-1
    basis=list(combinations(range(m),r));extended=list(combinations(range(m),r+1))
    db={J:determinant([B[i] for i in J]) for J in basis}
    if not all(db.values()):raise ValueError('Singular linear basis')
    da={J:determinant([[1]+B[i] for i in J]) for J in extended}
    if not all(da.values()):raise ValueError('Degenerate affine basis')
    interior_bases=[];facet_covered=set()
    for J,d in da.items():
        cofactors=[(-1)**j*db[tuple(i for i in J if i!=J[j])] for j in range(r+1)]
        if all(c*d>0 for c in cofactors):
            interior_bases.append(J);facet_covered.update(set(range(m))-set(J))
    if facet_covered!=set(range(m)):raise ValueError('Unverified genuine coordinate facets')
    # General-position hyperplane interpolation proves the finite transform
    # identity; no floating-point or sampled polynomial identity is used.
    Q=2**256;total=0;gradient=[0]*r;selected=0
    for J,d in db.items():
        Y=[B[i] for i in J]
        coordinates=[]
        for j in range(r):
            matrix=[row.copy() for row in Y];matrix[j]=list(ray)
            coordinates.append(determinant(matrix))
        if any(x==0 for x in coordinates):raise ValueError('Non-generic density ray')
        if any(x*d<0 for x in coordinates):continue
        theta=[]
        for j in range(r):
            matrix=[row.copy() for row in Y]
            for row in matrix:row[j]=1
            theta.append(determinant(matrix))
        denominator=abs(d)
        for k,b in enumerate(B):
            if k not in J:
                factor=d-sum(x*y for x,y in zip(theta,b))
                if not factor:raise ValueError('Zero interpolation denominator')
                denominator*=factor
        contribution=F(d**(m-r),denominator)
        total+=(contribution.numerator*Q)//contribution.denominator
        for j in range(r):
            term=-contribution*F(theta[j],d)
            gradient[j]+=(term.numerator*Q)//term.denominator
        selected+=1
    f_lo=F(total,Q);f_hi=F(total+selected,Q)
    if f_lo<=0:raise ValueError('No positive density enclosure')
    Qg=2**128;gamma=[]
    for b in B:
        low=total+sum(x*(gradient[j]+(selected if x<0 else 0)) for j,x in enumerate(b))
        high=total+selected+sum(x*(gradient[j]+(selected if x>0 else 0)) for j,x in enumerate(b))
        if low<=0:raise ValueError('Non-positive facet factor')
        lo=F(low,total+selected);hi=F(high,total)
        gamma.append(((lo.numerator*Qg)//lo.denominator,
                      -((-hi.numerator*Qg)//hi.denominator)))
    D=[0,0];E=[0,0]
    for collection,out in ((da,D),(db,E)):
        for J,d in collection.items():
            outside=[i for i in range(m) if i not in J]
            for side in range(2):
                out[side]+=abs(d)*fixed_product([gamma[i][side] for i in outside],Qg,side==1)
    a_lo=F(E[0],D[1]);a_hi=F(E[1],D[0]);g=F(n**n,factorial(n))
    R_lo=g*f_lo*F(D[0],Qg);R_hi=g*f_hi*F(D[1],Qg)
    # Coarsen only outwards for inexpensive subsequent integer power checks.
    aq=10**12;rq=10**9
    alo=F((a_lo.numerator*aq)//a_lo.denominator,aq)
    ahi=F(-((-a_hi.numerator*aq)//a_hi.denominator),aq)
    Rlo=F((R_lo.numerator*rq)//R_lo.denominator,rq)
    Rhi=F(-((-R_hi.numerator*rq)//R_hi.denominator),rq)
    need=[16*alo**2*(6*n+1)>9,121*ahi**2*(2*n+F(2,3))<64,
          8*Rhi**3<3**(3*n+1)]
    if not all(need):raise ValueError('Tail hypotheses not available: '+str(need))
    dimension=n;al=alo;ah=ahi
    for j in range(5):
        q=2*dimension;factor=2*F((2*q+1)**(2*q),q**(2*q)*comb(2*q,q))
        Rlo=Rlo**4*al*factor;Rhi=Rhi**4*ah*factor
        al/=2;ah/=2;dimension=4*dimension+1
    exponent=3*dimension+1
    if not lower**exponent<3*Rlo**3:raise ValueError('Lower growth endpoint failed')
    if not 8*Rhi**3<upper**exponent:raise ValueError('Upper growth endpoint failed')
    result=dict(status='PASS',
        dimension=n,rank=r,facets=m,ray=ray,selected_terms=selected,
        all_linear_bases=len(db),all_affine_bases=len(da),
        strictly_interior_simplex_bases=len(interior_bases),genuine_facets_verified=len(facet_covered),
        density_bounds=list(map(str,(f_lo,f_hi))),
        gradient_bounds=[[str(F(x,Q)),str(F(x+selected,Q))] for x in gradient],
        gamma_bounds=[[str(F(x,Qg)) for x in row] for row in gamma],
        a_bounds=list(map(str,(alo,ahi))),
        R_bounds=list(map(str,(F((R_lo.numerator*rq)//R_lo.denominator,rq),
                              F(-((-R_hi.numerator*rq)//R_hi.denominator),rq)))),
        amplified_lower=str(lower),amplified_upper=str(upper),last_dimension=dimension,
        endpoint_exponent=exponent,tail_lower=3,tail_upper=8,
        floating_point_acceptance=False,unrestricted_minimality_proved=False)
    return result


def need(ok,message):
    if not ok:raise ValueError(message)


def check(data):
    need(data.get('schema')=='rational-generic-simplex-section-v1','Unknown schema')
    B=data['columns']
    need(data['dimension']==18 and data['rank']==4 and len(B)==23,'Wrong dimensions')
    need(all(len(b)==4 and all(type(x) is int for x in b) for b in B),'Columns must be integer four-vectors')
    need(data['density_precision_bits']==256 and data['facet_precision_bits']==128,'Unexpected precision')
    need(data['last_level']==5,'Unexpected recurrence range')
    rays=data['rays'];need(len(rays)==2 and rays[0]!=rays[1],'Two distinct rays required')
    need(all(len(h)==4 and all(type(x) is int for x in h) for h in rays),'Invalid ray')
    lower,upper=F(data['limit_lower']),F(data['limit_upper'])
    need(F(366,125)<=lower<upper<=F(29283,10000),'Invalid or weakened endpoints')
    results=[reconstruct(B,h,lower,upper) for h in rays]
    for key in ('density_bounds','a_bounds','R_bounds'):
        bounds=[[F(x) for x in row[key]] for row in results]
        need(max(x[0] for x in bounds)<=min(x[1] for x in bounds),'Disjoint ray enclosures: '+key)
    for key in ('gradient_bounds','gamma_bounds'):
        for index in range(len(results[0][key])):
            bounds=[[F(x) for x in row[key][index]] for row in results]
            need(max(x[0] for x in bounds)<=min(x[1] for x in bounds),'Disjoint derivative or facet enclosures')
    for row in results:
        for key in ('a_bounds','R_bounds'):
            actual=list(map(F,row[key]));claimed=list(map(F,data[key]))
            need(len(claimed)==2 and claimed[0]<=actual[0]<=actual[1]<=claimed[1],'False seed-state bounds: '+key)
    return dict(status='PASS',dimension=18,rank=4,facets=23,
        density_precision_bits=256,facet_precision_bits=128,
        a_bounds=data['a_bounds'],R_bounds=data['R_bounds'],
        limit_lower=str(lower),limit_upper=str(upper),last_dimension=18773,
        endpoint_exponent=56320,tail_lower=3,tail_upper=8,
        rays=results,floating_point_used=False,unrestricted_minimality_proved=False,
        global_optimality_proved=False,
        analytic_argument='proof.txt; classical interpolation, coarea, weighted complementary minors and inherited product-join calculus')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-report',action='store_true')
    parser.add_argument('--report',type=Path,default=ROOT/'verification.json')
    args=parser.parse_args()
    raw=(ROOT/'seed.json').read_bytes();result=check(json.loads(raw))
    result['seed_sha256']=hashlib.sha256(raw).hexdigest()
    encoded=json.dumps(result,indent=2)+'\n'
    if args.check_report:need(args.report.read_text()==encoded,'Saved report differs from exact reconstruction')
    else:args.report.write_text(encoded,encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],dimension=18,facets=23,
        amplified_limit=[result['limit_lower'],result['limit_upper']],
        floating_point_used=False,unrestricted_minimality_proved=False)))


if __name__=='__main__':main()
