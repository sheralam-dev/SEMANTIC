'''
search_bar.py — Instant Input Field
Purpose: fast typing input with real-time search.

Text input optimized for low latency
Emits signal on every keystroke
Supports keyboard navigation (↑ ↓ enter)

Key class:

SearchBar(QLineEdit)

Signals:

text_changed(str)
enter_pressed()

Key methods:

on_text_change()
clear()

Notes:

debounce input (~20–50ms)
avoid blocking UI thread
normalize input (lowercase)
'''
