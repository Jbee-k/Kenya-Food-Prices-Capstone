# Data Quality Report — WFP Kenya Food Prices

**Source:** Humanitarian Data Exchange (HDX) — *Kenya - Food Prices*
**Contributor:** World Food Programme (WFP)
**Download date:** 2026-05-03
**Dataset URL:** https://data.humdata.org/dataset/wfp-food-prices-for-kenya
**File:** `wfp_food_prices_ken.csv` (2.4 MB, 19,005 rows × 16 columns)
**Date range:** 15 January 2006 — 15 March 2026 (20.2 years, 243 distinct months)

---

## Summary

The dataset is **exceptionally clean** for a real-world public dataset — no full-row duplicates, no missing dates or prices, and only 0.21% of rows missing geographic columns. The main quality work is *transformation*, not repair: unit normalization, aggregate-row filtering, and standardizing the geographic hierarchy.

## Findings

### 1. Missing values
- 99.79% of rows are complete
- 39 rows (0.21%) missing `admin1`, `admin2`, `latitude`, `longitude` — all belonging to the market **Hola (Tana River)**, which exists but lacks region/coords lookups. Will be backfilled manually (Hola sits in Tana River County, formerly Coast Province).

### 2. Duplicates
- Zero full-row duplicates
- Zero duplicates on (date + market + commodity + unit + pricetype) composite key — confirms the natural primary key for the fact table.

### 3. Price flags
- 66% `actual` (real market observations)
- 33% `aggregate` (computed national/regional summaries)
- 1% `actual,aggregate`
- **Decision:** filter to `priceflag = "actual"` to keep only true observations. Drops to 12,588 rows.

### 4. Price types
- 65% Retail, 35% Wholesale
- **Decision:** keep both, but use Retail as the primary lens (consumer-facing price = the human story). Wholesale becomes a secondary view.

### 5. Unit normalization
13 distinct units. Conversion plan:
| Unit | Factor (to kg or litre) | Rows |
|---|---|---|
| KG | 1.0 | 9,920 |
| 90 KG | 90 | 2,773 |
| L | 1.0 | 1,667 |
| 50 KG | 50 | 1,367 |
| 200 G | 0.2 | 1,100 |
| 500 ML | 0.5 | 595 |
| 13 KG | 13 | 459 |
| 126 KG | 126 | 361 |
| 64 KG | 64 | 346 |
| Unit | n/a | 275 |
| 400 G | 0.4 | 112 |
| Bunch | n/a | 15 |
| Head | n/a | 15 |

Will create computed `price_per_kg` and `price_per_litre` columns. Rows with `Unit/Bunch/Head` will be excluded from cross-unit comparisons but retained for commodity-specific views.

### 6. Outlier check
- Min price: 5.00 KES — plausible (small commodity sold per piece)
- Max price: 19,800 KES — plausible (90 KG bag of premium beans in 2021 drought period)
- No values < 1 KES, no negatives, no impossibly high values
- Top 5 highest prices all reconcile with 90 KG bags during known shock periods

### 7. Market coverage asymmetry
- 60 markets have 50+ observations (well-covered, suitable for time series)
- 123 markets have 12–50 observations (usable but with caveats)
- 43 markets have fewer than 12 observations (excluded from market-level visuals; rolled up to district level)

### 8. Year-over-year data density
| Period | Avg rows/year | Notes |
|---|---|---|
| 2006–2020 | ~315 | Sparse, focused monitoring |
| 2021 onward | ~3,000 | WFP expanded monitoring during COVID-19 / drought / fuel shock |

**Implication for storytelling:** the dashboard will present a long-arc view (2006–2020) for trend context, and a granular crisis-era view (2021–present) for actionable detail.

## Cleaning decisions (going into Power Query)

1. Filter `priceflag = "actual"` — drops aggregates
2. Backfill 39 Hola records with admin1=Coast, admin2=Tana River, plus correct lat/long
3. Standardize date as proper date type
4. Build a Counties dimension table mapping markets to modern (post-2013) Kenya counties
5. Compute `price_per_kg` and `price_per_litre` from `unit` + `price`
6. Trim and proper-case all text columns (markets, commodities)
7. Build dimension tables: DimDate, DimMarket, DimCounty, DimCommodity, DimCategory
8. Tag markets that are refugee camps (Kakuma, Dadaab complex, Kalobeyei) — for the refugee-camp dashboard page
9. Mark known shock periods (2008 post-election, 2011 HoA drought, 2017 maize crisis, 2020 COVID, 2022 fuel shock, 2022–23 ASAL drought) for time-series annotation
