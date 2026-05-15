'''
engine.py — Hybrid Search Engine
Purpose: combine fast prefix matching with semantic (vector) search.

Entry point for all queries from UI
Runs prefix search first (instant results)
Optionally runs vector search (semantic match)
Merges and ranks results

Key functions:

search(query: str, limit=100) -> list[FileResult]
merge_results(prefix_results, vector_results)
should_use_vector(query) -> bool

Flow:

normalize query
run prefix search
if needed → run vector search
merge results
rank using ranking.py
return top N
'''
