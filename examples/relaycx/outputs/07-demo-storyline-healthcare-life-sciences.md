# Demo storyline: Healthcare and life sciences

**My Product Launch · RelayCX is a fictional test product, not a real product** · Healthcare and life sciences

_Draft · Unbranded draft · Approved by PMM 2026-10-19_

> A spec for whoever builds the demo. Capabilities marked [VERIFY] must be confirmed with the product team before anything is built.

## Scenario

A fictional multisite dermatology practice, Riverbend Dermatology Partners, gets a patient request on its website chat to reschedule a specialist appointment. This is an illustration with fictional data, not a customer story.

## Who's in the room

| Persona | What they watch for |
|---|---|
| Patient access and scheduling director | Watches whether scheduling rules are followed and the reschedule finishes without staff. |
| Practice administrator or chief operating officer | Watches for front-desk capacity and patient experience. |
| Privacy and compliance officer | Watches verification, SMS content and AI disclosure. |
| Physician lead or medical director | Watches how clinical questions are handled. |

## The aha moment

**DM-2:** The reschedule is booked within the practice's own appointment-type rules and confirmed by the patient, with no staff touch [ASSUMPTION] (fictional capability). It answers the patient access director's biggest doubt about automation.

## Moments

| # | Moment | Pillar | Pain addressed |
|---|---|---|---|
| DM-1 | A patient asks to move an appointment | PL-1 | Patient service representative or scheduler: Phones ring nonstop with simple reschedules while patients wait in the lobby. |
| DM-2 | Booked by your rules | PL-2 | Patient access and scheduling director: Reschedule requests come in by phone, portal, text and chat, and my team re-keys them into the scheduling system. |
| DM-3 | Confirmed by text, details kept secure | PL-2 | Privacy and compliance officer: Text messages can expose PHI, and billing texts don't get the same TCPA treatment as reminders. |
| DM-4 | The freed slot | PL-1 | Practice administrator or chief operating officer: Patients wait weeks for appointments while cancelled slots go unfilled. |
| DM-5 | A clinical question goes to staff | PL-4 | Physician lead or medical director: I don't want an AI giving patients anything that looks like clinical advice. |
| DM-6 | What happened, on one screen | PL-3 | IT and EHR applications director: I'm expected to evaluate AI tools without clear criteria for safety or access. |

### DM-1: A patient asks to move an appointment

- **Tell:** Today this request becomes a phone call or a portal message a scheduler works later.
- **Show:** The patient opens web chat, sees an AI disclosure and a way to reach staff, and asks to reschedule. RelayCX verifies the patient through the practice's method.
- **Tell back:** The patient is verified and informed before anything happens.
- **Talk track:** The first thing the patient sees is that this is AI and how to reach a person. Then verification.
- **To verify:** [VERIFY] confirm configurable AI disclosure by state and channel; [VERIFY] confirm the product can reuse the practice's patient verification method

### DM-2: Booked by your rules  (aha)

- **Tell:** Scheduling rules by appointment type and provider are why practices hesitate to automate [ASSUMPTION].
- **Show:** RelayCX checks permitted appointment types and available slots, offers options, gets the patient's confirmation and books the change.
- **Tell back:** The reschedule is done, within the practice's rules, with no re-keying [ASSUMPTION] (fictional capability).
- **Talk track:** The agent only offers slots this appointment type allows. Nothing is booked until the patient confirms.
- **To verify:** [VERIFY] confirm the product can read appointment-type rules and book through a practice management or EHR interface

### DM-3: Confirmed by text, details kept secure

- **Tell:** Texts are convenient but can expose health information.
- **Show:** RelayCX sends a minimal SMS confirmation with a secure link to approved preparation instructions.
- **Tell back:** The patient gets what they need without PHI in the text.
- **Talk track:** The text says only what it must. Prep instructions sit behind a secure link, and only provider-approved content is used.
- **To verify:** [VERIFY] confirm minimal SMS templates and secure links to approved content

### DM-4: The freed slot

- **Tell:** The original slot is now open while new patients wait weeks.
- **Show:** The scheduling view shows the original slot released for booking.
- **Tell back:** Freed capacity is visible right away.
- **Talk track:** That slot is back on the schedule immediately. Whether it gets refilled automatically is a separate workflow.
- **To verify:** [VERIFY] confirm whether the product can work a waitlist to refill freed slots; not in the brief

### DM-5: A clinical question goes to staff

- **Tell:** Patients will ask clinical questions in any channel.
- **Show:** The patient asks whether to stop a medication before the visit. RelayCX doesn't answer; it transfers to clinical staff with the conversation summary and appointment details.
- **Tell back:** Clinical judgment stays with clinicians.
- **Talk track:** This is the line we never cross. The agent hands off, and staff see everything already done.
- **To verify:** [VERIFY] confirm detection of clinical questions and handoff to a staff queue

### DM-6: What happened, on one screen

- **Tell:** IT and privacy need to see what the AI did in their systems.
- **Show:** The reporting view shows completed, blocked and failed actions, the handoff, and the audit log for this patient. All numbers are demo data.
- **Tell back:** Every access and action is logged and reviewable.
- **Talk track:** This is the record your IT and privacy teams would review. The numbers are demo data, not results.
- **To verify:** [VERIFY] confirm the reporting view and audit log exist as shown

## 5-minute version

DM-1 → DM-2 → DM-5. Disclosure, rules-based booking, then the clinical handoff for the medical director.

## 20-minute version

DM-1 → DM-2 → DM-3 → DM-4 → DM-5 → DM-6. Pause after DM-3 for privacy and after DM-6 for IT.

## Demo data needed

- Fictional patient profile with verified contact details
- Fictional appointment with a dermatology provider
- Fictional appointment-type rules and open slots
- Provider-approved fictional preparation instructions
- Fictional reporting data

## Environment

- Demo practice management or EHR scheduling sandbox, or a mock API
- Web chat and SMS sandbox accounts
- Patient verification mock
- RelayCX demo tenant with AI disclosure and clinical handoff rules configured

## Before you use this

- **[VERIFY]:** 7 · **[ASSUMPTION]:** 3 · **[PROOF NEEDED]:** 0

Items to verify:

- [VERIFY] confirm configurable AI disclosure by state and channel
- [VERIFY] confirm the product can reuse the practice's patient verification method
- [VERIFY] confirm the product can read appointment-type rules and book through a practice management or EHR interface
- [VERIFY] confirm minimal SMS templates and secure links to approved content
- [VERIFY] confirm whether the product can work a waitlist to refill freed slots; not in the brief
- [VERIFY] confirm detection of clinical questions and handoff to a staff queue
- [VERIFY] confirm the reporting view and audit log exist as shown

## Sources

No sources cited.

---

_Draft generated with Industry Launch Accelerator on 2026-10-19. Verify items marked [VERIFY] before external use._
