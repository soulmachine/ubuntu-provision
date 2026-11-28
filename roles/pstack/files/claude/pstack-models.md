# Managed by the provisioning repo's pstack role (roles/pstack/files/claude/pstack-models.md). Edit it there: the next provision run overwrites any local change, a /pstack:setup-pstack run included.
# pstack model configuration. One line per role. Delete a line to fall back to the skill default.
# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model` and spawn `generalPurpose`). Alias entries in a panel list still count toward its fan-out.
# defaults: 3
# budget: large (xhigh)
feature, refactoring: opus xhigh
bug-fix: opus xhigh
perf-issue: opus xhigh
hillclimb: opus xhigh
judgment and prose: opus xhigh
arena runners: fable high, opus high, inherit-parent
arena cross-judge pool: opus high, inherit-parent
swarm workers: opus high
interrogate reviewers: fable high, opus high, inherit-parent
