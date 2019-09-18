r"""
Orlik-Terao Algebras
"""

#*****************************************************************************
#       Copyright (C) 2019 Travis Scrimshaw <tcscrims at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.combinat.free_module import CombinatorialFreeModule
from sage.categories.algebras import Algebras
from sage.matrix.constructor import matrix
from sage.sets.family import Family

class OrlikTeraoAlgebra(CombinatorialFreeModule):
    r"""
    An Orlik-Terao algebra.

    Let `R` be a commutative ring. Let `M` be a matroid with ground set
    `X` with some fixed ordering and representation `A = (a_x)_{x \in X}`
    (so `a_x` is a (column) vector). Let `C(M)` denote the set of circuits
    of `M`. Let `P` denote the quotient algebra `R[e_x \mid x \in X] /
    \langle e_x^2 \rangle`, i.e., the polynomial algebra with squares being
    zero. The *Orlik-Terao ideal* `J(M)` is the ideal of `P` generated by

    .. MATH::

        \partial e_S := \sum_{i=1}^t (-1)^i \chi(S \setminus \{j_i\})
        e_{S \setminus \{j_i\}}

    for all `S = \left\{ j_1 < j_2 < \cdots < j_t \right\} \in C(M)`,
    where `\chi(T)` is defined as follows. If `T` is linearly dependent,
    then `\chi(T) = 0`. Otherwise, let `T = \{x_1 < \cdots < x_{|T|}\}`,
    and for every flat `F` of `M`, choose a basis `\Theta_F`.
    Then define `\chi(T) = \det(b_1, \dotsc, b_{|T|})`, where `b_i` is
    `a_{x_i}` expressed in the basis `\Theta_F`.

    It is easy to see that `\partial e_S \in J(M)` not only for circuits
    `S`, but also for any dependent set `S` of `M`. Moreover, every
    dependent set `S` of `M` satisfies `e_S \in J(M)`.

    The *Orlik-Terao algebra* `A(M)` is the quotient `E / J(M)`.
    This is a graded finite-dimensional commutative `R`-algebra.
    The non-broken circuit (NBC) sets of `M` (that is, the subsets
    of `X` containing :meth:`no broken circuit
    <sage.matroids.matroid.Matroid.no_broken_circuits_sets>`
    of `M`) form a basis of `A(M)`. (Recall that a
    :meth:`broken circuit <sage.matroids.matroid.Matroid.broken_circuit>`
    of `M` is defined to be the result of removing
    the smallest element from a circuit of `M`.)

    In the current implementation, the basis of `A(M)` is indexed by the
    NBC sets, which are implemented as frozensets.

    INPUT:

    - ``R`` -- the base ring
    - ``M`` -- the defining matroid
    - ``ordering`` -- (optional) an ordering of the ground set

    EXAMPLES:

    We create the Orlik-Terao algebra of the wheel matroid `W(3)`
    and do some basic computations::

        sage: M = matroids.Wheel(3)
        sage: OT = M.orlik_terao_algebra(QQ)
        sage: OT.dimension()
        24
        sage: G = OT.algebra_generators()
        sage: sorted(map(sorted, M.broken_circuits()))
        [[1, 3], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4], [2, 5], [4, 5]]
        sage: G[1] * G[2] * G[3]
        OT{0, 1, 2} + OT{0, 2, 3}
        sage: G[1] * G[4] * G[5]
        -OT{0, 1, 4} - OT{0, 1, 5} - OT{0, 3, 4} - OT{0, 3, 5}

    We create an example of a linear matroid and do a basic computation::

        sage: R = ZZ['t'].fraction_field()
        sage: t = R.gen()
        sage: mat = matrix(R, [[1-3*t/(t+2), t, 5], [-2, 1, 3/(7-t)]])
        sage: M = Matroid(mat)
        sage: OT = M.orlik_terao_algebra()
        sage: G = OT.algebra_generators()
        sage: G[1] * G[2]
        ((2*t^3-12*t^2-12*t-14)/(8*t^2-19*t-70))*OT{0, 1}
         + ((10*t^2-44*t-146)/(-8*t^2+19*t+70))*OT{0, 2}

    REFERENCES:

    - [OT1994]_
    - [FL2001]_
    - [CF2005]_
    """
    @staticmethod
    def __classcall_private__(cls, R, M, ordering=None):
        """
        Normalize input to ensure a unique representation.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: from sage.algebras.orlik_terao import OrlikTeraoAlgebra
            sage: OT1 = algebras.OrlikTerao(QQ, M)
            sage: OT2 = OrlikTeraoAlgebra(QQ, M, ordering=(0,1,2,3,4,5))
            sage: OT3 = OrlikTeraoAlgebra(QQ, M, ordering=[0,1,2,3,4,5])
            sage: OT1 is OT2 and OT2 is OT3
            True
        """
        if ordering is None:
            ordering = sorted(M.groundset())
        return super(OrlikTeraoAlgebra, cls).__classcall__(cls, R, M, tuple(ordering))

    def __init__(self, R, M, ordering=None):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: TestSuite(OT).run(elements=OT.basis())

            sage: M = matroids.CompleteGraphic(4).ternary_matroid()
            sage: OT = M.orlik_terao_algebra(GF(3)['t'])
            sage: TestSuite(OT).run(elements=OT.basis())

            sage: H = hyperplane_arrangements.Catalan(4).cone()
            sage: M = H.matroid()
            sage: OT = M.orlik_terao_algebra()
            sage: OT.dimension()
            672
            sage: TestSuite(OT).run(elements=list(OT.basis()))

        We check on the matroid associated to the graph with 3 vertices and
        2 edges between each vertex::

            sage: G = Graph([[1,2],[1,2],[2,3],[2,3],[1,3],[1,3]], multiedges=True)
            sage: M = Matroid(G).regular_matroid()
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: elts = OT.some_elements() + list(OT.basis())
            sage: TestSuite(OT).run(elements=elts)
        """
        self._M = M
        self._sorting = {x: i for i, x in enumerate(ordering)}

        # set up the dictionary of broken circuits
        self._broken_circuits = dict()
        for c in self._M.circuits():
            L = sorted(c, key=self._sorting.__getitem__)
            self._broken_circuits[frozenset(L[1:])] = L[0]

        cat = Algebras(R).FiniteDimensional().Commutative().WithBasis().Graded()
        CombinatorialFreeModule.__init__(self, R, M.no_broken_circuits_sets(ordering),
                                         prefix='OT', bracket='{',
                                         sorting_key=self._sort_key,
                                         category=cat)

    def _sort_key(self, x):
        r"""
        Return the key used to sort the terms.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT._sort_key(frozenset({1, 2}))
            (-2, [1, 2])
            sage: OT._sort_key(frozenset({0, 1, 2}))
            (-3, [0, 1, 2])
            sage: OT._sort_key(frozenset({}))
            (0, [])
        """
        return (-len(x), sorted(x))

    def _repr_term(self, m):
        r"""
        Return a string representation of the basis element indexed by ``m``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT._repr_term(frozenset([0]))
            'OT{0}'
        """
        return "OT{{{}}}".format(', '.join(str(t) for t in sorted(m)))

    def _latex_term(self, m):
        r"""
        Return a string representation of the basis element indexed by ``m``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT._latex_term(frozenset([0, 1]))
            'e_{\\left\\{0, 1\\right\\}}'
            sage: OT._latex_term(frozenset())
            'e_{\\emptyset}'
        """
        if not m:
            return "e_{\\emptyset}"

        from sage.misc.latex import latex
        from sage.sets.set import Set
        return "e_{{{}}}".format(latex(Set(sorted(m))))

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: M.orlik_terao_algebra(QQ)
            Orlik-Terao algebra of Wheel(3): Regular matroid of rank 3
             on 6 elements with 16 bases over Rational Field
        """
        return "Orlik-Terao algebra of {} over {}".format(self._M, self.base_ring())

    @cached_method
    def one_basis(self):
        r"""
        Return the index of the basis element corresponding to `1`
        in ``self``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT.one_basis() == frozenset([])
            True
        """
        return frozenset({})

    @cached_method
    def algebra_generators(self):
        r"""
        Return the algebra generators of ``self``.

        These form a family indexed by the ground set `X` of `M`. For
        each `x \in X`, the `x`-th element is `e_x`.

        EXAMPLES::

            sage: M = matroids.Whirl(2)
            sage: OT = M.orlik_terao_algebra()
            sage: OT.algebra_generators()
            Finite family {0: OT{0}, 1: OT{1}, 2: OT{2}, 3: OT{3}}

            sage: M = matroids.named_matroids.Fano()
            sage: OT = M.orlik_terao_algebra()
            sage: OT.algebra_generators()
            Finite family {'a': OT{a}, 'b': OT{b}, 'c': OT{c}, 'd': OT{d},
                           'e': OT{e}, 'f': OT{f}, 'g': OT{g}}

            sage: M = matroids.named_matroids.NonFano()
            sage: OT = M.orlik_terao_algebra(GF(3)['t'])
            sage: OT.algebra_generators()
            Finite family {'a': OT{a}, 'b': OT{b}, 'c': OT{c}, 'd': OT{d},
                           'e': OT{e}, 'f': OT{f}, 'g': OT{g}}
        """
        return Family(sorted(self._M.groundset()),
                      lambda i: self.subset_image(frozenset([i])))

    def degree_on_basis(self, m):
        r"""
        Return the degree of the basis element indexed by ``m``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT.degree_on_basis(frozenset([1]))
            1
            sage: OT.degree_on_basis(frozenset([0, 2, 3]))
            3
        """
        return len(m)

    ## Multiplication

    def product_on_basis(self, a, b):
        r"""
        Return the product in ``self`` of the basis elements
        indexed by ``a`` and ``b``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT.product_on_basis(frozenset([2]), frozenset([3,4]))
            OT{0, 1, 2} + OT{0, 1, 4} + OT{0, 2, 3} + OT{0, 3, 4}

        ::

            sage: G = OT.algebra_generators()
            sage: prod(G)
            0
            sage: G[2] * G[4]
            OT{1, 2} + OT{1, 4}
            sage: G[3] * G[4] * G[2]
            OT{0, 1, 2} + OT{0, 1, 4} + OT{0, 2, 3} + OT{0, 3, 4}
            sage: G[2] * G[3] * G[4]
            OT{0, 1, 2} + OT{0, 1, 4} + OT{0, 2, 3} + OT{0, 3, 4}
            sage: G[3] * G[2] * G[4]
            OT{0, 1, 2} + OT{0, 1, 4} + OT{0, 2, 3} + OT{0, 3, 4}

        TESTS:

        Let us check that `e_{s_1} e_{s_2} \cdots e_{s_k} = e_S` for any
        subset `S = \{ s_1 < s_2 < \cdots < s_k \}` of the ground set::

            sage: G = Graph([[1,2],[1,2],[2,3],[3,4],[4,2]], multiedges=True)
            sage: M = Matroid(G).regular_matroid()
            sage: E = M.groundset_list()
            sage: OT = M.orlik_terao_algebra(ZZ)
            sage: G = OT.algebra_generators()
            sage: import itertools
            sage: def test_prod(F):
            ....:     LHS = OT.subset_image(frozenset(F))
            ....:     RHS = OT.prod([G[i] for i in sorted(F)])
            ....:     return LHS == RHS
            sage: all( test_prod(F) for k in range(len(E)+1)
            ....:                   for F in itertools.combinations(E, k) )
            True
        """
        if not a:
            return self.basis()[b]
        if not b:
            return self.basis()[a]

        if not a.isdisjoint(b):
            return self.zero()

        # Since a is disjoint from b, we can just multiply and look
        return self.subset_image(b.union(a))

    @cached_method
    def subset_image(self, S):
        r"""
        Return the element `e_S` of ``self`` corresponding to a
        subset ``S`` of the ground set of the defining matroid.

        INPUT:

        - ``S`` -- a frozenset which is a subset of the ground set of `M`

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra()
            sage: BC = sorted(M.broken_circuits(), key=sorted)
            sage: for bc in BC: (sorted(bc), OT.subset_image(bc))
            ([1, 3], OT{0, 1} + OT{0, 3})
            ([1, 4, 5], -OT{0, 1, 4} - OT{0, 1, 5} - OT{0, 3, 4} - OT{0, 3, 5})
            ([2, 3, 4], OT{0, 1, 2} + OT{0, 1, 4} + OT{0, 2, 3} + OT{0, 3, 4})
            ([2, 3, 5], -OT{0, 2, 3} + OT{0, 3, 5})
            ([2, 4], OT{1, 2} + OT{1, 4})
            ([2, 5], -OT{0, 2} + OT{0, 5})
            ([4, 5], -OT{3, 4} - OT{3, 5})

            sage: M4 = matroids.CompleteGraphic(4).ternary_matroid()
            sage: OT = M4.orlik_terao_algebra()
            sage: OT.subset_image(frozenset({2,3,4}))
            OT{0, 2, 3} + 2*OT{0, 3, 4}

        An example of a custom ordering::

            sage: G = Graph([[3, 4], [4, 1], [1, 2], [2, 3], [3, 5], [5, 6], [6, 3]])
            sage: M = Matroid(G).regular_matroid()
            sage: s = [(5, 6), (1, 2), (3, 5), (2, 3), (1, 4), (3, 6), (3, 4)]
            sage: sorted([sorted(c) for c in M.circuits()])
            [[(1, 2), (1, 4), (2, 3), (3, 4)],
             [(3, 5), (3, 6), (5, 6)]]
            sage: OT = M.orlik_terao_algebra(QQ, ordering=s)
            sage: OT.subset_image(frozenset([]))
            OT{}
            sage: OT.subset_image(frozenset([(1,2),(3,4),(1,4),(2,3)]))
            0
            sage: OT.subset_image(frozenset([(2,3),(1,2),(3,4)]))
            OT{(1, 2), (2, 3), (3, 4)}
            sage: OT.subset_image(frozenset([(1,4),(3,4),(2,3),(3,6),(5,6)]))
            -OT{(1, 2), (1, 4), (2, 3), (3, 6), (5, 6)}
             - OT{(1, 2), (1, 4), (3, 4), (3, 6), (5, 6)}
             + OT{(1, 2), (2, 3), (3, 4), (3, 6), (5, 6)}
            sage: OT.subset_image(frozenset([(1,4),(3,4),(2,3),(3,6),(3,5)]))
            -OT{(1, 2), (1, 4), (2, 3), (3, 5), (5, 6)}
             + OT{(1, 2), (1, 4), (2, 3), (3, 6), (5, 6)}
             - OT{(1, 2), (1, 4), (3, 4), (3, 5), (5, 6)}
             + OT{(1, 2), (1, 4), (3, 4), (3, 6), (5, 6)}
             + OT{(1, 2), (2, 3), (3, 4), (3, 5), (5, 6)}
             - OT{(1, 2), (2, 3), (3, 4), (3, 6), (5, 6)}

        TESTS::

            sage: G = Graph([[1,2],[1,2],[2,3],[2,3],[1,3],[1,3]], multiedges=True)
            sage: M = Matroid(G).regular_matroid()
            sage: sorted([sorted(c) for c in M.circuits()])
            [[0, 1], [0, 2, 4], [0, 2, 5], [0, 3, 4],
             [0, 3, 5], [1, 2, 4], [1, 2, 5], [1, 3, 4],
             [1, 3, 5], [2, 3], [4, 5]]
            sage: OT = M.orlik_terao_algebra()
            sage: OT.subset_image(frozenset([]))
            OT{}
            sage: OT.subset_image(frozenset([1, 2, 3]))
            0
            sage: OT.subset_image(frozenset([1, 3, 5]))
            0
            sage: OT.subset_image(frozenset([1, 2]))
            OT{0, 2}
            sage: OT.subset_image(frozenset([3, 4]))
            -OT{0, 2} + OT{0, 4}
            sage: OT.subset_image(frozenset([1, 5]))
            OT{0, 4}

            sage: G = Graph([[1,2],[1,2],[2,3],[3,4],[4,2]], multiedges=True)
            sage: M = Matroid(G).regular_matroid()
            sage: sorted([sorted(c) for c in M.circuits()])
            [[0, 1], [2, 3, 4]]
            sage: OT = M.orlik_terao_algebra(QQ)
            sage: OT.subset_image(frozenset([]))
            OT{}
            sage: OT.subset_image(frozenset([1, 3, 4]))
            -OT{0, 2, 3} + OT{0, 2, 4}

        We check on a non-standard ordering::

            sage: M = matroids.Wheel(3)
            sage: o = [5,4,3,2,1,0]
            sage: OT = M.orlik_terao_algebra(QQ, ordering=o)
            sage: BC = sorted(M.broken_circuits(ordering=o), key=sorted)
            sage: for bc in BC: (sorted(bc), OT.subset_image(bc))
            ([0, 1], -OT{0, 3} + OT{1, 3})
            ([0, 1, 4], OT{0, 3, 5} + OT{0, 4, 5} - OT{1, 3, 5} - OT{1, 4, 5})
            ([0, 2], OT{0, 5} - OT{2, 5})
            ([0, 2, 3], OT{0, 3, 5} - OT{2, 3, 5})
            ([1, 2], -OT{1, 4} + OT{2, 4})
            ([1, 2, 3], OT{1, 3, 5} + OT{1, 4, 5} - OT{2, 3, 5} - OT{2, 4, 5})
            ([3, 4], -OT{3, 5} - OT{4, 5})
        """
        if not isinstance(S, frozenset):
            raise ValueError("S needs to be a frozenset")
        R = self.base_ring()
        mone = -R.one()
        for bc in self._broken_circuits:
            if bc.issubset(S):
                i = self._broken_circuits[bc]
                if i in S:
                    # ``S`` contains not just a broken circuit, but an
                    # actual circuit; then `e_S = 0`.
                    return self.zero()
                # Now, reduce ``S``, and build the result ``r``
                r = self.zero()
                Si = S.union({i})
                C = bc.union({i})
                lc = self._chi(bc)
                for ind, j in enumerate(sorted(bc, key=self._sorting.__getitem__)):
                    coeff = self._chi(C.difference({j}))
                    if coeff:
                        r += mone**ind * R(coeff / lc) * self.subset_image(Si.difference({j}))
                return r
        else: # So ``S`` is an NBC set.
            return self.monomial(S)

    @cached_method
    def _flat_module(self, F):
        r"""
        Return a vector space for the flat ``F``.

        EXAMPLES::

            sage: M = matroids.Wheel(3)
            sage: OT = M.orlik_terao_algebra()
            sage: OT._flat_module(list(M.flats(2))[0])
            Vector space of degree 3 and dimension 2 over Rational Field
            Basis matrix:
            [1 0 0]
            [0 1 0]
        """
        rep_vecs = self._M.representation_vectors()
        return matrix(self.base_ring().fraction_field(), [rep_vecs[x] for x in F]).row_module()

    @cached_method
    def _chi(self, X):
        r"""
        Return `\chi(X)` for an independent set ``X``.

        EXAMPLES::

            sage: H = hyperplane_arrangements.Catalan(2).cone()
            sage: M = H.matroid()
            sage: OT = M.orlik_terao_algebra()
            sage: [OT._chi(X) for X in sorted(M.independent_sets(), key=sorted)]
            [1, -1, -1, -1, -2, 1, -1, -1, 1, 1, 1]
        """
        R = self.base_ring()
        assert self._M.is_independent(X)
        #if not self._M.is_independent(X):
        #    return R.zero()
        M = self._M
        rep_vecs = M.representation_vectors()
        V = self._flat_module(M.closure(X))
        X = sorted(X, key=self._sorting.__getitem__)
        return R(matrix([V.echelon_coordinates(rep_vecs[x]) for x in X]).det())

