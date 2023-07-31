from time import perf_counter


from bcls.boolean import (
    Var,
    minimal_cnf,
)

benchmark_terms = []
benchmark_terms.append(
    (
        Var("g")
        & (
            (
                (
                    (~Var("c") & ~Var("f") & Var("b") & Var("a"))
                    & (Var("d") & ~Var("g"))
                    & (Var("c") & ~Var("c") & ~Var("c"))
                )
                | Var("f")
            )
            | ((Var("b") & (Var("b") & ~Var("d") & ~Var("g"))) | ~Var("b") | ~Var("h"))
            | Var("c")
            | ~Var("g")
        )
        & (
            Var("b")
            & (
                (
                    (Var("a") | Var("b") | Var("e"))
                    & (~Var("f") & ~Var("g"))
                    & (Var("a") & Var("a") & ~Var("d"))
                    & (Var("g") | ~Var("e") | ~Var("d"))
                )
                & ((Var("g") | Var("g")) & Var("f"))
            )
        )
    )
    | (
        (
            ~Var("a")
            & (
                ~Var("g")
                | Var("f")
                | (
                    ~Var("b")
                    | (~Var("f") & Var("g") & Var("a") & ~Var("d"))
                    | (Var("h") | ~Var("c"))
                    | (Var("g") | Var("h") | ~Var("e") | ~Var("f"))
                )
            )
            & ~Var("g")
            & (Var("b") | ~Var("e"))
        )
        | (
            (
                Var("f")
                | ((Var("f") & ~Var("a") & Var("a")) & ~Var("c"))
                | (
                    Var("h")
                    & (~Var("f") & Var("d") & Var("b") & ~Var("b"))
                    & (Var("d") | Var("g"))
                )
            )
            & (
                (
                    (Var("a") & ~Var("g") & Var("c"))
                    | (Var("a") & Var("a") & Var("f") & ~Var("b"))
                )
                & ~Var("b")
            )
            & (
                (
                    (~Var("e") | ~Var("c") | Var("g") | Var("h"))
                    | (~Var("d") | ~Var("h") | ~Var("a"))
                    | (~Var("a") & Var("d") & Var("h"))
                    | (~Var("d") | Var("d"))
                )
                | (
                    (Var("d") & Var("h"))
                    & (~Var("h") | ~Var("h"))
                    & (Var("f") & Var("f") & ~Var("b") & Var("h"))
                    & Var("a")
                )
            )
        )
        | (
            (
                ((~Var("e") & ~Var("d") & Var("a")) | ~Var("d"))
                & (~Var("c") | (Var("f") & ~Var("g") & Var("e") & ~Var("f")))
                & (
                    (~Var("a") & ~Var("f") & ~Var("c") & ~Var("d"))
                    | (~Var("b") & ~Var("f"))
                    | (~Var("b") & ~Var("h") & ~Var("a") & ~Var("h"))
                    | (Var("a") & ~Var("d") & ~Var("a"))
                )
            )
            & (
                (
                    (~Var("e") | Var("c") | ~Var("f") | Var("a"))
                    | (~Var("a") & Var("c") & Var("d") & ~Var("h"))
                    | Var("a")
                )
                & ((~Var("g") | Var("d")) | Var("b") | (~Var("a") & Var("a")))
                & Var("d")
                & (
                    Var("g")
                    & ~Var("g")
                    & ~Var("b")
                    & (~Var("g") | Var("b") | ~Var("g"))
                )
            )
            & (
                (
                    ~Var("f")
                    | (~Var("a") & ~Var("g"))
                    | (~Var("h") & ~Var("h") & Var("b"))
                )
                | ~Var("e")
            )
        )
    )
    | Var("c")
)
benchmark_terms.append(
    ~Var("x13")
    & ~Var("x1")
    & (
        (
            (
                (Var("x12") & Var("x1"))
                | (
                    (~Var("x1") & ~Var("x2"))
                    & (~Var("x3") & Var("x3") & ~Var("x1") & Var("x3"))
                )
                | (~Var("x5") | (Var("x3") | ~Var("x12")))
                | (
                    (Var("x3") & Var("x1") & ~Var("x4") & ~Var("x11"))
                    & (~Var("x9") | Var("x7") | Var("x6"))
                    & (~Var("x7") | Var("x13"))
                    & ~Var("x8")
                )
            )
            & ~Var("x9")
            & Var("x7")
            & ~Var("x11")
        )
        | (
            (
                (
                    (Var("x13") & Var("x1"))
                    | Var("x8")
                    | (Var("x10") & ~Var("x2") & Var("x8"))
                )
                | Var("x11")
                | (~Var("x11") & (~Var("x9") | Var("x10")) & (Var("x2") & ~Var("x3")))
            )
            | ~Var("x13")
            | (Var("x1") & ~Var("x0") & ~Var("x10"))
            | (
                (
                    (~Var("x13") | ~Var("x5") | ~Var("x8"))
                    & (~Var("x12") | Var("x6") | Var("x13") | ~Var("x6"))
                    & (~Var("x7") & ~Var("x9"))
                    & (Var("x8") & Var("x7") & Var("x4"))
                )
                | ((Var("x3") & ~Var("x10") & Var("x12")) & Var("x9") & Var("x12"))
                | ~Var("x12")
                | ~Var("x10")
            )
        )
        | (
            (
                (Var("x13") & ~Var("x9"))
                | (
                    Var("x3")
                    & (~Var("x10") | ~Var("x7"))
                    & Var("x13")
                    & (Var("x0") & ~Var("x8"))
                )
                | ~Var("x7")
            )
            | (
                (
                    (Var("x11") | ~Var("x7") | ~Var("x8"))
                    & (~Var("x12") | ~Var("x2") | ~Var("x4") | ~Var("x3"))
                )
                | (
                    (~Var("x8") | Var("x0") | ~Var("x7") | Var("x1"))
                    | ~Var("x1")
                    | ~Var("x12")
                    | (Var("x3") | ~Var("x12"))
                )
                | Var("x4")
                | ((~Var("x4") | Var("x5") | Var("x7") | Var("x3")) & Var("x5"))
            )
            | (
                (
                    Var("x1")
                    & (Var("x13") & Var("x5"))
                    & (~Var("x6") | Var("x2") | Var("x9") | Var("x7"))
                )
                | (
                    ~Var("x9")
                    | Var("x3")
                    | (Var("x1") & Var("x6") & Var("x1") & ~Var("x2"))
                    | (Var("x4") | ~Var("x6") | ~Var("x8"))
                )
                | (
                    ~Var("x5")
                    & (Var("x13") | ~Var("x8") | Var("x1"))
                    & (~Var("x1") & ~Var("x11"))
                )
            )
            | (
                (
                    (~Var("x11") & ~Var("x1") & Var("x13") & ~Var("x1"))
                    & (~Var("x12") | ~Var("x12") | Var("x8"))
                    & Var("x8")
                    & Var("x10")
                )
                | ~Var("x0")
                | Var("x9")
            )
        )
        | (
            ~Var("x4")
            | (Var("x2") | (~Var("x9") | ~Var("x3")))
            | Var("x13")
            | (
                (
                    (Var("x13") & Var("x9") & Var("x3"))
                    & ~Var("x11")
                    & (Var("x10") | ~Var("x8") | Var("x1"))
                )
                & Var("x9")
                & (Var("x5") & (~Var("x3") & ~Var("x10") & ~Var("x10")) & Var("x5"))
                & ~Var("x4")
            )
        )
    )
)
benchmark_terms.append(((Var("A") & ~Var("B")) | Var("C")) & (~Var("C") | ~Var("A")))
benchmark_terms.append((Var("x7") | Var("x4")) & Var("x3") & ~Var("x8"))
benchmark_terms.append(
    (
        Var("x2")
        & (
            (~Var("x4") & ~Var("x4"))
            | (~Var("x11") | Var("x1") | Var("x9"))
            | Var("x7")
        )
        & (
            (~Var("x3") | ~Var("x7") | Var("x7") | ~Var("x12"))
            | (~Var("x10") | Var("x11") | Var("x1") | Var("x5"))
            | (Var("x1") & Var("x8") & ~Var("x10"))
        )
        & ((~Var("x12") & ~Var("x2") & Var("x13")) & Var("x5"))
    )
    | ~Var("x1")
    | (
        ~Var("x8")
        | (
            (~Var("x2") & Var("x1") & ~Var("x4"))
            & (~Var("x4") | ~Var("x3") | ~Var("x12"))
            & (Var("x10") | ~Var("x7") | ~Var("x4") | Var("x12"))
        )
        | (
            (~Var("x5") & Var("x3") & ~Var("x1"))
            & (Var("x8") & ~Var("x10"))
            & (~Var("x12") | Var("x13"))
            & (~Var("x2") & ~Var("x13"))
        )
    )
    | (
        (
            Var("x9")
            & (~Var("x4") & ~Var("x13"))
            & (~Var("x3") & ~Var("x5") & ~Var("x3") & ~Var("x9"))
            & (Var("x12") | ~Var("x13") | Var("x13"))
        )
        | (
            (Var("x10") | Var("x5"))
            & (~Var("x1") & Var("x13"))
            & (Var("x7") & Var("x12") & ~Var("x13") & Var("x12"))
            & ~Var("x4")
        )
        | (
            ~Var("x6")
            | (Var("x8") & ~Var("x12") & ~Var("x4"))
            | (Var("x2") & Var("x11") & ~Var("x0"))
            | (~Var("x7") | Var("x9"))
        )
        | ~Var("x3")
    )
)


def main(term_nr: int = 1, output: bool = True) -> float:
    term = benchmark_terms[term_nr]
    if output:
        print(term)
    timer = perf_counter()
    cnf = minimal_cnf(term)
    if output:
        print(cnf)
    return perf_counter() - timer


if __name__ == "__main__":
    main()
