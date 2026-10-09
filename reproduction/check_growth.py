"""Independent central-binomial recurrence, tail hypotheses and separation.

No producer/formula imports, numerical libraries, logarithms or float checks.
The geometric inputs are the independently regenerated seed geometry report.
"""
from copy import deepcopy
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import argparse, hashlib, json, sys

if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise ValueError(message)

def fraction(pair):return F(int(pair[0]),int(pair[1]))

def exponential_interval(x,terms=30):
    x=F(x);require(0<=x<terms+2,'Unsupported exponential argument')
    low=sum((x**k/F(factorial(k)) for k in range(terms+1)),F(0))
    first=x**(terms+1)/factorial(terms+1)
    return low,low+first/(1-x/F(terms+2))

def check_family(cert,geometry):
    require(cert['seed'] in geometry,'Missing geometric seed')
    seed=geometry[cert['seed']]
    d0=seed['dimension'];R0=fraction(seed['R']);a0=fraction(seed['a'])
    require(d0=={'seed-eight':8,'seed-twelve':12}[cert['seed']],'Wrong geometric seed dimension')
    require(R0>0 and a0>0,'Nonpositive geometric state')
    require(len(cert['levels'])==6,'Incomplete recurrence range')
    require(F(cert['tail_lower'])==3 and F(cert['tail_upper'])==7,'Wrong analytic tail constants')
    require(16*a0*a0*(6*d0+1)>9,'Lower all-level multiplier bound failed')
    require(121*a0*a0*(2*d0+F(2,3))<49,'Upper all-level multiplier bound failed')
    require(7*R0**3<3**(3*d0+1),'Strict growth hypothesis failed')
    n,R,a=d0,R0,a0;block=None
    for j,row in enumerate(cert['levels']):
        require(row['level']==j and row['dimension']==n,'Wrong recursive dimension')
        require(n==((3*d0+1)*4**j-1)//3,'Closed dimension formula failed')
        require(F(row['R'])==R and F(row['a'])==a,'Wrong exact recursive state')
        require(a==a0/2**j,'Lifted invariant recurrence failed')
        if j==2:block=R
        if j<5:
            q=2*n
            # Independent of the producer's factorial g-ratio.
            multiplier=2*a*F((2*q+1)**(2*q),q**(2*q)*comb(2*q,q))
            require(3<multiplier<7,'Computed multiplier outside analytic bounds')
            R,n,a=R**4*multiplier,4*n+1,a/2
    lo,hi=F(cert['limit_lower']),F(cert['limit_upper'])
    require(0<lo<hi,'Invalid claimed endpoints')
    exponent=3*n+1
    require(lo**exponent<3*R**3,'Lower asymptotic endpoint failed')
    require(7*R**3<hi**exponent,'Upper asymptotic endpoint failed')
    return dict(seed=cert['seed'],last_dimension=n,endpoint_exponent=exponent,
                limit_lower=str(lo),limit_upper=str(hi),strict_growth=True),block

def check_effective(cert,block):
    require(cert.get('seed')=='seed-twelve' and cert.get('level')==2 and cert.get('dimension')==197,'Wrong effective block')
    b=F(cert['block_root_lower']);c=F(cert['class_root_upper'])
    prefactor=F(cert['class_prefactor']);padding=F(cert['padding_constant']);start=cert['starting_dimension']
    require(b>c>0 and prefactor>0 and 0<padding<1,'Invalid comparison constants')
    require(type(start) is int and start>=197,'Effective recipe requires at least one block')
    require(block>b**197,'Claimed block root lower bound failed')
    # Independently build simplex values by consecutive ratios, rather than
    # the producer's factorial expression. Check every possible residue.
    simplex_values=[F(1),F(2)]
    for r in range(1,196):
        simplex_values.append(simplex_values[-1]*F(r+2,r+1)*F(r+1,r)**r)
    ratios=[value/b**r for r,value in enumerate(simplex_values)]
    require(len(ratios)==197 and all(x>padding for x in ratios),'Uniform residue padding bound failed')
    require((b/c)**start>prefactor*(start+1)/padding,'Effective starting dimension failed')
    require((b/c)*F(start+1,start+2)>1,'All-dimensional monotonic propagation failed')
    require(exponential_interval(F(1049,1000))[1]<c,'Prior class endpoint conversion failed')
    require(exponential_interval(F(49,1000))[1]<prefactor,'Finite class prefactor conversion failed')
    e_lo,e_hi=exponential_interval(1)
    require(e_lo>F(1359,500) and e_hi<F(11,4),'Elementary e bounds failed')
    return dict(starting_dimension=start,block_dimension=197,block_root_lower=str(b),
                class_root_upper=str(c),class_prefactor=str(prefactor),uniform_padding_lower=str(padding),
                residues_checked=len(ratios),worst_residue=min(range(197),key=ratios.__getitem__),
                comparison=f'R(E_n) > sup_{{K in C_n}} R(K) for every n>={start}',
                imported_upper_theorem='mxym mixed Bellman envelope; replayed separately')

def check(data,geometry):
    require(data.get('schema')=='symmetric-seed-recursive-growth-v1','Unknown certificate schema')
    require([x['seed'] for x in data['families']]==['seed-eight','seed-twelve'],'Wrong seed list')
    reports=[];block=None
    for cert in data['families']:
        report,current=check_family(cert,geometry);reports.append(report)
        if cert['seed']=='seed-twelve':block=current
    return dict(families=reports,effective_separation=check_effective(data['effective_separation'],block))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--report',type=Path,default=ROOT/'growth-verification.json')
    parser.add_argument('--geometry-report',type=Path,default=ROOT/'seed-geometry-verification.json')
    args=parser.parse_args()
    raw=(ROOT/'growth-certificate.json').read_bytes();data=json.loads(raw)
    geometry={r['name']:r for r in json.loads(args.geometry_report.read_text())}
    report=check(data,geometry)
    if args.self_test:
        mutations=[]
        bad=deepcopy(data);bad['families'][0]['levels'][1]['R']='1';mutations.append(bad)
        bad=deepcopy(data);bad['families'][1]['limit_lower']='3';bad['families'][1]['limit_upper']='4';mutations.append(bad)
        bad=deepcopy(data);bad['effective_separation']['padding_constant']='1/1000';mutations.append(bad)
        bad=deepcopy(data);bad['effective_separation']['starting_dimension']=1000;mutations.append(bad)
        for bad in mutations:
            try:check(bad,geometry)
            except (ValueError,KeyError,IndexError):continue
            raise ValueError('Corrupted certificate accepted')
        report['corrupted_certificates_rejected']=len(mutations)
    report.update(status='PASS',certificate_sha256=hashlib.sha256(raw).hexdigest(),
                  scope='Exact finite hypotheses and analytic endpoint arithmetic, not external peer review or formalization')
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
