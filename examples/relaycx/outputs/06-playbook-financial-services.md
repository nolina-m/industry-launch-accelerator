# Industry playbook: Financial services

**My Product Launch · RelayCX is a fictional test product, not a real product** · Financial services

_Draft · Unbranded draft · Approved by PMM 2026-10-19_

## Who to target

- First: US credit unions and regional banks with 50 to 500 service staff that already run a chatbot or digital banking platform and have usable APIs on their loan servicing system [ASSUMPTION].
- Second: institutions in or just after a merger or core conversion, where repeat contacts rise (T-financial-services-6) [ASSUMPTION].
- Third: non-bank consumer lenders with heavy document collection, positioned with the FTC Safeguards Rule in mind (R-financial-services-2).

The contact center director usually brings the problem and champions it to the COO or VP Customer Service, who signs. The CIO tests integration feasibility, the CISO tests verification and access, and the Chief Risk and Compliance Officer runs third-party risk review and can stop the deal. Service reps shape the champion's view through pilot feedback [ASSUMPTION].

## Why now

- **I-financial-services-1:** Most credit unions and about half of banks already run generative AI [S4]; the next step is finishing routine requests with controls examiners can follow [S8].
- **I-financial-services-2:** The CFPB has warned that chatbots blocking access to human help can break the law [S9]. Every AI channel needs a fast path to a person.
- **I-financial-services-3:** FinCEN reports fraudsters using deepfakes and fake IDs to get past verification [S12]; any channel that acts on accounts must verify first.
- **I-financial-services-4:** Banks must manage risk across the life cycle of every third-party relationship [S14]; AI vendors need evidence ready on day one.
- **I-financial-services-5:** Credit unions fell to 4,214 in Q2 2026 from 4,370 a year earlier [S13]; surviving institutions must absorb more members without matching headcount growth [ASSUMPTION].

## Value story by persona

| Persona | Message | Pillar |
|---|---|---|
| Chief Operating Officer | Serve members and customers like a national bank, without a national bank's AI budget. | PL-1 |
| Contact center and service operations director | Stop inheriting the chatbot's unfinished work: requests arrive done, or with every step so far. | PL-1 |
| Chief Information Officer | Add completed service tasks to your core and loan systems through the APIs you already support, one workflow at a time. | PL-2 |
| Chief Risk and Compliance Officer | Show examiners exactly what the agent did, when a person stepped in, and why. | PL-3 |
| Chief Information Security Officer | Verify the customer before anything sensitive happens, using your authentication and only the actions you allow. | PL-2 |
| Member or customer service representative | Spend your day helping members, not chasing loan documents they already sent. | PL-4 |

## Discovery guide

### Chief Operating Officer

| Ask | What good sounds like |
|---|---|
| Which routine requests take the most staff time today, and how many need more than one contact? | They can name one or two request types with real volume and know they generate repeat contacts. |
| What does your growth plan for the next two years assume about service headcount? | Growth or a merger is planned without matching headcount, so capacity is a stated gap. |
| What would you need to see in a pilot to expand it? | Clear, measurable criteria such as completion rate or repeat contacts, and a named owner. |

### Contact center and service operations director

| Ask | What good sounds like |
|---|---|
| What happens today when your chatbot can't answer: what does the agent see? | Agents get the customer with little or no history, and the director is frustrated by it. |
| Walk me through the last request that bounced between email, phone and chat. | A specific, recent story with multiple touches and re-verification. |
| What would a handoff need to contain for your team to trust it? | Concrete fields: identity status, what was done, what is left. |

### Chief Information Officer

| Ask | What good sounds like |
|---|---|
| Which systems would an agent need to read from and write to for your highest-volume request? | Two or three named systems, at least one with a supported API. |
| Where do your core and loan servicing systems expose usable APIs today? | Existing APIs or middleware in use, not a multi-year integration project. |
| What would make you choose to buy rather than build here? | Limited engineering capacity and a preference for vendor-maintained integrations. |

### Chief Risk and Compliance Officer

| Ask | What good sounds like |
|---|---|
| What would your third-party risk review need from an AI vendor on day one? | A defined checklist the vendor can prepare for, rather than an open-ended process. |
| Which customer requests must always reach a person? | Clear categories such as disputes, complaints and hardship, which can be configured as hard handoffs. |
| How do you capture and honor SMS opt-outs across channels today? | A known gap or manual process that a consistent capability would close. |

### Chief Information Security Officer

| Ask | What good sounds like |
|---|---|
| How do you verify identity today before changing anything on an account in a digital channel? | An existing authentication method the agent can reuse. |
| What access does a typical service vendor get to customer records? | Concern about broad access, which favors per-action permissions. |
| What logs would you need after an incident? | Specific requirements that action-level logs can meet. |

### Member or customer service representative

| Ask | What good sounds like |
|---|---|
| What part of your day is spent chasing information customers already gave someone? | A noticeable share of time, especially on loan document follow-ups. |
| Which follow-ups do you most often lose track of? | Document chases and callbacks that slip between shifts. |
| When would you want the system to hand a conversation to you right away? | Clear triggers such as upset customers, disputes or anything unusual. |

## Qualification

**Signals the deal is real**

- A named executive owner for a specific workflow
- At least one target system with a usable API
- Measurable repeat contacts or backlog on that workflow
- Compliance willing to start a third-party review in parallel with a pilot

**Disqualifiers: walk away if**

