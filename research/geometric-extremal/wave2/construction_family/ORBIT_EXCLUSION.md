# A bounded-difference explanation of the 111/41 witness

This is a rigorously bounded construction mechanism, not a novelty or asymptotic claim.

Let P_s be the filled nine-gon P(s,1) from `NINEGON_PROOF.md`. Its vertices give

```
0 ≤ 2a+b ≤ 6s+2,
0 ≤ a ≤ 4s+1.
```

For every difference v=p−q between two included points, therefore
`|2v_a+v_b|≤6s+2` and `|v_a|≤4s+1`.
The polygon has D3 symmetry. Its difference body P_s−P_s has the same rotational/reflection symmetries, together with central symmetry v→−v. A 120° rotation combined with a 180° rotation generates a 60° rotation. Thus the difference body has D6 symmetry. Applying this group to the two linear-functional bounds gives the exact necessary conditions

```
|a|, |b|, |a+b| ≤ 4s+1,
|2a+b|, |a+2b|, |a-b| ≤ 6s+2.
```

In particular, the vector `(3s+1,1)` violates the first diagonal bound by one:
`2(3s+1)+1=6s+3`. Its squared norm is

```
Q_s=(3s+1)²+(3s+1)+1=9s²+9s+3=N(s,1).
```

The entire orbit under the 12 dihedral transformations is excluded from the difference body. **This excludes that orbit, not every representation of Q_s.** If the same squared norm has a different lattice orbit, it may still occur. Indeed the tested s=5,7,8 configurations contain Q_s through other representations. No general primality hypothesis or formula for distance counts is asserted here.

At s=3, complete exact representation enumeration shows norm111 has precisely the 12-vector orbit of `(10,1)`. Completeness needs only `|a|,|b|≤sqrt(4·111/3)<13`, obtained by completing a square in `a²+ab+b²` and by coordinate symmetry. Every such representation is excluded.

There is also a compact independent upper certificate for the complete palette. Enumerate all integer pairs in the box [-13,13]² that satisfy

```
|a+b|≤13,
max(|2a+b|,|a+2b|,|a-b|)≤20,
(a,b)≠(0,0).
```

This gives 420 nonzero difference vectors and **41 distinct squared norms**, maximum127. The norm set agrees with the full 6,105-pair enumeration of the actual111-point construction. Thus the linear bounds alone establish at most41 distances; the pair histogram establishes that every listed norm is attained. The exact vectors and orbit audit are in `difference_envelope_s3.json`.

Compared with the first41 positive representable triangular-lattice norms (whose last value is112), this palette removes **111** and adds **127**. Among all45 representable norms up to127, it also omits117,121,124. This is a precise instance of geometric support clipping excluding an expensive norm orbit while retaining a larger but compatible orbit; the broader strategy of substituting rare distances already occurs in prior literature and is not claimed new.

A certificate-sized enumeration independent of the point-pair loop is:

```python
norms = {
    a*a+a*b+b*b
    for a in range(-13,14) for b in range(-13,14)
    if (a or b) and abs(a+b)<=13
    and max(abs(2*a+b),abs(a+2*b),abs(a-b))<=20
}
assert len(norms)==41
```
