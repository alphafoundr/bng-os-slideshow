"""Add step data to checked-in exports as their records are loaded."""
if __package__:
    from .dsl import at, draw
else:
    from dsl import at, draw


def companies(ch):
    at(0, ch[7])
    at(0, ch[19], ch[25], motion="dot")
    for step, links in enumerate((
        ((6, 8, 14, 15), (3, 9, 20, 21)),
        ((5, 10, 16, 17), (2, 11, 22, 23)),
        ((4, 12, 18, None), (1, 13, 24, None)),
    )):
        for line, card, end, label in links:
            at(step + 1, ch[card])
            draw(step, ch[line], end=ch[end], target=ch[card])
            if label is not None:
                at(step, ch[label], motion="label")
    draw(4, ch[0], ch[27])
    at(5, ch[26])


def ownership_lanes(ch):
    at(0, ch[6])
    for start, branch, trunk, marks, tools in (
        (0, 5, 0, (7, 8), (9,)),
        (2, 3, 4, (10, 11), (12, 13, 14)),
        (6, 1, 2, (15, 16), (17, 18, 19)),
    ):
        draw(start, ch[branch], end=ch[marks[0]])
        at(start + 1, ch[marks[1]])
        cards = [ch[i] for i in tools]
        for i, card in enumerate(cards, start + 2):
            card["n"] = card["ch"][0]["n"].replace("Tool disc", "Tool lane")
            at(i, card)
        draw(start + 1, ch[trunk], target=cards[-1], arrival=start + len(cards) + 1,
             via=[(start + i + 2, (card["x"] + 28 - ch[trunk]["x"]) / ch[trunk]["w"], card)
                  for i, card in enumerate(cards[:-1])])


def late_sales(ch):
    at(0, ch[7])
    at(0, ch[3], motion="dot")
    for i in range(3):
        step = 1 + 2 * i
        card = at(step + 1, ch[4 + i])
        draw(step, ch[i], end=ch[8 + i], target=card)


def schedule(key, ch):
    if key == "s01":
        companies(ch)
    elif key == "s03":
        ownership_lanes(ch)
    elif key == "s05":
        late_sales(ch)
