# T21-safe Path B helpers (RUO / clinical_validation=false / PHI-false)
# CODEX-099: hospital demo wrappers.

.PHONY: hospital-demo hospital-demo-pack help

OUT_DIR ?= /tmp/t21-hospital-demo
PACK_DIR ?= /tmp/t21-hospital-demo-partner-pack

help:
	@echo "Targets:"
	@echo "  make hospital-demo       # demo → HTML showcard → partner zip chain"
	@echo "  make hospital-demo-pack  # pack only (runs demo if report missing)"
	@echo "Vars: OUT_DIR=$(OUT_DIR) PACK_DIR=$(PACK_DIR)"

hospital-demo:
	bash scripts/run_hospital_demo_chain.sh "$(OUT_DIR)" "$(PACK_DIR)"

hospital-demo-pack:
	bash scripts/pack_hospital_demo_partner.sh "$(OUT_DIR)" "$(PACK_DIR)"
