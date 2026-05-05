# Reference CSVs — Star Schema Ground Truth

These four CSVs simulate the output of all Power Query transformations applied to the raw WFP Kenya food prices dataset. They represent the *expected* state of the data model after cleaning, ready to load directly into Power BI as a star schema.

## Files

| File | Rows | Cols | Purpose |
|---|---|---|---|
| `FactPrices.csv` | 12,588 | 9 | Fact table — all observed retail/wholesale prices |
| `DimDate.csv` | 7,670 | 8 | Date dimension (2006-01-01 → 2026-12-31) |
| `DimMarket.csv` | 226 | 9 | Market dimension with modern county and refugee flags |
| `DimCommodity.csv` | 51 | 4 | Commodity dimension with category and staple flag |

## Transformations Applied

### FactPrices
1. Filtered raw data to `priceflag = "actual"` — drops 6,417 rows of WFP-computed aggregates
2. Computed `PricePerKg` using unit-to-kg conversion factors (KG=1, 90 KG=90, 200 G=0.2, etc.)
3. Computed `PricePerLitre` using unit-to-litre conversion factors (L=1, 500 ML=0.5)
4. Renamed columns to PascalCase
5. Dropped redundant columns (admin1, admin2, market name, latitude, longitude, category, currency, priceflag) — those live in dimension tables

### DimMarket
1. Sourced from `counties_bridge.csv` (already cleaned)
2. 226 markets, 100% mapped to 25 modern Kenya counties
3. 15 markets flagged as refugee camps across 3 complexes (Kakuma, Dadaab, Kalobeyei)

### DimCommodity
1. Distinct commodity_id + commodity + category from raw data
2. Added `IsKenyaStaple` boolean — True for 15 commodities in the basic Kenyan household basket (maize variants, beans variants, sukuma/kale, sugar, salt, rice, wheat flour, oil, milk)

### DimDate
1. Generated daily calendar 2006-01-01 → 2026-12-31 (7,670 days)
2. Standard date attributes: Year, Quarter, MonthNumber, MonthName, MonthYear
3. Flagged `IsShockPeriod` and `ShockEvent` for 6 known crisis windows:
   - 2008 Post-Election Crisis (Jan-Mar 2008)
   - 2011 Horn of Africa Drought (Jul-Dec 2011)
   - 2017 Maize Crisis (Apr-Aug 2017)
   - 2020 COVID-19 Disruption (Mar-Aug 2020)
   - 2022 Fuel & Fertilizer Shock (Mar-Sep 2022)
   - 2022-23 ASAL Drought (Oct 2022 - Mar 2023)

## Referential Integrity (verified)
- 0 MarketIDs in FactPrices missing from DimMarket
- 0 CommodityIDs in FactPrices missing from DimCommodity
- 0 Dates in FactPrices missing from DimDate

## How to Use in Power BI

**Path 1 — Direct import (faster, skips Power Query practice):**
1. Get Data → Text/CSV → import all four files
2. In Model view, create relationships:
   - DimDate[Date] → FactPrices[Date], 1:many, single direction
   - DimMarket[MarketID] → FactPrices[MarketID], 1:many, single direction
   - DimCommodity[CommodityID] → FactPrices[CommodityID], 1:many, single direction
3. Mark DimDate as Date Table (Modeling tab)
4. Create _Measures table, paste DAX library
5. Build dashboard

**Path 2 — Validate Power Query work (recommended for capstone):**
1. Open Power BI, import raw `wfp_food_prices_ken.csv`
2. Replay Power Query steps from `data_quality_report.md` cleaning plan
3. After each major step, compare row counts and key statistics against the corresponding reference CSV
4. When your output matches, you've executed the cleaning correctly

## Key Validation Checks

| Check | Expected |
|---|---|
| FactPrices row count | 12,588 |
| FactPrices distinct MarketIDs | 213 |
| FactPrices distinct CommodityIDs | 45 |
| FactPrices PricePerKg non-null | 11,429 (90.8%) |
| DimMarket row count | 226 |
| DimMarket distinct counties | 25 |
| DimMarket refugee camps | 15 |
| DimCommodity row count | 51 |
| DimCommodity Kenya staples | 15 |
| DimDate row count | 7,670 |
| DimDate shock days | 1,008 |
