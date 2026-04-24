#!/bin/bash
cd /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica
python3 scripts/memory_search.py --query "GLP-1 cancer endometrial progestina" --top-k 3 2>&1
