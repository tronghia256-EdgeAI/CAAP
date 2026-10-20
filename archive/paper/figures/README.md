# paper/figures/

All figures exported as **PDF** (vector) for IEEE submission quality.
PNG is acceptable only for photographs / qualitative frame captures.

## Naming convention
```
figN_short_description.pdf
```

## Required figures (TODO — create during Month 3–4)

| File | Section | Content | Tool |
|---|---|---|---|
| `fig1_pipeline_body.tex` | III | Full system pipeline with C1/C2/C3 highlighted | TikZ (included directly) |
| `fig2_context_estimator.pdf` | III.A | C1 state machine / logic diagram | Draw.io |
| `fig3_ctrv_vs_kalman.pdf` | III.B | Trajectory comparison: CTRV vs linear Kalman on real footage | Matplotlib |
| `fig4_reliability_score.pdf` | III.C | C3 dual-threshold split diagram | Draw.io |
| `fig5_qualitative_tracking.pdf` | V.C | Side-by-side: baseline vs proposed track IDs | OpenCV annotation |
| `fig6_failure_cases.pdf` | I / V.C | Annotated frames: FP alert + track loss motivation | OpenCV annotation |
| `fig7_event_alert_metrics.pdf` | V.B (only with validated event GT) | Binary alert precision/recall, false alerts/hour and delay | Matplotlib |

## Export tips
- The legacy draft includes `fig1_pipeline_body.tex` directly, avoiding a stale
  cached pipeline PDF. The JRTIP manuscript keeps its TikZ figure inline to meet
  the single-file submission format. Both now show untested event-alert candidates.
- To rebuild the optional standalone pipeline PDF, compile
  `fig1_pipeline_overview.tex` from `paper/figures/` with a LaTeX installation.
- Matplotlib: `plt.savefig('figN_name.pdf', bbox_inches='tight', dpi=300)`
- Draw.io: File → Export As → PDF (uncheck "fit page")
- All text in figures: **minimum 8pt** (IEEE requirement)
- Color: use colorblind-safe palette (matplotlib `tab10` or `colorblind`)
