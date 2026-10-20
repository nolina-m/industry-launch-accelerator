# Industry playbook: Healthcare and life sciences

**My Product Launch · RelayCX is a fictional test product, not a real product** · Healthcare and life sciences

_Draft · Unbranded draft · Approved by PMM 2026-10-19_

## Who to target

- First: US multisite specialty practices with long new-patient waits and a central scheduling team, on a practice management system with scheduling APIs [ASSUMPTION].
- Second: outpatient provider groups with high front-desk turnover or recent vacancies (T-healthcare-life-sciences-1).
- Third: groups operating in California or Texas, where AI disclosure is already required (R-healthcare-life-sciences-3, R-healthcare-life-sciences-4).

The patient access director brings the scheduling problem to the practice administrator or COO, who signs. The medical director approves clinical boundaries and content, the IT and EHR director tests scheduling integrations, and the privacy and compliance officer runs the business associate and disclosure review and can stop the deal. Schedulers shape the champion's view [ASSUMPTION].

## Why now

- **I-healthcare-life-sciences-1:** Turnover pressure stays concentrated in front-desk and patient access roles [S23], and practice leaders name scheduling as their top AI automation target [S22].
- **I-healthcare-life-sciences-2:** Patients wait 31 days on average for a new appointment [S25]; every freed slot refilled quickly is access for someone waiting.
- **I-healthcare-life-sciences-3:** California requires AI patient communications to explain how to reach a person [S29], and Texas requires AI disclosure from January 2026 [S30].
- **I-healthcare-life-sciences-4:** The largest 2025 healthcare breach occurred at a business associate [S35], and OCR keeps enforcing risk analysis failures [S34].

## Value story by persona

| Persona | Message | Pillar |
|---|---|---|
| Practice administrator or chief operating officer | Keep scheduling moving when front-desk seats sit empty. | PL-1 |
| Patient access and scheduling director | Reschedules finished in the patient's channel of choice, booked by your rules, with no re-keying [ASSUMPTION] (fictional capability). | PL-1 |
| IT and EHR applications director | Grant scheduling access action by action, with every change logged. | PL-2 |
| Privacy and compliance officer | Configure AI disclosure, consent and minimal SMS content for every state where you see patients. | PL-2 |
| Physician lead or medical director | Clinical questions always go to your clinical staff, and scheduling just gets done. | PL-4 |
| Patient service representative or scheduler | Fewer rings for simple reschedules, and a full picture when a patient needs you. | PL-4 |

## Discovery guide

### Practice administrator or chief operating officer

| Ask | What good sounds like |
|---|---|
| How many patient access positions turned over in the past year, and what happened to phone wait times? | Specific vacancies and a visible service impact. |
| What happens to a cancelled appointment slot today? | Slots often go unfilled or are filled late by manual calls. |
| What would your physician owners need to hear before approving an AI tool at the front desk? | Concerns about clinical scope and privacy that RelayCX's boundaries address. |

### Patient access and scheduling director

| Ask | What good sounds like |
|---|---|
| What share of your scheduling requests are simple reschedules? | A large, countable share handled by phone or portal today. |
| How are appointment-type and provider rules enforced today? | Documented rules that could be configured, not tribal knowledge only. |
| Which requests must always go to a scheduler? | Clear exception categories that map to handoff rules. |

### IT and EHR applications director

| Ask | What good sounds like |
|---|---|
| Which EHR or practice management interfaces support scheduling writes today? | A named interface that supports booking or rescheduling. |
| What do you require from a vendor before granting write access? | A defined review the vendor can prepare for. |
| How do you monitor what third-party tools do in your systems? | Interest in action-level logs. |

### Privacy and compliance officer

| Ask | What good sounds like |
|---|---|
| How do you disclose AI use to patients today, if at all? | No consistent approach yet, especially across states. |
| What PHI do you allow in text messages? | A minimal-content policy that matches secure links for details. |
| How do you handle a patient who opts out of texts in one channel but not another? | A known gap that consistent consent handling would close. |

### Physician lead or medical director

| Ask | What good sounds like |
|---|---|
| What should never be said to a patient without clinical review? | Clear lines that become hard handoffs. |
| How do late cancellations affect your schedule today? | Visible gaps the provider cares about. |
| Who approves patient preparation instructions now? | An existing approval process RelayCX can follow. |

### Patient service representative or scheduler

| Ask | What good sounds like |
|---|---|
| How many of your calls are simple reschedules? | A large share of the day. |
| How do you work the waitlist today? | Manual, one-by-one calls when time allows. |
| What information do you need when a patient is handed to you? | Specific fields such as identity status and appointment details. |

## Qualification

**Signals the deal is real**

- A named owner for scheduling or patient access
- A practice management or EHR interface that supports scheduling writes
- Measurable call volume or long waits for new patients
- Privacy officer willing to review a business associate agreement in parallel with a pilot

**Disqualifiers: walk away if**

- Wants the agent to answer clinical questions or triage symptoms
- Wants voice as the first channel (out of scope for the first release)
- No scheduling interface available and no plan to add one
- Requires HIPAA certifications or audit reports RelayCX cannot provide today [ASSUMPTION] (fictional capability)

