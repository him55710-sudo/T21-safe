# T21-safe Path B helpers (RUO / clinical_validation=false / PHI-false)
# CODEX-099: hospital demo wrappers.

.PHONY: hospital-demo hospital-demo-pack proxy-hyp-benches proxy-hyp-pack help

OUT_DIR ?= /tmp/t21-hospital-demo
PACK_DIR ?= /tmp/t21-hospital-demo-partner-pack
PROXY_OUT_DIR ?= /tmp/t21-proxy-hyp-benches
PROXY_PACK_DIR ?= /tmp/t21-proxy-hyp-partner-pack

help:
	@echo "Targets:"
	@echo "  make hospital-demo       # demo → HTML showcard → partner zip chain"
	@echo "  make hospital-demo-pack  # pack incl. MEETING_ONEPAGER_PROXY_v0.1_KR.md (runs demo if report missing)"
	@echo "  make proxy-hyp-benches  # HYP-01/03/07 PROXY local runner (CODEX-104)"
	@echo "  make proxy-hyp-pack     # PROXY HYP partner zip incl. MEETING_ONEPAGER_PROXY_v0.1_KR.md (CODEX-108)"
	@echo "Vars: OUT_DIR=$(OUT_DIR) PACK_DIR=$(PACK_DIR) PROXY_OUT_DIR=$(PROXY_OUT_DIR) PROXY_PACK_DIR=$(PROXY_PACK_DIR)"

hospital-demo:
	bash scripts/run_hospital_demo_chain.sh "$(OUT_DIR)" "$(PACK_DIR)"

hospital-demo-pack:
	bash scripts/pack_hospital_demo_partner.sh "$(OUT_DIR)" "$(PACK_DIR)"

proxy-hyp-benches:
	bash scripts/run_proxy_hyp_benches.sh "$(PROXY_OUT_DIR)"

proxy-hyp-pack:
	bash scripts/pack_proxy_hyp_partner.sh "$(PROXY_OUT_DIR)" "$(PROXY_PACK_DIR)"
