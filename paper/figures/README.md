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
| `fig1_pipeline_overview.pdf` | III | Full system pipeline with C1/C2/C3 highlighted | Draw.io → PDF |
| `fig2_context_estimator.pdf` | III.A | C1 state machine / logic diagram | Draw.io |
| `fig3_ctrv_vs_kalman.pdf` | III.B | Trajectory comparison: CTRV vs linear Kalman on real footage | Matplotlib |
| `fig4_reliability_score.pdf` | III.C | C3 dual-threshold split diagram | Draw.io |
| `fig5_qualitative_tracking.pdf` | V.C | Side-by-side: baseline vs proposed track IDs | OpenCV annotation |
| `fig6_failure_cases.pdf` | I / V.C | Annotated frames: FP alert + track loss motivation | OpenCV annotation |
| `fig7_confusion_matrix.pdf` | V.B | 3-class severity confusion matrix | seaborn heatmap |

## Export tips
- Matplotlib: `plt.savefig('figN_name.pdf', bbox_inches='tight', dpi=300)`
- Draw.io: File → Export As → PDF (uncheck "fit page")
- All text in figures: **minimum 8pt** (IEEE requirement)
- Color: use colorblind-safe palette (matplotlib `tab10` or `colorblind`)
