# Local Live Blind-Evaluation Setup

This guide runs the existing Responses API blind evaluator locally. It does not upload candidate outputs to GitHub. Results are written under `reports/skill_blind_eval/`, which is git-ignored.

## Before starting

- Use only the public-literature prompts and registered public source metadata in this pilot. Do not include R21 telemetry, private traces or confidential data.
- Have an OpenAI API key available. Live Responses API usage is billed through API usage, not through this repository's CI. Check the API project budget before running.
- Choose a generator model and a judge model from **different model families**. Different model IDs alone do not establish independent judging.
- Record a truthful independence note. The runner checks that the note is present; it cannot authenticate the model family or prove independence.
- The blind judge is model-assisted. Human ADCS/EPS review remains mandatory for causal and component-localization disputes.

## Windows PowerShell

The helper prompts for model identifiers and family names, then reads the API key as a hidden SecureString. It asks for an explicit `RUN` confirmation after displaying the maximum call count.

Four-case smoke (12 API calls; 2 ADCS + 2 EPS):

```powershell
.\scripts\Run-SkillBlindEval.ps1 -Suite skill_holdout_cases.json -Limit 4
```

Full eight-case holdout (24 API calls):

```powershell
.\scripts\Run-SkillBlindEval.ps1 -Suite skill_holdout_cases.json -Limit 8
```

Thirteen-case development suite (39 API calls):

```powershell
.\scripts\Run-SkillBlindEval.ps1 -Suite skill_pressure_cases.json -Limit 13
```

The helper clears its process environment variables and frees the SecureString buffer in a `finally` block. The API key is not written to a command argument, source file or report. As with any process environment variable, it is available to the child Python process while the run is executing.

## Linux / macOS shell

Set the variables in the current shell session, then run the Python CLI. Avoid putting the API key directly in a shell command that will be stored in history.

```bash
export DGSI_GENERATOR_MODEL="..."
export DGSI_JUDGE_MODEL="..."
export DGSI_GENERATOR_FAMILY="..."
export DGSI_JUDGE_FAMILY="..."
export DGSI_JUDGE_INDEPENDENCE_NOTE="..."
read -rsp "OpenAI API key: " OPENAI_API_KEY
export OPENAI_API_KEY
echo
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 4
unset OPENAI_API_KEY DGSI_GENERATOR_MODEL DGSI_JUDGE_MODEL
unset DGSI_GENERATOR_FAMILY DGSI_JUDGE_FAMILY DGSI_JUDGE_INDEPENDENCE_NOTE
```

## Dry run

Both suites can be checked without credentials or network access:

```bash
python scripts/run_skill_blind_eval.py --suite skill_pressure_cases.json
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json
```

## Interpreting the result

- `COMPLETED` means every selected case completed the baseline, treatment and judge calls. It does not mean the Skill passed expert review.
- Inspect `by_domain.adcs` and `by_domain.eps`, each `per_case` row, judge critical failures and deterministic preflight findings.
- `candidate_without_critical_flags_rate` is a model-judge/preflight proxy, not human first-pass acceptance or final delivery success.
- If a holdout result is used to change a Skill, term catalog or rubric, retire that holdout from future generalization claims and freeze a replacement.
