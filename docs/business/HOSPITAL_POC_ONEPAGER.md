# Hospital PoC One-Pager — T21 Research Node

**Status:** DRAFT scaffold · Founder placeholder · Path B / RUO / Shadow  
**Lang:** EN + KR · **Do not email** until Founder approves  
**Related:** `docs/business/research-node-one-pager.md` (analyst draft)

---

## What / 하는 일

**EN:** Local-first research software that helps a hospital organize, quality-check, and reproducibly analyze perioperative biosignals for Down syndrome (T21) anesthesia/sedation **research**. Raw data stays hospital-owned.

**KR:** 병원 **내부**에서 T21 마취·진정 **연구용** 생체신호를 정리·품질검사·재현 분석하기 위한 **로컬 연구 소프트웨어**. 원자료는 병원 소유.

| | |
| --- | --- |
| Where | Hospital/research workstation or approved LAN |
| Inputs | ECG, PPG, BP, SpO2, EtCO2/resp (+ EEG/BIS if available), event timestamps |
| Outputs | QC reports, aligned timelines, local research export (non-PHI by default) |

---

## Not-what / 하지 않는 일

- Real-time clinical alerts or “early diagnosis”
- Arrest / bradycardia / hypotension **prediction** claims
- Dose, drug, or treatment recommendations
- Pump / ventilator / EHR write or closed-loop control
- Treating public **non-DS** bench scores as **DS clinical validation**

---

## Banned phrases (examples)

> “AI predicts DS anesthesia risk / prevents adverse events / diagnoses bradycardia early.”  
> “Approved monitor / SaMD cleared / safe for routine DS anesthesia in any clinic.”

See `docs/safety/PROHIBITED_CLAIMS.md`, Constitution Path B.

---

## Founder placeholder

- [ ] Target site / PI — `FOUNDER_TO_FILL`
- [ ] PoC success definition (feasibility, not prediction) — `FOUNDER_TO_FILL`
- [ ] Contact channel & send/no-send — `FOUNDER_TO_FILL`

**Recommended line:** “Research-use, local software to make T21 perioperative signal studies reproducible — not a bedside alarm product.”
