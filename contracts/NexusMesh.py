# {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}
# NexusMesh — Agentic Economy Infrastructure

from genlayer.py import public
import genlayer.py.gl as gl
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
        self.owner = gl.message.sender_address.as_hex

    @public
    def register_agent(
        self,
        display_name: str,
        agent_type: str,
        skills: str,
        description: str,
        hourly_rate: int,
        availability: str,
    ) -> None:
        addr = gl.message.sender_address.as_hex

        prompt = f"""You are validating an agent profile for NexusMesh,
a decentralized AI-agent economy marketplace on GenLayer.

Agent Profile:
- Name: {display_name}
- Type: {agent_type}
- Skills: {skills}
- Description: {description}
- Hourly Rate (base units): {hourly_rate}
- Availability: {availability}

Evaluate this profile. Return ONLY valid JSON, no markdown, no extra text:
{{
  "approved": true,
  "quality_score": 80,
  "normalized_skills": ["skill1", "skill2"],
  "category": "development",
  "rejection_reason": ""
}}

Rules:
- approved = true unless profile is spam, empty, or malicious
- quality_score = 0-100 based on description completeness
- normalize all skill names to lowercase
- category options: development|design|research|operations|data|creative|other"""

        result_str = gl.exec_prompt(prompt)
        result = json.loads(result_str)

        gl.log(
            f"NexusMesh:AgentRegistered:{addr}:{display_name}:"
            f"{result.get('category','other')}:{result.get('quality_score',50)}"
        )

    @gl.public.write.payable
    def post_task(
        self,
        title: str,
        description: str,
        required_skills: str,
        delivery_timeline_hours: int,
        task_type: str,
    ) -> int:
        task_id = self.task_count
        budget = gl.message.value

        if budget <= 0:
            raise Exception("Task funding is required. Attach native GEN value to this transaction.")

        prompt = f"""Analyze this task posted to NexusMesh agent marketplace.

Task Details:
- Title: {title}
- Description: {description}
- Required Skills: {required_skills}
- Budget: {budget} base units of GEN
- Delivery Timeline: {delivery_timeline_hours} hours
- Type: {task_type}

Return ONLY valid JSON:
{{
  "complexity": "simple",
  "risk_level": "low",
  "clarity_score": 85,
  "estimated_hours": 8,
  "normalized_skills": ["skill1"],
  "improvement_tip": "one sentence tip to improve listing"
}}

complexity options: simple|moderate|complex|expert
risk_level options: low|medium|high"""

        enrichment_str = gl.exec_prompt(prompt)
        enrichment = json.loads(enrichment_str)

        gl.log(
            f"NexusMesh:TaskPosted:{task_id}:{title}:"
            f"{budget}:"
            f"{delivery_timeline_hours}:"
            f"{enrichment.get('complexity','moderate')}:"
            f"{enrichment.get('risk_level','medium')}"
        )

        self.task_count = task_id + 1
        return task_id

    @public
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
        bidder = gl.message.sender_address.as_hex

        prompt = f"""You are scoring a bid for a task on NexusMesh marketplace.

TASK:
- Title: {task_title}
- Description: {task_description}
- Required Skills: {required_skills}

BID:
- Agent: {agent_name}
- Agent Skills: {agent_skills}
- Reputation Score: {agent_reputation}/100
- Proposed Price: {proposed_price} base units of GEN
- Delivery Time: {delivery_blocks} hours
- Pitch: {pitch}
- Approach: {approach}

Score this bid and return ONLY valid JSON:
{{
  "match_score": 78,
  "skill_match": 85,
  "price_value": 70,
  "recommendation": "accept",
  "key_strength": "Strong Python and API experience",
  "key_concern": ""
}}

match_score: 0-100 overall bid quality for this task
recommendation options: strong_accept|accept|consider|reject"""

        result_str = gl.exec_prompt(prompt)
        result = json.loads(result_str)
        score = result.get("match_score", 50)

        gl.log(
            f"NexusMesh:BidSubmitted:{task_id}:{bidder}:"
            f"{score}:{result.get('recommendation','consider')}"
        )
        return score

    @public
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

Fetch and review the content at the delivery URL.
Assess whether the work meets the contract requirements.

Return ONLY valid JSON:
{{
  "approved": true,
  "quality_score": 85,
  "completeness_score": 90,
  "payment_percentage": 100,
  "detailed_feedback": "Work is complete and meets all requirements.",
  "revision_required": false,
  "revision_instructions": ""
}}

payment_percentage: 0-100
approved: true if quality_score >= 60 and work is acceptable"""

        result_str = gl.exec_prompt(prompt)
        result = json.loads(result_str)

        status = "completed" if result.get("approved", False) else "revision_needed"
        gl.log(
            f"NexusMesh:Evaluated:{contract_id}:{status}:"
            f"{result.get('quality_score',0)}:"
            f"{result.get('payment_percentage',0)}"
        )
        return json.dumps(result)

    @public
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
        prompt = f"""You are the NexusMesh AI Arbitrator — an impartial judge.

CONTRACT:
- Task: {task_description}
- Original Submission URL: {submission_url}

CLAIMANT STATEMENT: {claimant_statement}
Claimant Evidence URL: {claimant_evidence_url}

RESPONDENT STATEMENT: {respondent_statement}
Respondent Evidence URL: {respondent_evidence_url}

Fetch ALL evidence URLs. Review both sides fairly and issue a binding verdict.

Return ONLY valid JSON:
{{
  "ruling": "agent_wins",
  "client_refund_pct": 0,
  "agent_payment_pct": 100,
  "reasoning": "Detailed explanation of ruling based on evidence reviewed.",
  "fault_assessment": "Who bears responsibility and why.",
  "confidence": 88
}}

ruling options: client_wins | agent_wins | split
All percentages must sum to 100."""

        result_str = gl.exec_prompt(prompt)
        result = json.loads(result_str)

        gl.log(
            f"NexusMesh:DisputeResolved:{contract_id}:"
            f"{result.get('ruling','split')}:{result.get('confidence',50)}"
        )
        return json.dumps(result)

    @public
    def get_platform_fee(self) -> int:
        return self.platform_fee_bps

    @public
    def get_task_count(self) -> int:
        return self.task_count

    @public
    def get_contract_count(self) -> int:
        return self.contract_count

    @public
    def get_owner(self) -> str:
        return self.owner
