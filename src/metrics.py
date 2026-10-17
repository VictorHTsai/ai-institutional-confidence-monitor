"""Quantity and endpoint valuation identities. Not transaction-level cash flows."""
import math

def finite(values):
    if any(v is None or not math.isfinite(v) for v in values):
        raise ValueError('Missing or non-finite inputs must not become zero')

def endpoint_decomposition(previous_shares,current_shares,previous_prices,current_prices):
    lengths={len(x) for x in (previous_shares,current_shares,previous_prices,current_prices)}
    if len(lengths)!=1 or not previous_shares:raise ValueError('Same nonempty constituent universe required')
    finite([v for a in (previous_shares,current_shares,previous_prices,current_prices) for v in a])
    if any(x<0 for x in previous_shares+current_shares) or any(x<=0 for x in previous_prices+current_prices):
        raise ValueError('Nonnegative long shares and positive prices required')
    delta=sum((b-a)*p for a,b,p in zip(previous_shares,current_shares,current_prices))
    price=sum(a*(p1-p0) for a,p0,p1 in zip(previous_shares,previous_prices,current_prices))
    value=sum(b*p1-a*p0 for a,b,p0,p1 in zip(previous_shares,current_shares,previous_prices,current_prices))
    if not math.isclose(value,delta+price,rel_tol=1e-10,abs_tol=.01):raise ValueError('Valuation reconciliation failed')
    return {'estimated_position_change_dollars':delta,'price_effect_dollars':price,'valuation_change_dollars':value}

def accumulation(levels,minimum_meaningful_peak):
    if not levels or minimum_meaningful_peak<=0:raise ValueError('Positive materiality threshold required')
    finite(levels)
    if any(x<=0 for x in levels):raise ValueError('Positive comparable position-stock levels required')
    peak=max(0,max(levels)-levels[0]);a=levels[-1]-levels[0]
    return {'remaining_accumulation_pct':100*a/peak if peak>minimum_meaningful_peak else None,
            'position_stock_drawdown_pct':100*(levels[-1]/max(levels)-1),
            'accumulation_since_baseline':a,'peak_accumulation':peak}

def resolve_chain(filings):
    """Input ordered by filing date, amendment number, accession. Return row states.
    Reject unanchored additions and unknown amendment types instead of guessing.
    Each row must already have a unique accession/row key.
    """
    state=None
    for f in filings:
        if f['form']=='13F-NT' or f['form']=='13F-NT/A':raise ValueError('Notice requires scope reconciliation')
        if not f['amended']:
            if state is not None:raise ValueError('Multiple original filings require review')
            state=list(f['rows'])
        elif f['type'].upper()=='RESTATEMENT':state=list(f['rows'])
        elif f['type'].upper()=='NEW HOLDINGS':
            if state is None:raise ValueError('Additive amendment without original')
            state.extend(f['rows'])
        else:raise ValueError('Unknown amendment type')
    if state is None:raise ValueError('No usable filing')
    return state
