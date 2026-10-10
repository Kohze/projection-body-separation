"""Independent exact certificate for separation in every dimension n >= 9.

No producer, formula module, floating arithmetic or numerical optimizer imports.
Imported operation rules and the analytic Bellman envelope are stated in the
paper. Geometry inputs must come from the independent geometric checker.
"""
from fractions import Fraction as F
from math import comb,factorial
from pathlib import Path
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parent
ALPHA=F(87,2000);DELTA=F(11,2000)
def need(ok,message):
    if not ok:raise ValueError(message)
def pair(value):return F(int(value[0]),int(value[1]))
def exp_bounds(x,terms=50):
    x=F(x);need(0<=x<terms+2,'Unsupported exponential argument')
    term=F(1);low=term
    for k in range(1,terms+1):term*=x/k;low+=term
    first=term*x/(terms+1)
    return low,low+first/(1-x/(terms+2))
def g_values(last):
    values=[F(1),F(1)]
    for n in range(1,last):values.append(values[-1]*F(n+1,n)**n)
    return values
def operation(tag,r,s,left,right,G):
    h,q=left;j,v=right
    if tag=='join':return h+j,q*v
    need(tag=='product' and r>0 and s>0,'Invalid operation')
    n=r+s
    return F(n)*h*j/(r*j+s*h),q*v*G[r]*G[s]/G[n]*(s*h+r*j)/n

def exact_small_class(G):
    """Replay all point-generated states through dimension nine, with dominance.

    Both operation outputs increase in both H,Q coordinates at fixed input
    dimensions. Dropping coordinatewise dominated states is therefore complete.
    This is the previously published Pareto algorithm, not a new classification.
    """
    frontiers=[[(F(1),F(1))]];count=0
    for n in range(1,10):
        by_h={}
        for tag in ('join','product'):
            for r in range(n):
                s=n-r-(tag=='join')
                if r>s or s>=n or (tag=='product' and r==0):continue
                for left in frontiers[r]:
                    for right in frontiers[s]:
                        h,q=operation(tag,r,s,left,right,G);count+=1
                        by_h[h]=max(q,by_h.get(h,F(0)))
        frontier=[];best=F(0)
        for h,q in sorted(by_h.items(),reverse=True):
            if q>best:frontier.append((h,q));best=q
        need(frontier,'Empty finite class frontier');frontiers.append(frontier)
    need(max(h*q for h,q in frontiers[9])==10,'Dimension-nine class maximum is not the simplex')
    return dict(max_dimension=9,candidates_replayed=count,retained_states=sum(map(len,frontiers)),
                sharp_R_over_simplex='1',attribution='mxym exact Pareto finite-optima algorithm, 8 October 2026')

def tangent_upper(n,h):
    """f''(H) <= -2 alpha/D implies f(H) <= f(h)+D f'(h)^2/(4 alpha)."""
    D=F(n+1);need(0<h<=D,'Invalid tangent centre')
    exponent=ALPHA*(D-h*h/D)+DELTA*(D-h**4/D**3)
    slope=1/h-2*ALPHA*h/D-4*DELTA*h**3/D**3
    exponent+=D*slope*slope/(4*ALPHA)
    return h*exp_bounds(exponent)[1]

