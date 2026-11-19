"""Bounded authoring recipes; selection scores are GPT declarations, not evidence.

This module never calls a model or reads test outcomes. A host AI proposes and
scores instructions before answering; the resolver checks binding and selection.
Semantic fidelity still requires independent review of the resulting candidate.
"""
from .skill_delivery import DeliveryError, digest

CRITERIA = ('task_alignment', 'clarity', 'input_answerability',
            'evidence_roles', 'scope_retention')
RECIPES = ('baseline', 'evolve', 'select', 'evolve-select')
OPERATIONS = ('comparability', 'evidence_roles', 'bounded_scope')

DGSI_POLICY = (
    '依据当前可见日志分析现象，解释上游ML候选和未校准分数；分别表达故障源与受影响部件。'
    '证据引用必须逐项标注角色：直接观测、ML推断、独立观测/反证、未附原件的上游引用。'
    'ML推断与独立观测必须作为不同证据项分别列出，禁止合并成同一支持证据项或重复计票；'
    '独立观测可以单独用于 corroborate/contradict ML推断，但不得改写为ML输出本身。'
    '保留飞行/地面/AIT适用范围；比较前说明可见的时间、构型、模式和路径可比性。'
    '涉及发射/注入过程时，必须核对是否为同一发射路径，以及该观测窗口内是否发生路径切换；'
    '只有输入明确记录路径标识和窗口内无切换时，才能写作“同一发射路径、窗口内未切换”。'
    '路径标识、切换事件或窗口边界任一缺失时，明确标为未知/未记录，不得推断为未切换。'
    '其他没有记录的条件同样标为缺失，不能默认成立。历史先检查as-of、状态和硬件适用性，'
    '缺可信时间的历史拒绝迁移。处置只写可见材料支持的执行/计划/原文建议；'
    '未记录则NOT_RECORDED和[]；新建议放follow_up_actions。保持来源允许的不确定性。'
)


def authoring_recipe(recipe_id: str) -> dict:
    """Return a separate host-authoring policy, never a model-facing SFT message."""
    if recipe_id not in RECIPES or recipe_id == 'baseline':
        raise DeliveryError('INSTRUCTION_RECIPE_UNKNOWN')
    evolve = recipe_id in ('evolve', 'evolve-select')
    select = recipe_id in ('select', 'evolve-select')
    return {
        'recipe_id': recipe_id, 'recipe_version': '1', 'not_for_sft': True,
        'candidate_count': 3 if select else 1,
        'evolution_enabled': evolve, 'selection_enabled': select,
        'domain_policy': DGSI_POLICY,
        'procedure': (
            '先读取冻结user输入，只改写任务指令，禁止更改task_type或任何输入事实。'
            + ('从comparability、evidence_roles、bounded_scope中选择演化操作，'
               '提高证据判别或约束明确程度，不增加新事实。' if evolve else
               '以不同表述风格提出指令，不追加新的任务要求。')
            + ('生成恰好三个不同指令，每条先独立给五项0-2分；'
               '事实/范围检查不通过或任一项0分者排除；总分最高者入选，平分取原序号最小者。'
               if select else '生成一条演化指令并按五项0-2分检查；不合格则停止。')
            + '选定指令后只生成一份formal_target，不生成多份答案择优。'
              '评分只评价指令与可见输入的适配，不能读取标准答案、其他方法答案或最终评审。'
              '证据不足时明确请求补充材料也是可回答任务，不应强迫唯一根因。'
              '生成记录与检查只在method_record保存；正式instruction不含审稿人或评分要求，'
              'formal_target只含正式诊断结论。'),
        'score_scale': {'0': '不满足或引入不支持内容', '1': '部分满足', '2': '充分满足'},
        'criteria': list(CRITERIA),
        'record_contract': {
            'recipe_id': recipe_id, 'recipe_version': '1',
            'input_sha256': 'copy shared_input_sha256', 'not_for_sft': True,
            'candidates': [{'candidate_id': 'I1..I3 in original order',
                'instruction': 'task instruction only',
                'operation': 'comparability|evidence_roles|bounded_scope|style',
                'scores': dict.fromkeys(CRITERIA, 'integer 0,1,2'),
                'grounding_ok': 'boolean self-declaration',
                'scope_ok': 'boolean self-declaration'}],
            'selected_candidate_id': 'computed winner ID'},
        'limitations': [
            'GPT instruction scores are not an independently trained Auto-Instruct ranker.',
            'Binding and score validation do not prove semantic truth.',
            'Store records at Case.internal_review when attaching to L1; never prompt/target.',
            'One proposal/selection/answer pass; no optimization against final test scores.'],
    }


def resolve_instruction_design(user: dict, record: dict) -> str:
    """Validate a frozen-input authoring record and return its selected instruction."""
    root_keys = {'recipe_id', 'recipe_version', 'input_sha256', 'not_for_sft',
                 'candidates', 'selected_candidate_id'}
    if not isinstance(record, dict) or set(record) != root_keys:
        raise DeliveryError('INSTRUCTION_RECORD_INVALID')
    recipe = authoring_recipe(record['recipe_id'])
    if record['recipe_version'] != '1' or record['not_for_sft'] is not True:
        raise DeliveryError('INSTRUCTION_RECORD_INVALID')
    if record['input_sha256'] != digest(user):
        raise DeliveryError('INSTRUCTION_INPUT_MISMATCH')
    candidates = record['candidates']
    if not isinstance(candidates, list) or len(candidates) != recipe['candidate_count']:
        raise DeliveryError('INSTRUCTION_RECORD_INVALID')
    texts, eligible = set(), []
    candidate_keys = {'candidate_id', 'instruction', 'operation', 'scores',
                      'grounding_ok', 'scope_ok'}
    for index, candidate in enumerate(candidates, 1):
        if not isinstance(candidate, dict) or set(candidate) != candidate_keys:
            raise DeliveryError('INSTRUCTION_RECORD_INVALID')
        instruction = candidate['instruction']
        if not isinstance(instruction, str) or not instruction.strip() or len(instruction) > 4000:
            raise DeliveryError('INSTRUCTION_RECORD_INVALID')
        normalized = ' '.join(instruction.split())
        operations = OPERATIONS if recipe['evolution_enabled'] else ('style',)
        if (candidate['candidate_id'] != f'I{index}' or normalized in texts
                or candidate['operation'] not in operations):
            raise DeliveryError('INSTRUCTION_RECORD_INVALID')
        texts.add(normalized)
        scores = candidate['scores']
        if (not isinstance(scores, dict) or set(scores) != set(CRITERIA)
                or any(type(v) is not int or v not in (0, 1, 2) for v in scores.values())
                or type(candidate['grounding_ok']) is not bool
                or type(candidate['scope_ok']) is not bool):
            raise DeliveryError('INSTRUCTION_RECORD_INVALID')
        if candidate['grounding_ok'] and candidate['scope_ok'] and all(scores.values()):
            eligible.append((sum(scores.values()), -index, candidate))
    if not eligible:
        raise DeliveryError('NO_ELIGIBLE_INSTRUCTION')
    chosen = max(eligible, key=lambda item: item[:2])[2]
    if record['selected_candidate_id'] != chosen['candidate_id']:
        raise DeliveryError('INSTRUCTION_SELECTION_MISMATCH')
    return chosen['instruction']
