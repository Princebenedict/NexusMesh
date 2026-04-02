# {"Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0"}

import json
import typing
from dataclasses import dataclass

import genlayer as gl
from genlayer import DynArray, TreeMap, allow_storage


MAX_REPUTATION = 100
TOKEN_SYMBOL = "$GEN"


@allow_storage
@dataclass
class Task:
    task_id: int
    creator: str
    title: str
    description: str
    required_skills: str
    budget: int
    task_type: str
    complexity: str
    risk_level: str
    clarity_score: int
    estimated_hours: int
    improvement_tip: str
    status: str
    awarded_application_id: int


@allow_storage
@dataclass
class Application:
    application_id: int
    task_id: int
    bidder: str
    task_title: str
    task_description: str
    required_skills: str
    agent_name: str
    agent_skills: str
    agent_reputation: int
    proposed_price: int
    profile_links: str
    pitch: str
    approach: str
    match_score: int
    skill_match: int
    price_value: int
    recommendation: str
    key_strength: str
    key_concern: str
    status: str
    founder_feedback: str
    evaluation_result: str


@allow_storage
@dataclass
class FeedbackRecord:
    feedback_id: int
    task_id: int
    application_id: int
    founder: str
    bidder: str
    verdict: str
    feedback: str


@allow_storage
@dataclass
class AgentProfile:
    wallet: str
    display_name: str
    agent_type: str
    skills: str
    description: str
    hourly_rate: int
    availability: str
    quality_score: int
    category: str
    approved: bool


