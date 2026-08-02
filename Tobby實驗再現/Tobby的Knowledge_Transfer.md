# Knowledge Transfer Checklist
### Transfer Information

| Item | Description |
|---|---|
| Thesis Title | 異質小型基地台網路節能開關 Cell Switching for Energy Saving in Heterogeneous Small Cell Networks |
| Graduating Researcher |  Tobby |
| Responsible Incoming Student | Winnie |
| Advisor | Winnie |
| Final Defense Date | 2026/6/22 |
| Transfer Date | 2026/7/3 |
| pCloud Link | https://u.pcloud.link/publink/show?code=kZ0eJi5ZuXoB32GhTmprjUUXEEQ3EVws0vM7 |

### Research Package

| Item                  | Link | Status |
| --------------------- | ---- | ------ |
| Thesis / Thesis Draft | Final / [Oral exam drift version](https://u.pcloud.link/publink/show?code=XZaVpN5ZoLYTUEXeEbLpq190qy4drpADb8dy) / [Overleaf Link](https://www.overleaf.com/project/69d5eb36a71638902942abad)     | ☐      |
| Paper / Manuscript    | Final / [Overleaf Link](https://www.overleaf.com/project/68c7b4ca7597180cb87f100c)     | ☐      |
| Defense Slides        | [Final](https://u.pcloud.link/publink/show?code=XZYoLU5ZFSgVRRjevVRWvuF1hBiAbkmM8RpV) / [Oral exam drift version](https://u.pcloud.link/publink/show?code=XZfKBN5ZtvWwNAngiQLVaC53X2Pnj7zf6VK7)     | ☐      |
| Design Documents      | [Readme](Data_modeling/Readme.md#9-detailed-design-proposed-method)     | ☐      |
| README                | [Readme](Data_modeling/Readme.md)     | ☐      |

---

### Research Repository

| Item                  | Link | Status |
| --------------------- | ---- | ------ |
| GitHub Repository     | https://github.com/bmw-ece-ntust/intent-configuration-system/tree/tobby     | ☐      |
| Latest Working Commit |      | ☐      |

---

### Minimum Reproducible Result (MRR)

List every experimental result presented in the final defense slides.

| Slide / Figure / Table | Expected Result | Configuration | Execution Guide | Reference Evidence |
|---|---|---|---|---|
| Scenario 1: Algorithm Behavior Validation / P26, 27  | [P26](Data_modeling/result_backup/same_area_uniform/figure/consumption_throughput_by_config/fixed_throughput/actual_power_saving_sweep_tput_10.png), [P27](Data_modeling/result_backup/PMdiff_uniform/figure/consumption_throughput_by_config/fixed_throughput/actual_power_saving_percent_sweep_tput_10.png) |[P26](Data_modeling/Other/VIAVI_config/ai-rsg_config_37cells_PMdiffer_sameArea_8UE_random_macro130w_each_cell.json), [P27](Data_modeling/Other/VIAVI_config/ai-rsg_config_37cells_PMdiffer_8UE_random_macro130w_each_cell.json) | [Execute Command](Data_modeling/Readme.md#experiment-1-algorithm-behavior-validation)| P26: Data_modeling/result_backup/same_area_uniform, P27: Data_modeling/result_backup/PMdiff_uniform  |
| Scenario 2: Algorithm Comparison under Random Loading / P28 |[P28 left](Data_modeling/result_backup/same_area_nonuniform/figure/consumption_throughput_by_config/fixed_throughput/actual_power_saving_percent_sweep_tput_10.png), [P28 right](Data_modeling/result_backup/PMdiff_nonuniform/figure/consumption_throughput_by_config/fixed_throughput/actual_power_saving_percent_sweep_tput_10.png) | [P28 left](Data_modeling/Other/VIAVI_config/ai-rsg_config_37cells_PMdiffer_sameArea_120UE_random_macro130w.json), [P28 right](Data_modeling/Other/VIAVI_config/ai-rsg_config_37cells_PMdiffer_120UE_random_macro130w.json) | [Execute Command](Data_modeling/Readme.md#experiment-2-algorithm-comparison-under-random-loading)| P28 left: Data_modeling/result_backup/same_area_nonuniform, P28 right: Data_modeling/result_backup/PMdiff_nonuniform  |
| Scenario 3: Cell On/Off Strategy and Thresholds / P29, 30, 31, 32, 33 | [$\mu_{on} = 245$ vs. $\mu_{on} = 191$ throughput and macro cell full load](Data_modeling/result_backup/TimeSerise/comparison_overall_analysis_70_vs_90_full_load_vs_throughput.png), <br>[$\mu_{on} = 245$ vs. $\mu_{on} = 191$ energy saving](Data_modeling/result_backup/TimeSerise/comparison_overall_analysis_70_vs_90_energy_saving.png), <br>[$\mu_{on} = 245$ and $\mu_{off} = 81$ Macro cell PRB](Data_modeling/result_backup/TimeSerise/90_x/20260613_103916_90-30/comparison_results_coverage_prb.png), <br>[$\mu_{on} = 191$ and $\mu_{off} = 81$ Macro cell PRB](Data_modeling/result_backup/TimeSerise/70_x/20260609_074303_70-30/comparison_results_coverage_prb.png), <br>[$\mu_{on} = 191$ vs. $\mu_{on} = 136$ throughput and macro cell full load](Data_modeling/result_backup/TimeSerise/comparison_overall_analysis_70_vs_50_full_load_vs_throughput.png), <br>[$\mu_{on} = 191$ vs. $\mu_{on} = 136$ energy saving](Data_modeling/result_backup/TimeSerise/comparison_overall_analysis_70_vs_50_energy_saving.png), <br>[$\mu_{on} = 191$ vs. $\mu_{on} = 136$ number of on/off control](Data_modeling/result_backup/TimeSerise/comparison_overall_analysis_70_vs_50_cell_actions_comparison.png), <br>[$\mu_{on} = 191$ and $\mu_{off} = 81$ Cells state](Data_modeling/result_backup/TimeSerise/70_x/20260609_074303_70-30/influxdb/plots/Cell_ON_OFF_Status.png), <br>[$\mu_{on} = 136$ and $\mu_{off} = 81$](Data_modeling/result_backup/TimeSerise/50_x/20260610_044711_50-30/influxdb/plots/Cell_ON_OFF_Status.png) | [Config file](Data_modeling/Other/VIAVI_config/ai-rsg_config_37cells_PMdiffer_sameArea_216UE_time_2.json) | [Execute Command](Data_modeling/Readme.md#experiment-3-cell-onoff-strategy-and-thresholds) | All result: Data_modeling/result_backup/TimeSerise, $\mu_{on} = 245$: Data_modeling/result_backup/TimeSerise/90_x, $\mu_{on} = 191$: Data_modeling/result_backup/TimeSerise/70_x, $\mu_{on} = 136$: Data_modeling/result_backup/TimeSerise/50_x|

---

### Research Assets

| Asset                  | Location | Status |
| ---------------------- | -------- | ------ |
| Hardware               |          | ☐      |
| Software License       |          | ☐      |
| Accounts / Permissions |          | ☐      |
| Dataset                |          | ☐      |
| Other Resources        |          | ☐      |

---

### Remaining Work

| Item                   | Link | Status |
| ---------------------- | ---- | ------ |
| Open Issues            |      | ☐      |
| Future Work            |      | ☐      |
| Recommended First Task |      | ☐      |

> **Completing this checklist means that the transfer package is ready
> for verification. It does not mean that knowledge transfer has been accepted.**


---

## Where?

### Related Documents

* [Knowledge Transfer](../docs/10-knowledge-transfer.md)

### Related Templates

* [C-verification-report.md](C-verification-report.md)
* [D-acceptance-form.md](D-acceptance-form.md)

---

## Final Message

> **Knowledge transfer begins with a complete research package.**