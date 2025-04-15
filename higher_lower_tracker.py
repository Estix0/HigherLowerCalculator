import streamlit as st
import colorsys

SUITS = ['\U00002660', '\U00002665', '\U00002666', '\U00002663']
CARD_ORDER_FULL = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

st.set_page_config(page_title="Higher / Lower Odds", layout="wide")
st.title("🃏 Higher / Lower Odds Tracker")

# Sidebar options
st.sidebar.markdown("<h1>Deck Settings</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<span style='font-size:15px;'>Number of Decks</span>", unsafe_allow_html=True)
num_decks = st.sidebar.slider("Decks", 1, 10, 1, label_visibility="hidden")
st.sidebar.markdown("---")

use_custom_deck = st.sidebar.checkbox("Use a custom deck")
if use_custom_deck:        
    custom_deck_input = st.sidebar.text_input(
        "Custom Deck (comma-separated, e.g., 2,3,4,5,6,J,Q,K,A)", 
        value=",".join(CARD_ORDER_FULL)
    )
    custom_deck = [card.strip().upper() for card in custom_deck_input.split(",") if card.strip()]
    CARD_ORDER = custom_deck
else:
    start_card = st.sidebar.selectbox("Start Card", CARD_ORDER_FULL, index=0)
    end_card = st.sidebar.selectbox("End Card", CARD_ORDER_FULL, index=len(CARD_ORDER_FULL) - 1)

    start_index = CARD_ORDER_FULL.index(start_card)
    end_index = CARD_ORDER_FULL.index(end_card)
    CARD_ORDER = CARD_ORDER_FULL[start_index:end_index+1]

CARD_VALUE_MAP = {card: i + 2 for i, card in enumerate(CARD_ORDER)}

st.sidebar.markdown("---")

use_custom_suits = st.sidebar.checkbox("Use custom suits")

if use_custom_suits:
    custom_suits_input = st.sidebar.text_input(
        "Custom Suits (comma-separated, e.g., ♠,♥,♦,♣ or S,H,D,C)", 
        value="♠,♥,♦,♣"
    )
    SUITS = [s.strip() for s in custom_suits_input.split(",") if s.strip()]
else:
    SUITS = ['♠', '♥', '♦', '♣']


# Initialize state
if 'seen' not in st.session_state or \
   set(k[0] for k in st.session_state.seen.keys()) != set(CARD_ORDER) or \
   set(k[1] for k in st.session_state.seen.keys()) != set(SUITS):
    st.session_state.seen = {(card, suit): 0 for suit in SUITS for card in CARD_ORDER}
if 'last_clicked' not in st.session_state:
    st.session_state.last_clicked = None

st.sidebar.markdown("---")
st.sidebar.markdown("Reset Seen Cards:")
if st.sidebar.button("🔄"):
    for key in st.session_state.seen:
        st.session_state.seen[key] = 0
    st.session_state.last_clicked = None

# Get background color

def get_bg_color(n):
    if n == 0:
        return "white"
    hue = (n - 1) / 10.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

left, right = st.columns([3, 1])

with left:
    for suit in SUITS:
        st.markdown(f"### {suit}")
        cols = st.columns(len(CARD_ORDER))
        for i, card in enumerate(CARD_ORDER):
            key = (card, suit)
            count = st.session_state.seen[key]
            color = get_bg_color(count)
            with cols[i]:
                button_html = f"""<style> .stButton>button {{ width: 60px; height: 50px;}} </style>"""
                st.markdown(button_html, unsafe_allow_html=True)
                if st.button(f"{card}", key=f"{card}_{suit}"):
                    st.session_state.seen[key] = (count + 1) % (num_decks + 1)
                    st.session_state.last_clicked = key
                    st.rerun()
                st.markdown(f"<div style='width: 60px; height: 50px; background-color: {color}; border-radius: 8px; padding-top: 8px; text-align: center; font-weight: bold;'><big>{count if count > 0 else ''}<big></div>", unsafe_allow_html=True)

# Odds calculator

def calculate_odds(current_card, seen_counts, per_card_max, valid_cards):
    cur_val = CARD_VALUE_MAP[current_card]
    higher = lower = equal = total = 0

    for (card, suit), count in seen_counts.items():
        if card not in valid_cards:
            continue
        val = CARD_VALUE_MAP[card]
        remaining = max(0, per_card_max - count)
        total += remaining
        if val > cur_val:
            higher += remaining
        elif val < cur_val:
            lower += remaining
        elif val == cur_val:
            equal += remaining

    high_pct = (higher / total) * 100 if total else 0
    low_pct = (lower / total) * 100 if total else 0
    equal_pct = (equal / total) * 100 if total else 0
    return high_pct, low_pct, equal_pct

# Suit chance calculator
def calculate_suit_chances(seen_counts, per_card_max, valid_cards):
    suit_totals = {s: 0 for s in SUITS}
    total = 0
    for (card, suit), count in seen_counts.items():
        if card not in valid_cards:
            continue
        remaining = max(0, per_card_max - count)
        suit_totals[suit] += remaining
        total += remaining
    chances = {s: (suit_totals[s] / total * 100 if total else 0) for s in SUITS}
    return chances

# Show odds
with right:
    if st.session_state.last_clicked:
        card, suit = st.session_state.last_clicked
        st.markdown(f"#### Last Clicked Card: **{suit} {card}**")
        high, low, equal = calculate_odds(card, st.session_state.seen, num_decks, CARD_ORDER)
        suit_chances = calculate_suit_chances(st.session_state.seen, num_decks, CARD_ORDER)

        st.markdown(f"##### 🔼 Higher: `{high:.2f}%`")
        st.markdown(f"##### 🔽 Lower: `{low:.2f}%`")
        st.markdown(f"##### 🟰 Equal: `{equal:.2f}%`")

        st.markdown("#### Suit Probabilities:")
        for s in SUITS:
            st.markdown(f"##### {s}  :  `{suit_chances[s]:.2f}%`")
    else:
        st.info("Click a card to calculate odds.")

# Seen card summary
st.markdown("---")
st.markdown("### 📊 Seen Card Summary")
total_seen = sum(st.session_state.seen[key] for key in st.session_state.seen if key[0] in CARD_ORDER)
st.markdown(f"**Total cards seen:** {total_seen}")
for card in CARD_ORDER:
    per_suit = [st.session_state.seen[(card, s)] for s in SUITS]
    if any(per_suit):
        st.markdown(f"- {card}: {dict(zip(SUITS, per_suit))}")