class NexusMesh(gl.Contract):
    owner: str
    platform_fee_bps: int
    task_count: int
    application_count: int
    contract_count: int
    feedback_count: int
    task_ids: DynArray[int]
    application_ids: DynArray[int]
    feedback_ids: DynArray[int]
    tasks: TreeMap[int, Task]
    applications: TreeMap[int, Application]
    feedback_records: TreeMap[int, FeedbackRecord]
    task_applications: TreeMap[int, DynArray[int]]
    agents: TreeMap[str, AgentProfile]

    def __init__(self, platform_fee_bps: int = 250) -> None:
        self.owner = str(gl.message.sender_address)
        self.platform_fee_bps = platform_fee_bps
        self.task_count = 0
        self.application_count = 0
        self.contract_count = 0
        self.feedback_count = 0
        self.task_ids = DynArray()
        self.application_ids = DynArray()
        self.feedback_ids = DynArray()
        self.tasks = TreeMap()
        self.applications = TreeMap()
        self.feedback_records = TreeMap()
        self.task_applications = TreeMap()
        self.agents = TreeMap()

    def _safe_json(self, payload: str) -> typing.Dict[str, typing.Any]:
        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return {}

    def _ask_ai(self, prompt: str) -> typing.Dict[str, typing.Any]:
        try:
            result = gl.exec_prompt(prompt)
            return self._safe_json(result)
        except Exception:
            return {}

    def _get_task(self, task_id: int) -> Task:
        task = self.tasks.get(task_id)
        assert task is not None, "Task does not exist"
        return task

    def _get_application(self, application_id: int) -> Application:
        application = self.applications.get(application_id)
        assert application is not None, "Application does not exist"
        return application

    def _get_task_application_ids(self, task_id: int) -> DynArray[int]:
        ids = self.task_applications.get(task_id)
        if ids is None:
            return DynArray()
        return ids

    def _find_task_id_by_title(self, title: str) -> int:
        found_id = -1
        for task_id in self.task_ids:
            task = self.tasks.get(task_id)
            if task is not None and task.title == title:
                found_id = task_id
        return found_id

    def _find_task_id_by_description(self, description: str) -> int:
        found_id = -1
        for task_id in self.task_ids:
            task = self.tasks.get(task_id)
            if task is not None and task.description == description:
                found_id = task_id
        return found_id

    def _task_to_dict(self, task: Task) -> typing.Dict[str, typing.Any]:
        ids = self._get_task_application_ids(task.task_id)
        return {
            "task_id": task.task_id,
            "creator": task.creator,
            "title": task.title,
            "description": task.description,
            "required_skills": task.required_skills,
            "budget": task.budget,
            "budget_token": TOKEN_SYMBOL,
            "task_type": task.task_type,
            "complexity": task.complexity,
            "risk_level": task.risk_level,
            "clarity_score": task.clarity_score,
            "estimated_hours": task.estimated_hours,
            "improvement_tip": task.improvement_tip,
            "status": task.status,
            "awarded_application_id": task.awarded_application_id,
            "application_count": len(ids),
        }

    def _application_to_dict(self, application: Application) -> typing.Dict[str, typing.Any]:
        return {
            "application_id": application.application_id,
            "task_id": application.task_id,
            "bidder": application.bidder,
            "task_title": application.task_title,
            "task_description": application.task_description,
            "required_skills": application.required_skills,
            "agent_name": application.agent_name,
            "agent_skills": application.agent_skills,
            "agent_reputation": application.agent_reputation,
            "max_reputation": MAX_REPUTATION,
            "proposed_price": application.proposed_price,
            "price_token": TOKEN_SYMBOL,
            "profile_links": application.profile_links,
            "pitch": application.pitch,
            "approach": application.approach,
            "match_score": application.match_score,
            "skill_match": application.skill_match,
            "price_value": application.price_value,
            "recommendation": application.recommendation,
            "key_strength": application.key_strength,
            "key_concern": application.key_concern,
            "status": application.status,
            "founder_feedback": application.founder_feedback,
            "evaluation_result": application.evaluation_result,
        }

    def _feedback_to_dict(self, record: FeedbackRecord) -> typing.Dict[str, typing.Any]:
        return {
            "feedback_id": record.feedback_id,
            "task_id": record.task_id,
            "application_id": record.application_id,
            "founder": record.founder,
            "bidder": record.bidder,
            "verdict": record.verdict,
            "feedback": record.feedback,
        }

    def _agent_to_dict(self, agent: AgentProfile) -> typing.Dict[str, typing.Any]:
        return {
            "wallet": agent.wallet,
            "display_name": agent.display_name,
            "agent_type": agent.agent_type,
            "skills": agent.skills,
            "description": agent.description,
            "hourly_rate": agent.hourly_rate,
            "availability": agent.availability,
            "quality_score": agent.quality_score,
            "category": agent.category,
            "approved": agent.approved,
        }

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
        wallet = str(gl.message.sender_address)

        prompt = f"""Validate this NexusMesh agent profile and return only valid JSON:
{{
  "approved": true,
  "quality_score": 80,
  "normalized_skills": ["python", "fastapi"],
  "category": "development",
  "rejection_reason": ""
}}

Name: {display_name}
Type: {agent_type}
Skills: {skills}
Description: {description}
Hourly rate: {hourly_rate}
Availability: {availability}
"""
        result = self._ask_ai(prompt)
        normalized_skills = json.dumps(result.get("normalized_skills", []), sort_keys=True)

        profile = gl.storage.inmem_allocate(
            AgentProfile,
            wallet,
            display_name,
            agent_type,
            normalized_skills if normalized_skills != "[]" else skills,
            description,
            hourly_rate,
            availability,
            int(result.get("quality_score", 60)),
            str(result.get("category", "other")),
            bool(result.get("approved", True)),
        )
        self.agents[wallet] = profile
        gl.log(f"NexusMesh:AgentRegistered:{wallet}:{display_name}")
        return json.dumps(self._agent_to_dict(profile), sort_keys=True)

    @gl.public.write.payable
    def post_task(
        self,
        title: str,
        description: str,
        required_skills: str,
        task_type: str,
    ) -> int:
        budget = int(gl.message.value)
        assert budget > 0, f"Attach {TOKEN_SYMBOL} to fund the task"

        prompt = f"""Analyze this NexusMesh task and return only valid JSON:
{{
  "complexity": "moderate",
  "risk_level": "medium",
  "clarity_score": 84,
  "estimated_hours": 10,
  "normalized_skills": ["python"],
  "improvement_tip": "Add acceptance criteria."
}}

Title: {title}
Description: {description}
Required skills: {required_skills}
Budget: {budget}
Budget token: {TOKEN_SYMBOL}
Task type: {task_type}
"""
        enrichment = self._ask_ai(prompt)
        task_id = self.task_count

        task = gl.storage.inmem_allocate(
            Task,
            task_id,
            str(gl.message.sender_address),
            title,
            description,
            json.dumps(enrichment.get("normalized_skills", []), sort_keys=True)
            if enrichment.get("normalized_skills")
            else required_skills,
            budget,
            task_type,
            str(enrichment.get("complexity", "moderate")),
            str(enrichment.get("risk_level", "medium")),
            int(enrichment.get("clarity_score", 70)),
            int(enrichment.get("estimated_hours", 8)),
            str(enrichment.get("improvement_tip", "")),
            "open",
            -1,
        )

        self.tasks[task_id] = task
        self.task_applications[task_id] = DynArray()
        self.task_ids.append(task_id)
        self.task_count = task_id + 1

        gl.log(f"NexusMesh:TaskPosted:{task_id}:{title}")
        return task_id

    @gl.public.write
    def submit_bid(
        self,
        task_title: str,
        task_description: str,
        required_skills: str,
        agent_name: str,
        agent_skills: str,
        agent_reputation: int,
        proposed_price: int,
        profile_links: str,
        pitch: str,
        approach: str,
    ) -> int:
        reputation = max(0, min(MAX_REPUTATION, int(agent_reputation)))
        task_id = self._find_task_id_by_title(task_title)
        assert task_id >= 0, "Task title not found on-chain"

        task = self._get_task(task_id)
        assert task.status in ("open", "shortlisted"), "Task is not accepting applications"

        prompt = f"""Score this NexusMesh bid strictly and return only valid JSON:
{{
  "match_score": 78,
  "skill_match": 85,
  "price_value": 74,
  "recommendation": "accept",
  "key_strength": "Strong public proof of work",
  "key_concern": ""
}}

Task title: {task_title}
Task description: {task_description}
Required skills: {required_skills}
Agent name: {agent_name}
Agent skills: {agent_skills}
Reputation: {reputation}
Max reputation: {MAX_REPUTATION}
Profile links and credibility proof: {profile_links}
Proposed price: {proposed_price}
Price token: {TOKEN_SYMBOL}
Pitch: {pitch}
Approach: {approach}
"""
        result = self._ask_ai(prompt)
        application_id = self.application_count

        application = gl.storage.inmem_allocate(
            Application,
            application_id,
            task_id,
            str(gl.message.sender_address),
            task_title,
            task_description,
            required_skills,
            agent_name,
            agent_skills,
            reputation,
            proposed_price,
            profile_links,
            pitch,
            approach,
            int(result.get("match_score", 50)),
            int(result.get("skill_match", 50)),
            int(result.get("price_value", 50)),
            str(result.get("recommendation", "consider")),
            str(result.get("key_strength", "")),
            str(result.get("key_concern", "")),
            "pending",
            "",
            "",
        )

        self.applications[application_id] = application
        self.application_ids.append(application_id)

        ids = self._get_task_application_ids(task_id)
        ids.append(application_id)
        self.task_applications[task_id] = ids

        self.application_count = application_id + 1
        gl.log(f"NexusMesh:BidSubmitted:{task_id}:{application_id}")
        return application_id

    @gl.public.write
    def submit_application_feedback(
        self,
        task_id: int,
        application_id: int,
        verdict: str,
        feedback: str,
    ) -> int:
        task = self._get_task(task_id)
        application = self._get_application(application_id)
        founder = str(gl.message.sender_address)

        assert application.task_id == task_id, "Application does not belong to task"
        assert founder == task.creator or founder == self.owner, "Only founder can submit feedback"

        application.status = verdict
        application.founder_feedback = feedback
        self.applications[application_id] = application

        if verdict in ("accepted", "awarded", "hired"):
            if task.awarded_application_id == -1:
                self.contract_count = self.contract_count + 1
            task.status = "assigned"
            task.awarded_application_id = application_id
        elif verdict == "shortlisted":
            task.status = "shortlisted"

        self.tasks[task_id] = task

        feedback_id = self.feedback_count
        record = gl.storage.inmem_allocate(
            FeedbackRecord,
            feedback_id,
            task_id,
            application_id,
            founder,
            application.bidder,
            verdict,
            feedback,
        )
        self.feedback_records[feedback_id] = record
        self.feedback_ids.append(feedback_id)
        self.feedback_count = feedback_id + 1

        gl.log(f"NexusMesh:FeedbackSubmitted:{task_id}:{application_id}:{verdict}")
        return feedback_id

    @gl.public.write
    def evaluate_work(
        self,
        task_title: str,
        task_description: str,
        submission_url: str,
        submission_notes: str,
    ) -> str:
        task_id = self._find_task_id_by_title(task_title)
        result_prompt = f"""Evaluate this NexusMesh delivery and return only valid JSON:
{{
  "approved": true,
  "quality_score": 85,
  "completeness_score": 90,
  "payment_percentage": 100,
  "detailed_feedback": "Work meets requirements.",
  "revision_required": false,
  "revision_instructions": ""
}}

Task title: {task_title}
Task description: {task_description}
Submission URL: {submission_url}
Notes: {submission_notes}
"""
        result = self._ask_ai(result_prompt)
        serialized = json.dumps(result, sort_keys=True)

        if task_id >= 0:
            task = self._get_task(task_id)
            if task.awarded_application_id >= 0:
                application = self._get_application(task.awarded_application_id)
                application.evaluation_result = serialized
                application.founder_feedback = str(result.get("detailed_feedback", application.founder_feedback))
                application.status = "completed" if bool(result.get("approved", False)) else "revision_needed"
                self.applications[task.awarded_application_id] = application
                task.status = application.status
                self.tasks[task_id] = task

        gl.log(f"NexusMesh:Evaluated:{task_title}")
        return serialized

    @gl.public.write
    def resolve_dispute(
        self,
        task_description: str,
        claimant_statement: str,
        claimant_evidence_url: str,
        respondent_statement: str,
        respondent_evidence_url: str,
    ) -> str:
        task_id = self._find_task_id_by_description(task_description)

        prompt = f"""Resolve this NexusMesh dispute and return only valid JSON:
{{
  "ruling": "agent_wins",
  "client_refund_pct": 0,
  "agent_payment_pct": 100,
  "reasoning": "Decision grounded in supplied evidence.",
  "fault_assessment": "No material fault by the agent.",
  "confidence": 88
}}

Task description: {task_description}
Claimant: {claimant_statement}
Claimant evidence: {claimant_evidence_url}
Respondent: {respondent_statement}
Respondent evidence: {respondent_evidence_url}
"""
        result = self._ask_ai(prompt)
        serialized = json.dumps(result, sort_keys=True)

        if task_id >= 0:
            task = self._get_task(task_id)
            task.status = "disputed"
            self.tasks[task_id] = task
            if task.awarded_application_id >= 0:
                application = self._get_application(task.awarded_application_id)
                application.status = "disputed"
                application.evaluation_result = serialized
                self.applications[task.awarded_application_id] = application

        gl.log("NexusMesh:DisputeResolved")
        return serialized

    @gl.public.view
    def get_task(self, task_id: int) -> str:
        return json.dumps(self._task_to_dict(self._get_task(task_id)), sort_keys=True)

    @gl.public.view
    def get_task_applications(self, task_id: int) -> str:
        ids = self._get_task_application_ids(task_id)
        items = []
        for application_id in ids:
            application = self.applications.get(application_id)
            if application is not None:
                items.append(self._application_to_dict(application))
        return json.dumps(items, sort_keys=True)

    @gl.public.view
    def get_founder_dashboard(self, founder: str) -> str:
        posted_tasks = []
        incoming_applications = []
        feedback = []

        for task_id in self.task_ids:
            task = self.tasks.get(task_id)
            if task is not None and task.creator == founder:
                posted_tasks.append(self._task_to_dict(task))
                ids = self._get_task_application_ids(task_id)
                for application_id in ids:
                    application = self.applications.get(application_id)
                    if application is not None:
                        incoming_applications.append(self._application_to_dict(application))

        for feedback_id in self.feedback_ids:
            record = self.feedback_records.get(feedback_id)
            if record is not None and record.founder == founder:
                feedback.append(self._feedback_to_dict(record))

        return json.dumps({
            "posted_tasks": posted_tasks,
            "incoming_applications": incoming_applications,
            "feedback_sent": feedback,
            "token_symbol": TOKEN_SYMBOL,
            "max_reputation": MAX_REPUTATION,
        }, sort_keys=True)

    @gl.public.view
    def get_bidder_dashboard(self, bidder: str) -> str:
        applications = []
        feedback = []

        for application_id in self.application_ids:
            application = self.applications.get(application_id)
            if application is not None and application.bidder == bidder:
                applications.append(self._application_to_dict(application))

        for feedback_id in self.feedback_ids:
            record = self.feedback_records.get(feedback_id)
            if record is not None and record.bidder == bidder:
                feedback.append(self._feedback_to_dict(record))

        return json.dumps({
            "applications": applications,
            "feedback_received": feedback,
            "token_symbol": TOKEN_SYMBOL,
            "max_reputation": MAX_REPUTATION,
        }, sort_keys=True)

    @gl.public.view
    def get_marketplace_snapshot(self) -> str:
        tasks = []
        for task_id in self.task_ids:
            task = self.tasks.get(task_id)
            if task is not None:
                tasks.append(self._task_to_dict(task))

        return json.dumps({
            "owner": self.owner,
            "task_count": self.task_count,
            "application_count": self.application_count,
            "contract_count": self.contract_count,
            "feedback_count": self.feedback_count,
            "platform_fee_bps": self.platform_fee_bps,
            "token_symbol": TOKEN_SYMBOL,
            "max_reputation": MAX_REPUTATION,
            "tasks": tasks,
        }, sort_keys=True)

    @gl.public.view
    def get_agent(self, wallet: str) -> str:
        profile = self.agents.get(wallet)
        if profile is None:
            return json.dumps({}, sort_keys=True)
        return json.dumps(self._agent_to_dict(profile), sort_keys=True)

    @gl.public.view
    def get_platform_fee(self) -> int:
        return self.platform_fee_bps

    @gl.public.view
    def get_task_count(self) -> int:
        return self.task_count

    @gl.public.view
    def get_application_count(self) -> int:
        return self.application_count

    @gl.public.view
    def get_contract_count(self) -> int:
        return self.contract_count

    @gl.public.view
    def get_feedback_count(self) -> int:
        return self.feedback_count

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner

    @gl.public.view
    def get_max_reputation(self) -> int:
        return MAX_REPUTATION
