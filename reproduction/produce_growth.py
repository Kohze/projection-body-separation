"""Produce exact recurrence data; this is not the independent checker."""
import argparse, json
from pathlib import Path
import sys
from exact_model import SEEDS, F, recursive_levels, state

if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=ROOT)
    args=parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    certificates=[]
    for name,(n,positive,denominator) in SEEDS.items():
        rows=recursive_levels(state(n,[F(x,denominator) for x in positive]),5)
        encoded=[dict(level=r['level'],dimension=r['dimension'],R=str(r['R']),a=str(r['a'])) for r in rows]
        lo,hi=('28571/10000','28573/10000') if n==8 else ('2861/1000','28611/10000')
        certificates.append(dict(seed=name,levels=encoded,tail_lower='3',tail_upper='7',limit_lower=lo,limit_upper=hi))
        print(name,'last dimension',rows[-1]['dimension'],'certificate rows',len(rows),flush=True)
    data=dict(schema='symmetric-seed-recursive-growth-v1',families=certificates,
              effective_separation=dict(seed='seed-twelve',level=2,dimension=197,block_root_lower='28581/10000',
                class_root_upper='7137/2500',class_prefactor='1051/1000',padding_constant='1/3500',starting_dimension=15500,
                scope='Against point-generated products/joins and invertible affine equivalences; imports the prior mixed upper theorem.'))
    (args.output_directory/'growth-certificate.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':main()
