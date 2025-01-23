from __future__ import annotations

max_iter = 4

dom = {
    'A': 400,
    'B': 500,
    'D': None,
    'F': None,
}

init_relations = {
    'R1': {
        'card': 1000.0,
        'columns': [
            ["A", 4, 200.0],
            ["F", 4, 50.0],
        ]
    },
    'R2': {
        'card': 1000.0,
        'columns': [
            ["A", 4, 40.0],
            ["B", 4, 100.0],
        ]
    },
    'R3': {
        'card': 2000.0,
        'columns': [
            ["B", 4, 400.0],
            ["D", 4, 50.0],
        ]
    },
    'R4': {
        'card': 1000.0,
        'columns': [
            ["B", 4, 200.0],
            ["F", 4, 50.0],
        ]
    },
}

dom_ = {
    'A': 1000,
    'B': 500,
    'C': 100,
    'D': None,
    'E': None,
    'F': None,
}

init_relations_ = {
    'R': {
        'card': 5000.0,
        'columns': [
            ["A", 3, 1000.0],
            ["B", 4, 500.0],
            ["E", 25, 5000.0],
        ]
    },
    'S': {
        'card': 1000.0,
        'columns': [
            ["B", 4, 200.0],
            ["C", 2, 100.0],
            ["D", 20, 1000.0],
        ]
    },
    'U': {
        'card': 200.0,
        'columns': [
            ["A", 3, 200.0],
            ["C", 2, 50.0],
        ]
    },
}


def cost(s: Relation, col: str) -> float:
    return s.columns[col].size * s.columns[col].val


def effect(r: Relation, s: Relation, col: str) -> float:
    return r.card * s.columns[col].sf


def revenue(r: Relation, s: Relation, col: str) -> float:
    return r.card - effect(r, s, col)


class Column:
    def __init__(self, name: str, size: float, val: float):
        self.name = name
        self.size = size
        self.val = val
        self.sf = val / dom[name] if name in dom and dom[name] is not None else 0


class Relation:
    def __init__(self, name: str, card: float, columns: list[Column]):
        self.name = name
        self.card = card
        self.columns: dict[str, Column] = {column.name: column for column in columns}

    def semi_join(self, s: Relation, col: str) -> Relation:
        columns = []
        r = effect(self, s, col)
        for c, column in self.columns.items():
            if c != col:
                m = self.columns[c].val
                if r < m / 2:
                    val = r
                elif m / 2 <= r < 2 * m:
                    val = (r + m) / 3
                else:
                    val = m
                columns.append(Column(c, column.size, val))
            elif c in s.columns:
                val = self.columns[c].sf * s.columns[c].val
                columns.append(Column(c, column.size, val))

        return Relation(self.name + "'", r, columns)

    @classmethod
    def print_header(cls):
        columns = " | ".join([f"{d}.size | {d}.val  | {d}.sf  " for d in dom])
        print(f" {'':>5} | {'CARD':>6} | {columns}")

    def print(self):
        columns = []
        for d in dom:
            if d in self.columns:
                c = self.columns[d]
                columns.append(f"{c.size:>6} | {c.val:>6} | {c.sf:>6}")
            else:
                columns.append(f"       |        |       ")
        print(f" {self.name:>5} | {self.card:>6} | {' | '.join(columns)}")


class SemiJoin:
    def __init__(self, r: Relation, s: Relation, col: str):
        self.r = r
        self.s = s
        self.col = col
        self.cost = cost(s, col)
        self.effect = effect(r, s, col)
        self.revenue = revenue(r, s, col)
        self.relation = r.semi_join(s, col)

    def used_in_join(self, r: Relation, s: Relation) -> bool:
        return r.name.strip("'") == self.r.name.strip("'") and s.name.strip("'") == self.s.name.strip("'")

    @classmethod
    def print_header(cls):
        print(f" R    | COL | S     | COST    | EFFECT  | REVENUE")

    def print(self):
        print(
            f"{self.r.name:>5} | {self.col:>3} | {self.s.name:>5} | {self.cost:>7} | {self.effect:>7} | {self.revenue:>7}")


def used_in_joins(joins: list[SemiJoin], r: Relation, s: Relation) -> tuple[bool, SemiJoin | None]:
    for join in joins:
        if join.used_in_join(r, s):
            join.r = r
            return True, join
    return False, None


def main():
    relations = [
        Relation(r, init_relations[r]['card'],
                 [Column(c[0], c[1], c[2]) for c in init_relations[r]['columns']]
                 ) for r in init_relations
    ]

    prev_joins = []

    print("Initial state")
    Relation.print_header()
    for r in relations:
        r.print()

    i = 0
    while i < max_iter:
        i += 1
        print(f"\nIteration #{i}")
        semi_joins = []

        for r in relations:
            for s in relations:
                is_used_in_joins, join = used_in_joins(prev_joins, r, s)
                if r.name != s.name and not is_used_in_joins:
                    for r_col in r.columns:
                        for s_col in s.columns:
                            if r_col == s_col and dom[r_col] is not None:
                                semi_joins.append(SemiJoin(r, s, r_col))
                elif r.name != s.name and is_used_in_joins:
                    join.revenue = 0
                    join.effect = join.relation.card
                    semi_joins.append(join)

        print("\nSemi joins")

        SemiJoin.print_header()
        msj: SemiJoin | None = None

        for sj in sorted(semi_joins, key=lambda a: a.r.name):
            if msj is None or msj.revenue < sj.revenue:
                msj = sj
            sj.print()

        prev_joins.append(msj)

        print("\nBest semi join")

        SemiJoin.print_header()
        msj.print()

        print("\nRelations")

        relations.remove(msj.r)
        relations.append(msj.relation)

        Relation.print_header()
        for r in relations:
            r.print()


if __name__ == '__main__':
    main()
