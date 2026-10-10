"""Recompute exact witness states from the frozen, explicit operation recipes."""
import argparse,hashlib,json
from pathlib import Path
from exact_model import SEEDS,FINITE_SEEDS,F,g,state,recursive_levels

ROOT=Path(__file__).resolve().parent
def produce():
    raw=(ROOT/'threshold-recipes.json').read_bytes();recipe=json.loads(raw)
    states=[];encoded=[]
    for row in recipe['nodes']:
        op=row['op'];tag=op[0]
        if tag=='point':d,R,a=0,F(1),F(1)
        elif tag=='seed':
            d,u,den=(SEEDS|FINITE_SEEDS)[op[1]]
            seed=state(d,[F(x,den) for x in u]);R,a=seed['R'],seed['a']
        else:
            r,R1,a1=states[op[1]];s,R2,a2=states[op[2]]
            if tag=='product':d=r+s;R=R1*R2;a=(r*a1+s*a2)/d
            elif tag=='join':d=r+s+1;R=g(d)/g(r)/g(s)*R1*R2*(a1+a2);a=a1*a2/(a1+a2)
            else:raise ValueError('Unknown operation')
        if d!=row['dimension']:raise ValueError('Recipe dimension mismatch')
        states.append((d,R,a));encoded.append(dict(dimension=d,H=str(1/a),Q=str(a*R/g(d))))
    d,u,den=SEEDS['seed-twelve']
    block=recursive_levels(state(d,[F(x,den) for x in u]),2)[2]
    return dict(schema='finite-separation-certificate-v1',recipe_sha256=hashlib.sha256(raw).hexdigest(),
                nodes=encoded,block_dimension=block['dimension'],block_R=str(block['R']))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=ROOT);args=parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    data=produce()
    (args.output_directory/'threshold-certificate.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Produced exact finite-separation states:',len(data['nodes']),flush=True)
if __name__=='__main__':main()
