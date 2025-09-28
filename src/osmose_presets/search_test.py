def evaluate_search(search_term, target_string):
   # Split the search term by " OR " to handle the lowest precedence operator.
   or_clauses = [clause.strip() for clause in search_term.split(" OR ")]
   # Evaluate each "AND" clause independently.
   # Using a generator expression for efficiency.
   and_results = (all(term.strip() in target_string for term in clause.split(" AND ")) for clause in or_clauses)

   # Step 3: The final result is TRUE if any of the "AND" clauses were a match.
   return any(and_results)


if __name__ == "__main__":
   # --- Example Usage ---
   target_text = "The quick brown fox jumps over the lazy dog."

   # Test 1: Multiple ANDs
   search1 = "quick AND brown AND fox"
   print(f'Query: "{search1}" -> Match: {evaluate_search(search1, target_text)}')

   # Test 2: Multiple ORs
   search2 = "cat OR dog OR rabbit"
   print(f'Query: "{search2}" -> Match: {evaluate_search(search2, target_text)}')

   # Test 3: Combination of AND and OR (AND has precedence)
   search3 = "quick AND brown OR cat AND mouse"
   print(f'Query: "{search3}" -> Match: {evaluate_search(search3, target_text)}')

   # Test 4: Another combination (first part matches)
   search4 = "lazy AND dog OR cat"
   print(f'Query: "{search4}" -> Match: {evaluate_search(search4, target_text)}')

   # Test 5: No match
   search5 = "mouse AND rabbit OR unicorn"
   print(f'Query: "{search5}" -> Match: {evaluate_search(search5, target_text)}')
