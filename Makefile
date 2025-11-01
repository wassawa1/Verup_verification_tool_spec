.PHONY: help setup-iverilog setup-python clean clean-all

help:
	@echo "Verification Pipeline Setup"
	@echo ""
	@echo "Targets:"
	@echo "  setup-iverilog  - Setup Verilog verification"
	@echo "  setup-python    - Setup Python verification"
	@echo "  clean           - Remove generated files"
	@echo "  clean-all       - Remove all copied files"

setup-iverilog:
	@$(MAKE) -s setup-impl TYPE=iverilog NAME=iVerilog

setup-python:
	@$(MAKE) -s setup-impl TYPE=python NAME=Python

setup-impl:
	@mkdir -p scripts testcases
	@cp -r examples/$(TYPE)/scripts/* scripts/
	@cp -r examples/$(TYPE)/testcases/* testcases/
	@echo "✅ $(NAME) setup complete. Run: python3 run_pipeline.py"

clean:
	@rm -rf sim_new sim_old tmp reports

clean-all: clean
	@rm -rf scripts testcases
