"""The product brief fields (Appendix A): which are required, and what to ask when one is missing.

The order here is the order of impact: questions about earlier fields are asked first.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    section: str
    key: str
    label: str
    required: bool
    question: str
    min_words: int = 1
    kind: str = "text"  # "text" | "list" | "choice"
    choices: tuple[str, ...] = ()
    min_items: int = 0
    ai_only: bool = False

    @property
    def path(self) -> str:
        return f"{self.section}.{self.key}"


R, OPT = True, False

FIELDS: list[Field] = [
    # Basics
    Field("basics", "product_name", "Product name", R, "What is the product called, exactly as it should appear?"),
    Field("basics", "company_name", "Company name", R, "What is the company name, exactly as it should appear?"),
    Field("basics", "launch_date", "Launch date", R, "When does this launch go live (a date or a target month)?"),
    Field("basics", "launch_size", "Launch size", R, "Is this a major, minor or feature launch?",
          kind="choice", choices=("major", "minor", "feature")),
    # Problem
    Field("problem", "problem_statement", "Problem statement", R,
          "In two or three sentences: what goes wrong for the customer today, and what does it cost them?",
          min_words=12),
    Field("problem", "who_has_it", "Who has the problem", R,
          "Which roles, at which kinds of company, feel this problem most?", min_words=3),
    Field("problem", "current_workarounds", "Current workarounds", R,
          "What do those people do today instead (spreadsheets, an older tool, an agency, nothing)?", min_words=3),
    # Solution
    Field("solution", "what_it_is", "What it is", R,
          "In one plain paragraph: what is the product and what does it do?", min_words=15),
    Field("solution", "capabilities", "Top capabilities", R,
          "What are the 3 to 5 capabilities a buyer would notice first? One line each.",
          kind="list", min_items=3),
    Field("solution", "how_it_works", "How it works", R,
          "Briefly, how does it work: the main steps or parts a customer would see?", min_words=10),
    # Target
    Field("target", "company_size", "Company size", R,
          "Which company sizes are you targeting (for example enterprise, mid-market, SMB)?"),
    Field("target", "regions", "Regions", R, "Which regions or countries is this launch for?"),
    Field("target", "primary_buyer_roles", "Primary buyer roles", R,
          "Who signs off on buying this, who champions it, and who uses it day to day?", min_words=2),
    # Value
    Field("value", "customer_outcomes", "Customer outcomes", OPT,
          "What measurable outcome should a customer expect: time saved, revenue, risk reduced?"),
    Field("value", "numbers_or_benchmarks", "Numbers or benchmarks", OPT,
          "Do you have any real numbers or benchmarks we can cite, and where do they come from?"),
    # Differentiation
    Field("differentiation", "why_us", "Why us", OPT, "Why would a buyer choose you over the alternatives?"),
    Field("differentiation", "known_competitors", "Known competitors", OPT,
          "Which competitors (including 'do nothing' or 'build in-house') come up most in deals?"),
    # Proof
    Field("proof", "customers", "Customers", OPT, "Which customers can be named, and are they approved for external use?"),
    Field("proof", "quotes", "Quotes", OPT, "Do you have customer quotes approved for external use?"),
    Field("proof", "metrics", "Metrics", OPT, "Do you have customer results (metrics) we can use, and with what permission?"),
    Field("proof", "case_studies", "Case studies", OPT, "Are there published case studies we can point to?"),
    # Pricing
    Field("pricing", "pricing_model", "Pricing model", OPT, "How will the product be priced (per seat, usage, platform fee...)?"),
    Field("pricing", "packaging", "Packaging", OPT, "How is it packaged: editions, tiers or add-ons?"),
    # Integrations
    Field("integrations", "ecosystem", "Ecosystem", OPT, "Which platforms or ecosystems does it belong to?"),
    Field("integrations", "integrations", "Integrations", OPT, "Which integrations matter most to buyers?"),
    Field("integrations", "dependencies", "Dependencies", OPT, "Does it depend on anything the customer must already have?"),
    # AI specifics
    Field("ai_specifics", "channels", "Channels", OPT, "Where does the AI work: chat, voice, email, inside another product?",
          ai_only=True),
    Field("ai_specifics", "autonomy_and_actions", "Autonomy and actions", OPT,
          "What can the AI do on its own, and what needs a person to approve?", ai_only=True),
    Field("ai_specifics", "guardrails", "Guardrails", OPT, "What guardrails keep the AI accurate and on-brand?", ai_only=True),
    Field("ai_specifics", "human_handoff", "Human handoff", OPT, "When and how does it hand off to a person?", ai_only=True),
    Field("ai_specifics", "certifications", "Certifications", OPT,
          "Which security or compliance certifications do you actually hold?", ai_only=True),
    Field("ai_specifics", "outcome_metrics", "Outcome metrics", OPT,
          "Which outcome metrics do you track for the AI (resolution rate, accuracy...)?", ai_only=True),
    # Constraints
    Field("constraints", "claims_we_cant_make", "Claims we can't make", OPT,
          "Are there claims this launch must not make?"),
    Field("constraints", "legal_limits", "Legal limits", OPT, "Any legal limits on what we can say?"),
    Field("constraints", "embargoes", "Embargoes", OPT, "Is anything embargoed until a certain date?"),
    # Free-form
    Field("free_form", "anything_else", "Anything else we should know", OPT, ""),
]

BY_PATH = {f.path: f for f in FIELDS}
SECTIONS = list(dict.fromkeys(f.section for f in FIELDS))