- Wants voice as the first channel (out of scope for the first release)
- Wants the agent to make lending decisions or give financial advice
- No API access to any system the workflow needs, and no plan to add it
- Requires certifications RelayCX cannot provide today

## Top objections

| Objection | Response |
|---|---|
| Security and compliance review will take months. | Agree the review is required, since banks must manage third-party risk across the relationship life cycle [S14]; offer the due diligence pack up front and ask what the team needs first. |
| Regulators won't accept an AI agent here. | Regulators apply existing rules [S8]; design for a human path [S9] and examinable logs. Not legal advice. |
| Our core can't integrate with this. | Start with a workflow on a system that already exposes an API, and widen from there. No integration is built yet [VERIFY]. |
| Competitor D is built for credit unions and has many references [VERIFY]. | Acknowledge the references; focus on whether the workflow is completed end to end across email and SMS. |
| We already have the CRM vendor, so Competitor C is the default. | Ask where the work is actually completed; if it's in the core or loan system, compare the effort to build that there. |

## Competitive quick reference

| Competitor | Win with | Watch out for |
|---|---|---|
| Competitor D | Multistep lending tasks completed and verified across email and SMS. | Large credit union reference base and a reported hallucination guarantee [VERIFY]; answer with controls, not counter-guarantees. |
| Competitor C | Completing work in non-the CRM vendor cores and loan systems. | Bundled pricing in existing enterprise agreements. |
| Competitor A | Mid-market focus and packaged banking workflows. | Voice coverage and enterprise lending logos. |
| Competitor B | SMS continuity and regulated-institution controls. | Fintech peer logos and flexible pricing. |
| Incumbent contact center or chatbot platform | Tasks finished, not just answered. | The incumbent bundling an AI agent at low cost. |
| Build internally | Controls, logs and handoffs that are already built. | Strong internal engineering with a build mandate. |
| Maintain current processes | A cost-of-inaction view based on repeat contacts. | Merger or conversion freezes. |

## Recommended next steps

- **Workshop:** Workflow mapping session: pick one request type, map systems, controls and handoffs. _When:_ After first discovery, when a workflow and owner are named.
- **Demo:** Loan document collection storyline (DM-1 to DM-6). _When:_ When the contact center director and COO are both engaged.
- **Pilot:** Time-boxed pilot on one workflow with a baseline and success thresholds agreed up front. _When:_ Once IT confirms API access and compliance agrees to run review in parallel.

## Proof library

| Proof | Status | Source |
|---|---|---|
| Verified completion rate from a pilot | [PROOF NEEDED] |  |
| Repeat-contact baseline and change on the pilot workflow | [PROOF NEEDED] |  |
| Security and due diligence pack (no certifications claimed) | [PROOF NEEDED] |  |
| Handoff quality ratings from staff | [PROOF NEEDED] |  |
| Customer references and logos (none exist; Relay Labs is fictional) | [PROOF NEEDED] |  |
| Lending workflow template coverage list | [PROOF NEEDED] |  |

## Before you use this

- **[VERIFY]:** 3 · **[ASSUMPTION]:** 4 · **[PROOF NEEDED]:** 6

Items to verify:

- Start with a workflow on a system that already exposes an API, and widen from there. No integration is built yet [VERIFY].
- Competitor D is built for credit unions and has many references [VERIFY].
- Large credit union reference base and a reported hallucination guarantee [VERIFY]; answer with controls, not counter-guarantees.

## Sources

- **[S4]** What's Going On in Banking Research Finds AI, Crypto, and Fraud Are Top of Mind for Banking Executives in 2026, Cornerstone Advisors (2026-01-29; retrieved 2026-10-19; tier 2). https://www.crnrstone.com/press-release/cornerstone-advisors-whats-going-on-in-banking-research-finds-ai-crypto-and-fraud-are-top-of-mind-for-banking-executives-in-2026
- **[S8]** Artificial Intelligence: Use and Oversight in Financial Services (GAO-25-107197), U.S. Government Accountability Office (2025-05-19; retrieved 2026-10-19; tier 1). https://www.gao.gov/products/GAO-25-107197
- **[S9]** Chatbots in consumer finance (Issue Spotlight), Consumer Financial Protection Bureau (2023-06-06; retrieved 2026-10-19; tier 1). https://www.consumerfinance.gov/data-research/research-reports/chatbots-in-consumer-finance/
- **[S12]** FinCEN Issues Alert on Fraud Schemes Involving Deepfake Media Targeting Financial Institutions, Financial Crimes Enforcement Network (2024-11-13; retrieved 2026-10-19; tier 1). https://fincen.gov/news/news-releases/fincen-issues-alert-fraud-schemes-involving-deepfake-media-targeting-financial
- **[S13]** NCUA Releases Second Quarter 2026 Credit Union System Performance Data, National Credit Union Administration (2026-09-14; retrieved 2026-10-19; tier 1). https://ncua.gov/newsroom/press-release/2026/ncua-releases-second-quarter-2026-credit-union-system-performance-data
- **[S14]** Interagency Guidance on Third-Party Relationships: Risk Management, Federal Register (Federal Reserve, FDIC, OCC) (2023-06-09; retrieved 2026-10-19; tier 1). https://www.federalregister.gov/documents/2023/06/09/2023-12340/interagency-guidance-on-third-party-relationships-risk-management

---

_Draft generated with Industry Launch Accelerator on 2026-10-19. Verify items marked [VERIFY] before external use._
