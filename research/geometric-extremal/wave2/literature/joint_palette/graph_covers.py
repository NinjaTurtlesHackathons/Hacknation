"""Valid distance-class cardinality cuts from disjoint triangles and edges."""
import random
import networkx as nx

def cover_bound(g,n,seed=0):
    base=list(nx.max_weight_matching(g,maxcardinality=True));best=(n-len(base),[],base)
    triangles=[(a,b,c) for a in g for b in g[a] if a<b for c in set(g[a]).intersection(g[b]) if b<c]
    rng=random.Random(seed)
    for strategy in range(5):
        order=triangles.copy();rng.shuffle(order)
        if strategy<3:order.sort(key=lambda t:sum(g.degree(x) for x in t),reverse=(strategy==1))
        occupied=set();ts=[]
        for tri in order:
            if not occupied.intersection(tri):occupied.update(tri);ts.append(tri)
        edges=list(nx.max_weight_matching(g.subgraph(set(g)-occupied),maxcardinality=True))
        alpha=n-2*len(ts)-len(edges)
        if alpha<best[0]:best=(alpha,ts,edges)
    alpha,ts,edges=best;vertices=[v for t in ts for v in t]+[v for e in edges for v in e]
    assert len(vertices)==len(set(vertices))
    assert all(g.has_edge(a,b) and g.has_edge(a,c) and g.has_edge(b,c) for a,b,c in ts)
    assert all(g.has_edge(a,b) for a,b in edges)
    return {'alpha_upper':alpha,'triangles':ts,'edges':edges,'method':'disjoint clique cover; each forbidden-distance triangle holds at most1, edge at most1; uncovered vertices counted individually'}
