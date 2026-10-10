"""Exact arithmetic controls for the finite-zonotope local corollary.

The general proof is in zonotope-local-extension.txt and depends on the
published all-binary theorem. This checker accepts individual rational
hinge lists using only the standard library; it does not prove minimality.
"""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import argparse,json

ROOT=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def hinge_statistics(values):
    b=tuple(map(F,values));n=len(b)
    need(n>=2,'Dimension must be at least two')
    a=tuple(-v for v in b if v<0);c=tuple(v for v in b if v>0)
    @lru_cache(None)
    def race(i,j):
        if i==len(a):return F(1),sum(c[j:],F(0))
        if j==len(c):return F(0),F(0)
        p,A=race(i+1,j);q,B=race(i,j+1);weight=c[j]/(a[i]+c[j])
        return weight*p+(1-weight)*q,weight*A+(1-weight)*B
    if not c:p,positive=F(0),F(0)
    elif not a:p,positive=F(1),sum(c,F(0))
    else:p,positive=race(0,0)
    D=sum((abs(x-y) for x,y in combinations(b,2)),F(0))
    loss=positive-p*sum(b,F(0));gain=p*(1-p)*D/(n+1)
    return dict(probability=p,positive_mean=positive,dispersion=D,loss=loss,
                gain_upper_bound=gain,derivative_upper_bound=gain-loss)

def check_hinges(hinges):
    rows=[];upper=F(0)
    for b in hinges:
        need(len(b)==8,'The local corollary is for dimension eight')
        values=hinge_statistics(b)
        need(values['derivative_upper_bound']<=0,'Individual binary inequality failed')
        upper+=values['derivative_upper_bound']
        rows.append(dict(coefficients=list(map(str,b)),**{k:str(v) for k,v in values.items()}))
    return dict(status='PASS: exact arithmetic for individual hinge list',dimension=8,
        hinge_count=len(rows),hinges=rows,derivative_upper_bound=str(upper),
        proof_dependency='All-binary local theorem; see zonotope-local-extension.txt',
        unrestricted_minimality_proved=False)

def check():
    result=check_hinges([[-3,-2,-1,1,2,3,4,5],[2,-1,4,-3,1,-2,3,-4]])
    need(F(result['derivative_upper_bound'])==F(-770865251,1625702400),'Wrong exact hinge scaling')
    repeated=hinge_statistics([-1]*4+[1]*4)
    need(repeated['loss']==F(35,32) and repeated['derivative_upper_bound']==F(-59,288),
         'Repeated-coefficient control failed')
    zero=hinge_statistics([-1,1]+[0]*6)
    need(zero['derivative_upper_bound']==F(-1,9),'Zero-coefficient control failed')
    result['repeated_control']={k:str(v) for k,v in repeated.items()}
    result['zero_control']={k:str(v) for k,v in zero.items()}
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hinges',type=Path,help='JSON list of rational eight-coordinate hinge vectors')
    parser.add_argument('--report',type=Path)
    parser.add_argument('--check-report',action='store_true')
    args=parser.parse_args()
    need(not(args.hinges and args.check_report),'Frozen controls cannot be compared with another hinge list')
    result=check_hinges(json.loads(args.hinges.read_text())) if args.hinges else check()
    if args.check_report:
        need(result==json.loads((ROOT/'zonotope-local-verification.json').read_text()),'Frozen controls mismatch')
    output=json.dumps(result,indent=2)+'\n'
    if args.report:args.report.write_text(output,encoding='utf-8',newline='\n')
    print(output,end='')

if __name__=='__main__':main()
