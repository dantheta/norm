

def encode_where(kw):
    clauses = []
    values = {}
    for k in kw:
        if isinstance(kw[k], tuple):
            k_cmp = kw[k][0]
            values[k] = kw[k][1]
        else:
            k_cmp = '='
            values[k] = kw[k]
        clauses.append( "%s %s %%(%s)s" %(k, k_cmp, k) )
    return ' AND '.join(clauses), values
