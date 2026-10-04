# Packing Solutions

This is the online supplement for the paper

T. Berthold, D. Kamp, G. Mexi, S. Pokutta, I. Polik. Out-of-the-Box Global Optimization for Packing Problems: New Models and Improved Solutions. Submitted to the Journal of Global Optimization (JoGO), 2026.

## Problems

### Circle Packing in Unit Square (`square/`)

Pack n circles with variable radii into the unit square, maximizing the sum of radii.

- Instances: n in {1, ..., 60}
- Directory: `n{n}/`
- Files: `circlepacking_n{n}.txt`, `circlepacking_n{n}.pdf`
- Solution format: Line 1: `n`, Line 2: `sum_radii`, Lines 3+: `x_i y_i r_i` per circle

### Circle Packing in Rectangle (`rectangle/`)

Pack n circles with variable radii into a rectangle of perimeter 4, maximizing the sum of radii.

- Instances: n in {1, ..., 60}
- Directory: `n{n}/`
- Files: `rectangle_n{n}.txt`, `rectangle_n{n}.pdf`
- Solution format: Line 1: `n`, Line 2: `sum_radii`, Lines 3+: `x_i y_i r_i` per circle (rectangle width inferred as 1 + max(x_i + r_i) - max(y_i + r_i) clamped to [0, 1])

### Polygon Packing (`polygon/`)

Pack n regular m-gons with unit circumradius into a regular l-gon, minimizing the circumradius R of the outer polygon.

- Instances: l, m in {3, ..., 7}, n in {1, ..., 30}
- Directory: `l{l}/m{m}/n{n}/`
- Files: `polygon_n{n}_m{m}_l{l}.txt`, `polygon_n{n}_m{m}_l{l}.pdf`
- Solution format: Line 1: `l m n`, Line 2: `R`, Lines 3+: `x_i y_i theta_i` per inner polygon

### Platonic Solid Packing (`platonic/`)

Pack n Platonic solids of type m with unit circumradius into a Platonic solid of type l, minimizing the circumradius R of the outer solid.

Solid types: 1 = Tetrahedron, 2 = Octahedron, 3 = Cube, 4 = Icosahedron, 5 = Dodecahedron.

- Instances: l, m in {1, ..., 5}, n in {1, ..., 30}
- Directory: `l{l}/m{m}/n{n}/`
- Files: `platonic_n{n}_m{m}_l{l}.txt`, `platonic_n{n}_m{m}_l{l}.pdf`, `platonic_n{n}_m{m}_l{l}.html`
- Solution format: Line 1: `l m n`, Line 2: `R`, Lines 3+: `x_i y_i z_i theta_i iota_i kappa_i` per inner solid (ZYX rotation angles)

## Results Tables

Each problem directory contains a `results.dat` file listing all instances with rounded objective values:
- Square and Rectangle: sum of radii floored to 5 decimal places (maximization)
- Polygon and Platonic: circumradius ceiled to 5 decimal places (minimization)