def check(recipe,cert,geometry,recipe_digest):
    need(recipe.get('schema')=='finite-separation-recipes-v1' and cert.get('schema')=='finite-separation-certificate-v1','Unknown schema')
    need(cert['recipe_sha256']==recipe_digest,'Recipe digest mismatch')
    need((recipe['first_dimension'],recipe['uniform_base_dimension'],recipe['period'])==(9,49,197),'Wrong all-dimensional coverage')
    C=F(recipe['uniform_prefactor']);c=F(recipe['class_root_upper'])
    need(C==F(9,10) and c==F(7137,2500),'Unexpected comparison constants')
    G=g_values(245)
    need(len(recipe['nodes'])==len(cert['nodes']) and recipe['nodes'],'Incomplete witness graph')
    states=[];dimensions=[];seed_names=set()
    for index,(row,claimed) in enumerate(zip(recipe['nodes'],cert['nodes'])):
        op=row['op'];tag=op[0]
        if tag=='point':need(op==['point'],'Malformed point');n=0;h=q=F(1)
        elif tag=='seed':
            need(len(op)==2 and op[1] in ('seed-nine','seed-ten','seed-twelve'),'Unsupported seed')
            seed=geometry[op[1]];n=seed['dimension'];h=1/pair(seed['a']);q=pair(seed['Q']);seed_names.add(op[1])
        else:
            need(len(op)==3 and tag in ('join','product'),'Malformed operation')
            i,j=op[1:];need(type(i) is int and type(j) is int and 0<=i<index and 0<=j<index,'Non-topological pointer')
            r,s=dimensions[i],dimensions[j];n=r+s+(tag=='join')
            need(n<=245,'Witness exceeds certified range')
            h,q=operation(tag,r,s,states[i],states[j],G)
        need(type(row['dimension']) is int and row['dimension']==n==claimed['dimension'],'Wrong witness dimension')
        need(F(claimed['H'])==h and F(claimed['Q'])==q and h>0 and q>0,'False exact witness state')
        dimensions.append(n);states.append((h,q))
    need(seed_names=={'seed-nine','seed-ten','seed-twelve'},'Incomplete seed list')
    need(set(recipe['targets'])=={str(n) for n in range(9,246)},'Missing dimension/residue witness')
    need(set(recipe['tangent_centres'])=={str(n) for n in range(10,49)},'Missing finite upper tangent')
    small=exact_small_class(G);finite_margins=[];base_margins=[]
    for n in range(9,246):
        index=recipe['targets'][str(n)]
        need(type(index) is int and 0<=index<len(states) and dimensions[index]==n,'Wrong target pointer')
        h,q=states[index];T=h*q
        if n==9:
            need(T>10*F(4001,4000),'Dimension-nine witness fails sharp comparison')
            nine_ratio=T/10
        elif n<49:
            bound=tangent_upper(n,F(recipe['tangent_centres'][str(n)]))
            need(T>F(4001,4000)*bound,'Finite Bellman comparison failed: '+str(n))
            finite_margins.append(T/bound)
        else:
            need(G[n]*T>F(1001,1000)*C*c**n,'Uniform residue witness failed: '+str(n))
            base_margins.append(G[n]*T/(C*c**n))
    # The analytic proof shows (n+1) g(n)^2 exp(-2n) strictly decreases.
    # Dropping the quartic envelope term bounds H^2 exp(-2 alpha H^2/D)
    # by D/(2 alpha e). This one finite check proves R_C(n)<C*c^n for n>=49.
    elo=exp_bounds(1)[0];shiftlo=exp_bounds(F(451,500))[0]
    need(C*C*elo**98*shiftlo>F(1000,87)*50*G[49]**2,'Uniform class prefactor failed')
    need(exp_bounds(F(1049,1000))[1]<c,'Class exponential conversion failed')
    seed=geometry['seed-twelve'];n=12;R=pair(seed['R']);a=pair(seed['a'])
    for _ in range(2):
        q=2*n;R=R**4*2*a*F((2*q+1)**(2*q),q**(2*q)*comb(2*q,q));a/=2;n=4*n+1
    need(n==cert['block_dimension']==197 and R==F(cert['block_R']),'Wrong repeating block state')
    need(R>F(5,4)*c**197,'Block fails strict propagation gain')
    return dict(status='PASS',starting_dimension=9,finite_dimensions_checked=40,
                finite_class_nine=small,dimension_nine_R_over_class_maximum=str(nine_ratio),
                finite_Bellman_dimensions=[10,48],finite_Bellman_margin_lower='4001/4000',
                uniform_class_bound='(9/10)*(7137/2500)^n for every n>=49',
                residue_dimensions=[49,245],residues_checked=197,residue_margin_lower='1001/1000',
                repeating_block_dimension=197,repeating_block_gain_lower='5/4',
                witness_nodes=len(states),seeds=sorted(seed_names),
                conclusion='R(E_n) > sup_{K in C_n} R(K) for every integer n>=9',
                scope='Imports the analytic mixed Bellman theorem and operation identities; not global optimality or external peer review')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-report',type=Path,default=ROOT/'seed-geometry-verification.json')
    parser.add_argument('--report',type=Path,default=ROOT/'threshold-verification.json');args=parser.parse_args()
    raw=(ROOT/'threshold-recipes.json').read_bytes();cert_raw=(ROOT/'threshold-certificate.json').read_bytes()
    geometry={r['name']:r for r in json.loads(args.geometry_report.read_text())}
    report=check(json.loads(raw),json.loads(cert_raw),geometry,hashlib.sha256(raw).hexdigest())
    report['certificate_sha256']=hashlib.sha256(cert_raw).hexdigest()
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
