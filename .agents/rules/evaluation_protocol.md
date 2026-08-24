# PIPELINEIQ EVALUATION & PRE-FLIGHT RULES

1. Always use `eval/reliable_eval.py` for performance evaluation.
2. Full 25 public games denominator: `['ar25', 'bp35', 'cd82', 'cn04', 'dc22', 'ft09', 'g50t', 'ka59', 'lf52', 'lp85', 'ls20', 'm0r0', 'r11l', 're86', 's5i5', 'sb26', 'sc25', 'sk48', 'sp80', 'su15', 'tn36', 'tr87', 'tu93', 'vc33', 'wa30']`.
3. Kaggle projected score is calculated as `(mean_rhae * 0.25) * 100%`.
4. Submission gate: Local score must be >= 0.0800 (8.00%), which translates to >= 2.00% on Kaggle, before any push to Kaggle is permitted.
5. All code must be thread-safe (`threading.Lock()`) and have zero spatial coordinate hardcoding.
