#!/usr/bin/env python3
"""Run DGSI offline: prepare new synthetic packets, or replay the GPT-reviewed demo."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from dgsi.skill_delivery import prepare, replay


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    demo=commands.add_parser('demo',help='Offline replay of recorded candidates and GPT reviews; no model call')
    demo.add_argument('--bundle',type=Path,default=ROOT/'evaluation/closeout_20261119')
    demo.add_argument('--output',type=Path,required=True)
    intake=commands.add_parser('prepare',help='Validate supplied L0/L1 and prepare answer-free generation requests')
    intake.add_argument('--collection',type=Path,required=True)
    intake.add_argument('--source-facts',type=Path,required=True)
    intake.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.output.exists() or args.output.is_symlink():
            raise FileExistsError
        report=(replay(args.bundle,args.output) if args.command=='demo'
                else prepare(args.collection,args.source_facts,args.output))
    except FileExistsError:
        code='OUTPUT_ALREADY_EXISTS'
    except FileNotFoundError:
        code='INPUT_FILE_NOT_FOUND'
    except Exception as exc:
        # Payload-free errors from strict validators. Do not echo user sources.
        code=str(exc) if str(exc).replace('_','').isalnum() and len(str(exc))<80 else 'INPUT_OR_REPLAY_INVALID'
    else:
        print(json.dumps(report,ensure_ascii=False))
        return 0
    print(json.dumps({'decision':'BLOCKED','error_code':code,'admitted_sft_records':0,'training_authorized':False}))
    return 2


if __name__=='__main__':
    raise SystemExit(main())
