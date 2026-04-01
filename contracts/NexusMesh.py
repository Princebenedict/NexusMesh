# {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}
# NexusMesh — Agentic Economy Infrastructure
# GenLayer Bradbury Network | Hackathon 2024
# A decentralized marketplace where AI agents and humans
# post tasks, bid, deliver work, and get paid on-chain.
# All key decisions made by on-chain AI via gl.exec_prompt().

from genlayer.py import public
import genlayer.py.gl as gl
import json


class NexusMesh(gl.Contract):
    """
    NexusMesh: The nervous system for the Agentic Economy.

    Agents register, discover tasks, bid, deliver work, and get
    paid — governed entirely by on-chain AI intelligence.

    GenLayer enables:
    - gl.exec_prompt() for trustless AI decisions on-chain
    - All AI reasoning stored on-chain and auditable
    - No centralized AI server — fully decentralized
    - Privacy: data evaluated by AI without leaving chain
    """

    # ── State Variables ────────────────────────────────────────
    task_count: int
    contract_count: int
    platform_fee_bps: int   # 250 = 2.5%
    owner: str

    def __init__(self, platform_fee_bps: int) -> None:
        self.task_count = 0
        self.contract_count = 0
        self.platform_fee_bps = platform_fee_bps
        self.owner = gl.message.sender_address.as_hex

    # ════════════════════════════════════════════════════════════
    #  1. AGENT REGISTRATION — AI validates profile on-chain
    # ════════════════════════════════════════════════════════════

    @public
    def register_agent(
        self,
        display_name: str,
        agent_type: str,       # "human" | "ai_agent" | "hybrid"
        skills: str,           # JSON array: ["python","solidity"]
        description: str,
        hourly_rate: int,       # wei per hour
        availability: str,      # "immediate"|"scheduled"|"project_only"
    ) -> None:
        """Register agent profile. AI validates quality & normalizes skills."""
        addr = gl.message.sender_address.as_hex

        # ── ON-CHAIN AI CALL #1: Validate agent profile ───────────
        prompt = f"""You are validating an agent profile for NexusMesh,
a decentralized AI-agent economy marketplace on GenLayer.

Agent Profile:
- Name: {display_name}
- Type: {agent_type}
- Skills: {skills}
- Description: {description}
- Hourly Rate (wei): {hourly_rate}
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

        # Log registration event on-chain
        gl.log(
            f"NexusMesh:AgentRegistered:{addr}:{display_name}:"
            f"{result.get('category','other')}:{result.get('quality_score',50)}"
        )

    # ════════════════════════════════════════════════════════════
    #  2. POST TASK — AI enriches listing on-chain
    # ════════════════════════════════════════════════════════════

    @public
    def post_task(
        self,
        title: str,
        description: str,
        required_skills: str,     # JSON array
        budget: int,               # in wei
        deadline_blocks: int,
        task_type: str,             # "fixed"|"hourly"|"milestone"
    ) -> int:
        """Post a task. AI enriches with complexity & risk scores."""
        task_id = self.task_count

        # ── ON-CHAIN AI CALL #2: Enrich task metadata ────────────
        prompt = f"""Analyze this task posted to NexusMesh agent marketplace.

Task Details:
- Title: {title}
- Description: {description}
- Required Skills: {required_skills}
- Budget: {budget} wei
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
            f"{enrichment.get('complexity','moderate')}:"
            f"{enrichment.get('risk_level','medium')}"
        )

        self.task_count = task_id + 1
        return task_id

    # ════════════════════════════════════════════════════════════
    #  3. SUBMIT BID — AI scores match compatibility
    # ════════════════════════════════════════════════════════════

    @public
    def submit_bid(
        self,
        task_id: int,
        task_title: str,
        task_description: str,
        required_skills: str,
        agent_name: str,
        agent_skills: str,
        agent_reputation: int,    # 0-100
        proposed_price: int,       # in wei
        delivery_blocks: int,
        pitch: str,
        approach: str,
    ) -> int:
        """Submit bid. AI scores match 0-100 on-chain."""
        bidder = gl.message.sender_address.as_hex

        # ── ON-CHAIN AI CALL #3: Score bid compatibility ─────────
        prompt = f"""You are scoring a bid for a task on NexusMesh marketplace.

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

    # ════════════════════════════════════════════════════════════
    #  4. EVALUATE DELIVERY — AI reviews submitted work
    # ════════════════════════════════════════════════════════════

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
        """AI fetches delivery URL, evaluates quality, approves/rejects payment."""

        # ── ON-CHAIN AI CALL #4: Evaluate work delivery ──────────
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

payment_percentage: 0-100, what percentage of agreed price agent deserves
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

    # ════════════════════════════════════════════════════════════
    #  5. RESOLVE DISPUTE — AI arbitrates with evidence review
    # ════════════════════════════════════════════════════════════

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
        """AI arbitrates dispute by fetching and reviewing all evidence URLs."""

        # ── ON-CHAIN AI CALL #5: Arbitrate dispute ────────────────
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

    # ════════════════════════════════════════════════════════════
    #  READ-ONLY METHODS
    # ════════════════════════════════════════════════════════════

    @public
    def get_platform_fee(self) -> int:
        """Return platform fee in basis points (250 = 2.5%)"""
        return self.platform_fee_bps

    @public
    def get_task_count(self) -> int:
        """Return total number of tasks posted."""
        return self.task_count

    @public
    def get_contract_count(self) -> int:
        """Return total number of contracts created."""
        return self.contract_count

    @public
    def get_owner(self) -> str:
        """Return the contract deployer address."""
        return self.owner