## Top objections

| Objection | Response |
|---|---|
| Competitor E already integrates with our EHR. | Integration is necessary; ask what the agent does with it across email, SMS and web chat. RelayCX's EHR integrations are proposed, not built [VERIFY]. |
| We need a business associate agreement and a security review. | Agree, and offer the due diligence pack and business associate terms up front. |
| Will patient data train your models? | Data use belongs in the contract; Relay Labs' policy must be written down before launch [VERIFY]. |
| AI makes things up. | Answers are limited to approved content, actions are verified, and clinical questions go to staff. No zero-error claim. |
| This will replace our front desk. | It handles routine requests so staff can focus on patients who need them; it does not replace staff. |

## Competitive quick reference

| Competitor | Win with | Watch out for |
|---|---|---|
| Competitor E | Inbound requests completed across email, SMS and web chat with shared context. | Deep EHR integrations and near-identical 'notifying to completing' messaging [VERIFY]. |
| Competitor A | Mid-market practices and a packaged patient access edition. | Healthcare customer references [VERIFY] and voice coverage. |
| Competitor C | Practices that don't run the CRM vendor. | Groups already on a the CRM vendor health platform [VERIFY]. |
| Incumbent contact center or chatbot platform | Completing reschedules rather than sending reminders. | Existing reminder tools seen as good enough. |
| Maintain current processes | Cost of front-desk turnover and unfilled slots. | Budget locked until the next fiscal year. |

## Recommended next steps

- **Workshop:** Scheduling rules and handoff mapping session with the patient access director and medical director. _When:_ After first discovery, when scheduling is confirmed as the target.
- **Demo:** Appointment rescheduling storyline (DM-1 to DM-6). _When:_ When the administrator and patient access director are both engaged.
- **Pilot:** Pilot at one location or specialty with a call-volume and fill-rate baseline agreed up front. _When:_ Once IT confirms a scheduling interface and privacy agrees to review terms in parallel.

## Proof library

| Proof | Status | Source |
|---|---|---|
| Verified completion rate from a pilot | [PROOF NEEDED] |  |
| Repeat-contact baseline and change on the pilot workflow | [PROOF NEEDED] |  |
| Security and due diligence pack (no certifications claimed) | [PROOF NEEDED] |  |
| Handoff quality ratings from staff | [PROOF NEEDED] |  |
| Customer references and logos (none exist; Relay Labs is fictional) | [PROOF NEEDED] |  |
| Example AI disclosure configuration by state | [PROOF NEEDED] |  |

## Before you use this

- **[VERIFY]:** 5 · **[ASSUMPTION]:** 4 · **[PROOF NEEDED]:** 6

Items to verify:

- Integration is necessary; ask what the agent does with it across email, SMS and web chat. RelayCX's EHR integrations are proposed, not built [VERIFY].
- Data use belongs in the contract; Relay Labs' policy must be written down before launch [VERIFY].
- Deep EHR integrations and near-identical 'notifying to completing' messaging [VERIFY].
- Healthcare customer references [VERIFY] and voice coverage.
- Groups already on a the CRM vendor health platform [VERIFY].

## Sources

- **[S22]** Automatic for the people: AI for front-office access, MGMA (2026-02-11; retrieved 2026-10-19; tier 2). https://mgma.com/mgma-stat/automatic-for-the-people-ai-for-front-office-access
- **[S23]** Stabilized but not solved: Staff turnover in 2026, MGMA (2026-05-28; retrieved 2026-10-19; tier 2). https://www.mgma.com/mgma-stat/stabilized-but-not-solved-staff-turnover-in-2026
- **[S25]** Average patient appointment wait time is 31 days in 2025, TechTarget PatientEngagementHIT (2025-05-27; retrieved 2026-10-19; tier 2). https://www.techtarget.com/patientengagement/news/366624919/Average-patient-appointment-wait-time-is-31-days-in-2025
- **[S29]** California Requires Disclaimers for Health Care Providers' AI-Generated Patient Communications, ArentFox Schiff (undated; retrieved 2026-10-19; tier 2). https://www.afslaw.com/perspectives/alerts/california-requires-disclaimers-health-care-providers-ai-generated-patient
- **[S30]** Texas Enacts Comprehensive AI Governance Laws, Holland & Knight (2025-06-27; retrieved 2026-10-19; tier 2). https://www.hklaw.com/en/insights/publications/2025/06/texas-enacts-comprehensive-ai-governance-laws
- **[S34]** OCR announces 11th and 12th Risk Analysis Initiative enforcement actions, McDonald Hopkins (undated; retrieved 2026-10-19; tier 2). https://www.mcdonaldhopkins.com/insights/news/ocr-announces-risk-analysis-initiative-enforcement-actions
- **[S35]** Largest Healthcare Data Breaches of 2025, HIPAA Journal (undated; retrieved 2026-10-19; tier 2). https://www.hipaajournal.com/largest-healthcare-data-breaches-of-2025/

---

_Draft generated with Industry Launch Accelerator on 2026-10-19. Verify items marked [VERIFY] before external use._
