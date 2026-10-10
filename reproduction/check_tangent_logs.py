"""Cross-check all 39 finite comparisons using rational logarithm intervals.

This review check uses the atanh series rather than the main checker's
exponential Taylor bounds. Run the main state/geometry checks first.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,json

ROOT=Path(__file__).resolve().parent
def need(ok,message):
    if not ok:raise ValueError(message)
def series(z,terms=50):
    low=2*sum((z**(2*j+1)/(2*j+1) for j in range(terms)),F(0))
    tail=2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return low,low+tail
def log_bounds(x):
    need(x>0,'Nonpositive logarithm');k=0
    while x>=2:x/=2;k+=1
    while x<1:x*=2;k-=1
    lo,hi=series((x-1)/(x+1));a,b=series(F(1,3))
    return (lo+k*a,hi+k*b) if k>=0 else (lo+k*b,hi+k*a)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'tangent-log-verification.json');args=parser.parse_args()
    recipe=json.loads((ROOT/'threshold-recipes.json').read_text())
    cert=json.loads((ROOT/'threshold-certificate.json').read_text())
    margins=[]
    for n in range(10,49):
        row=cert['nodes'][recipe['targets'][str(n)]]
        h=F(recipe['tangent_centres'][str(n)]);D=F(n+1);alpha=F(87,2000);delta=F(11,2000)
        derivative=1/h-2*alpha*h/D-4*delta*h**3/D**3
        exponent=alpha*(D-h*h/D)+delta*(D-h**4/D**3)+D*derivative**2/(4*alpha)
        lower,_=log_bounds(F(row['H'])*F(row['Q'])/h)
        margin=lower-exponent
        need(margin>F(1,4000),'Independent logarithmic comparison failed: '+str(n))
        margins.append((margin,n))
    report=dict(status='PASS',method='rational atanh logarithm intervals; no exponential-series import',
                dimensions=[10,48],comparisons=39,logarithmic_margin_lower='1/4000',
                smallest_margin_dimension=min(margins)[1],acceptance_uses_floating_point=False)
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
