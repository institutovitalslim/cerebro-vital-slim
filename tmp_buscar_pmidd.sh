#!/bin/bash
# Buscar PMID correto do paper Podder et al. sobre GLP-1 e câncer endometrial
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=Podder+GLP-1+endometrial+cancer&retmode=json&retmax=5" | python3 -m json.tool 2>/dev/null | grep -A 5 "idlist"
