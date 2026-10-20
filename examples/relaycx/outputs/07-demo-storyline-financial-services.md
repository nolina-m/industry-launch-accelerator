# Demo storyline: Financial services

**My Product Launch · RelayCX is a fictional test product, not a real product** · Financial services

_Draft · Unbranded draft · Approved by PMM 2026-10-19_

> A spec for whoever builds the demo. Capabilities marked [VERIFY] must be confirmed with the product team before anything is built.

## Scenario

A fictional mid-market credit union, Lakeshore Community Credit Union, is processing a member's auto loan. The member emails about outstanding documents, uploads them, and later texts to ask whether they arrived. This is an illustration with fictional data, not a customer story.

## Who's in the room

| Persona | What they watch for |
|---|---|
| Contact center and service operations director | Watches whether the request finishes without a rep and what the handoff looks like. |
| Chief Operating Officer | Watches for staff time saved and control over what the agent can do. |
| Chief Risk and Compliance Officer | Watches for verification, approval rules and the audit trail. |
| Chief Information Security Officer | Watches identity verification and permissions. |

## The aha moment

**DM-3:** The member switches from email to SMS and the agent picks up the same request, re-verifies and checks the system of record. It shows the context continuity the contact center director says is missing today.

## Moments

| # | Moment | Pillar | Pain addressed |
|---|---|---|---|
| DM-1 | The member asks what's missing | PL-1 | Member or customer service representative: Chasing missing loan documents means repeated emails and calls that pull me off live contacts. |
| DM-2 | A secure upload, not attachments | PL-2 | Chief Information Security Officer: Vendors want broad access to customer records when they need only a few actions. |
| DM-3 | Same request, different channel | PL-1 | Contact center and service operations director: Customers start in one channel and finish in another, and my team asks them to repeat everything. |
| DM-4 | Receipt is not approval | PL-2 | Chief Risk and Compliance Officer: Examiners apply existing rules to AI, so I have to prove an agent won't trap customers or mishandle disputes. |
| DM-5 | A request that needs a person | PL-4 | Contact center and service operations director: Our chatbot answers questions but can't finish anything, so its conversations land in my queue anyway. |
| DM-6 | What happened, on one screen | PL-3 | Chief Risk and Compliance Officer: Every new AI vendor adds third-party risk work, monitoring and evidence I have to keep current. |

### DM-1: The member asks what's missing

- **Tell:** Today a loan specialist reads the email, looks up the checklist and writes back, often a day later.
- **Show:** The member's email arrives. RelayCX identifies the intent, asks the member to verify identity through the credit union's existing method, then retrieves the document checklist.
- **Tell back:** The member knows exactly what's missing in minutes, and nobody on staff touched it.
- **Talk track:** Here's the email your loan team gets every day. Watch what happens before any loan details are shared: the member verifies first.
- **To verify:** [VERIFY] confirm the product can reuse the institution's existing identity verification method; [VERIFY] confirm the product can read a document checklist from a loan servicing system

### DM-2: A secure upload, not attachments

- **Tell:** Members often email sensitive documents as attachments.
- **Show:** RelayCX replies with a secure upload link instead of asking for attachments, and logs the request.
- **Tell back:** Sensitive documents go through a secure, authenticated flow.
- **Talk track:** The agent never asks for documents in email. It sends a secure link, and the action is logged.
- **To verify:** [VERIFY] confirm the product can generate secure upload links

### DM-3: Same request, different channel  (aha)

- **Tell:** Two days later the member texts instead of emailing, and today that starts from zero.
- **Show:** The member texts 'Did you get my documents?'. RelayCX links the SMS to the same request after re-verification, checks receipt and updates the service case.
- **Tell back:** The member didn't repeat anything, and the case record is current.
- **Talk track:** New channel, same request. The agent knows the history, re-verifies, and checks the system of record.
- **To verify:** [VERIFY] confirm the product can link an SMS conversation to an earlier email request; [VERIFY] confirm the product can check document receipt and update a service case

### DM-4: Receipt is not approval

- **Tell:** Compliance worries an AI will say something that sounds like a loan decision.
- **Show:** RelayCX confirms the documents were received and that staff review is pending. It does not say anything about approval.
- **Tell back:** The agent stays inside what it's allowed to say, every time.
- **Talk track:** Notice the exact wording: received, pending staff review. The agent can't imply approval because it isn't permitted to.
- **To verify:** [VERIFY] confirm response wording can be constrained by configured rules

### DM-5: A request that needs a person

- **Tell:** Some requests should always go to staff.
- **Show:** The member asks for a late fee to be waived. Fee adjustments require staff approval, so RelayCX hands off with a summary, identity status, actions taken and the open request [ASSUMPTION] (fictional capability).
- **Tell back:** The rep starts where the agent stopped.
- **Talk track:** Fee adjustments are on the approval list. Here is exactly what the rep sees when the conversation arrives.
- **To verify:** [VERIFY] confirm handoff into the institution's contact center or CRM queue

### DM-6: What happened, on one screen

- **Tell:** Leaders and examiners need to see what the AI did.
- **Show:** The reporting view shows completed, blocked and failed actions, the handoff, and the audit log for this member's request. All numbers are demo data.
- **Tell back:** Every action is attributable and reviewable.
- **Talk track:** This is the record your risk team and examiners would review. These numbers are demo data, not results.
- **To verify:** [VERIFY] confirm the reporting view and audit log export exist as shown

## 5-minute version

DM-1 → DM-3 → DM-4. Lead with the channel switch; close on 'receipt is not approval' for compliance.

## 20-minute version

DM-1 → DM-2 → DM-3 → DM-4 → DM-5 → DM-6. Pause after DM-5 for the contact center director and after DM-6 for risk and compliance.

## Demo data needed

- Fictional member profile with verified contact details
- Fictional auto loan with a three-item document checklist
- Sample fictional documents for upload
- A fictional service case record
- Fictional reporting data for the dashboard

## Environment

- Demo loan servicing system or mock API with checklist and receipt status
- Demo CRM or service case system
- Email and SMS sandbox accounts
- Identity verification mock using the institution's method
- RelayCX demo tenant with fee-adjustment approval rule configured

## Before you use this

- **[VERIFY]:** 8 · **[ASSUMPTION]:** 1 · **[PROOF NEEDED]:** 0

Items to verify:

- [VERIFY] confirm the product can reuse the institution's existing identity verification method
- [VERIFY] confirm the product can read a document checklist from a loan servicing system
- [VERIFY] confirm the product can generate secure upload links
- [VERIFY] confirm the product can link an SMS conversation to an earlier email request
- [VERIFY] confirm the product can check document receipt and update a service case
- [VERIFY] confirm response wording can be constrained by configured rules
- [VERIFY] confirm handoff into the institution's contact center or CRM queue
- [VERIFY] confirm the reporting view and audit log export exist as shown

## Sources

No sources cited.

---

_Draft generated with Industry Launch Accelerator on 2026-10-19. Verify items marked [VERIFY] before external use._
