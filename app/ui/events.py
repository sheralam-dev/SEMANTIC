'''
events.py — UI Event Handling
Purpose: connect UI with search engine.

Binds search bar → engine
Handles user interactions
Coordinates async updates

Key functions:

connect_events(window)
on_query_change(text)
on_result_selected(item)

Flow:

user types → search_bar signal
events.py calls engine.search()
results → results_view.update()

Notes:

debounce search calls
cancel previous queries if typing fast
keep UI responsive (threading/async)
'''
