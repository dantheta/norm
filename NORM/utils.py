

def encode_where(kw):
    clauses = []
    for k in kw:
        if isinstance(kw[k], tuple):
            k_cmp = kw[k][0]
            value = kw[k][1]
        else:
            k_cmp = '='
            value = kw[k]
        clauses.append( "%s %s %%(%s)s" %(k, k_cmp, k) )
    return ' AND '.join(clauses)
