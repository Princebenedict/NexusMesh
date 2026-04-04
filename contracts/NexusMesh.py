# {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}
# pyright: reportMissingImports=false, reportUndefinedVariable=false

from genlayer import *

import json


class NexusMesh(gl.Contract):
    task_count: int
    contract_count: int
    platform_fee_bps: int
    owner: str

    def __init__(self, platform_fee_bps: int) -> None:
        self.task_count = 0
        self.contract_count = 0
        self.platform_fee_bps = platform_fee_bps
        self.owner = gl.message.sender_address.as_hex()

    def _normalize_json(self, response: str) -> str:
        cleaned = response.replace("```json", "").replace("```", "").strip()
        return json.dumps(json.loads(cleaned), sort_keys=True)

    @gl.public.write
    def register_agent(
        self,
        display_name: str,
        agent_type: str,
        skills: str,
        description: str,
        hourly_rate: int,
        availability: str,
    ) -> str:
        addr = gl.message.sender_address.as_hex()

        prompt = f"""You are validating an agent profile for NexusMesh.

Agent Profile:
- Name: {display_name}
- Type: {agent_type}
- Skills: {skills}
- Description: {description}
- Hourly Rate (wei): {hourly_rate}
- Availability: {availability}

Return ONLY valid JSON:
{{
  "approved": true,
  "quality_score": 80,
  "normalized_skills": ["skill1", "skill2"],
  "category": "development",
  "rejection_reason": ""
}}"""

        def nondet() -> str:
            return self._normalize_json(gl.exec_prompt(prompt))

        result_json = gl.eq_principle_strict_eq(nondet)
        result = json.loads(result_json)

        gl.log(
            f"NexusMesh:AgentRegistered:{addr}:{display_name}:"
            f"{result.get('category', 'other')}:{result.get('quality_score', 50)}"
        )

        return result_json

    @gl.public.write
    def post_task(
        self,
        title: str,
        description: str,
        required_skills: str,
        budget: int,
        deadline_blocks: int,
        task_type: str,
    ) -> int:
        task_id = self.task_count

        prompt = f"""Analyze this task posted to NexusMesh.

Task Details:
- Title: {title}
- Description: {description}
- Required Skills: {required_skills}
- Budget: {budget} wei
- Deadline Blocks: {deadline_blocks}
- Type: {task_type}

Return ONLY valid JSON:
{{
  "complexity": "simple",
  "risk_level": "low",
  "clarity_score": 85,
  "estimated_hours": 8,
  "normalized_skills": ["skill1"],
  "improvement_tip": "one sentence tip to improve listing"
}}"""

        def nondet() -> str:
            return self._normalize_json(gl.exec_prompt(prompt))

        enrichment_json = gl.eq_principle_strict_eq(nondet)
        enrichment = json.loads(enrichment_json)

        gl.log(
            f"NexusMesh:TaskPosted:{task_id}:{title}:"
            f"{enrichment.get('complexity', 'moderate')}:"
            f"{enrichment.get('risk_level', 'medium')}"
        )

        self.task_count = task_id + 1
        return task_id

    @gl.public.write
    def submit_bid(
        self,
        task_id: int,
        task_title: str,
        task_description: str,
        required_skills: str,
        agent_name: str,
        agent_skills: str,
        agent_reputation: int,
        proposed_price: int,
        delivery_blocks: int,
        pitch: str,
        approach: str,
    ) -> int:
        bidder = gl.message.sender_address.as_hex()

        prompt = f"""You are scoring a bid for a task on NexusMesh.

TASK:
- Title: {task_title}
- Description: {task_description}
- Required Skills: {required_skills}

BID:
- Agent: {agent_name}
- Agent Skills: {agent_skills}
- Reputation Score: {agent_reputation}/100
- Proposed Price: {proposed_price} wei
- Delivery Time: {delivery_blocks} blocks
- Pitch: {pitch}
- Approach: {approach}

Return ONLY valid JSON:
{{
  "match_score": 78,
  "skill_match": 85,
  "price_value": 70,
  "recommendation": "accept",
  "key_strength": "Strong Python and API experience",
  "key_concern": ""
}}"""

        def nondet() -> str:
            return self._normalize_json(gl.exec_prompt(prompt))

        result_json = gl.eq_principle_strict_eq(nondet)
        result = json.loads(result_json)
        score = int(result.get("match_score", 50))

        gl.log(
            f"NexusMesh:BidSubmitted:{task_id}:{bidder}:"
            f"{score}:{result.get('recommendation', 'consider')}"
        )
        return score

    @gl.public.write
    def evaluate_delivery(
        self,
        contract_id: int,
        task_title: str,
        task_description: str,
        required_skills: str,
        submission_url: str,
        submission_notes: str,
    ) -> str:
        prompt = f"""You are an impartial AI evaluator for NexusMesh work contracts.

CONTRACT DETAILS:
- Task: {task_title}
- Description: {task_description}
- Required Skills: {required_skills}

SUBMITTED WORK:
- Delivery URL: {submission_url}
- Notes: {submission_notes}

Return ONLY valid JSON:
{{
  "approved": true,
  "quality_score": 85,
  "completeness_score": 90,
  "payment_percentage": 100,
  "detailed_feedback": "Work is complete and meets all requirements.",
  "revision_required": false,
  "revision_instructions": ""
}}"""

        def nondet() -> str:
            return self._normalize_json(gl.exec_prompt(prompt))

        result_json = gl.eq_principle_strict_eq(nondet)
        result = json.loads(result_json)

        status = "completed" if result.get("approved", False) else "revision_needed"
        gl.log(
            f"NexusMesh:Evaluated:{contract_id}:{status}:"
            f"{result.get('quality_score', 0)}:"
            f"{result.get('payment_percentage', 0)}"
        )
        return result_json

    @gl.public.write
    def resolve_dispute(
        self,
        contract_id: int,
        task_description: str,
        submission_url: str,
        claimant_statement: str,
        claimant_evidence_url: str,
        respondent_statement: str,
        respondent_evidence_url: str,
    ) -> str:
        prompt = f"""You are the NexusMesh AI Arbitrator.

CONTRACT:
- Task: {task_description}
- Original Submission URL: {submission_url}

CLAIMANT STATEMENT: {claimant_statement}
Claimant Evidence URL: {claimant_evidence_url}

RESPONDENT STATEMENT: {respondent_statement}
Respondent Evidence URL: {respondent_evidence_url}

Return ONLY valid JSON:
{{
  "ruling": "agent_wins",
  "client_refund_pct": 0,
  "agent_payment_pct": 100,
  "reasoning": "Detailed explanation of ruling based on evidence reviewed.",
  "fault_assessment": "Who bears responsibility and why.",
  "confidence": 88
}}"""

        def nondet() -> str:
            return self._normalize_json(gl.exec_prompt(prompt))

        result_json = gl.eq_principle_strict_eq(nondet)
        result = json.loads(result_json)

        gl.log(
            f"NexusMesh:DisputeResolved:{contract_id}:"
            f"{result.get('ruling', 'split')}:{result.get('confidence', 50)}"
        )
        return result_json

    @gl.public.view
    def get_platform_fee(self) -> int:
        return self.platform_fee_bps

    @gl.public.view
    def get_task_count(self) -> int:
        return self.task_count

    @gl.public.view
    def get_contract_count(self) -> int:
        return self.contract_count

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner
