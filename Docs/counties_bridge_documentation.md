# Counties Bridge Table — Documentation

## Purpose
Maps each of the 226 markets in the WFP Kenya food prices dataset to its modern (post-2013) Kenya county, plus refugee camp metadata. Used as a lookup table merged into `DimMarket` in Power BI.

## File
`counties_bridge.csv` — 226 rows × 10 columns

## Columns
| Column | Type | Description |
|---|---|---|
| MarketID | Integer | Unique market identifier (matches FactPrices.MarketID) |
| MarketName | Text | Cleaned market name |
| Province | Text | Legacy 8-province admin1 (pre-2013 system) |
| District | Text | Sub-county / admin2 |
| County | Text | **Modern post-2013 Kenya county (47 total in Kenya, 25 covered here)** |
| IsRefugeeCamp | Boolean | True for the 15 refugee complex markets |
| RefugeeComplex | Text | Kakuma / Dadaab / Kalobeyei / null |
| Latitude | Decimal | Market coordinates |
| Longitude | Decimal | Market coordinates |
| RecordCount | Integer | Number of price observations for this market |

## Mapping Rules Applied
1. Direct match where district name == county name (22 cases)
2. Translation rules for renamed/restructured districts:
   - Ijara → Garissa County
   - Meru North → Meru County
   - Meru South → Tharaka-Nithi County
   - Moyale → Marsabit County
   - Taita Taveta → Taita-Taveta County (hyphen)
3. Refugee camp overrides (force County by complex):
   - Kakuma * → Turkana County
   - Kalobeyei * → Turkana County
   - Dadaab / Hagadera / IFO / Dagahaley → Garissa County

## Coverage Summary
- 226 markets fully mapped, zero null counties
- **25 of Kenya's 47 counties have data** (54% coverage)
- 22 counties with no market data — primarily Western Province, most of Central, parts of Nyanza and Rift Valley
- Heavy bias toward ASAL (Arid and Semi-Arid Lands) counties: Turkana (57), Garissa (21), Samburu (20), Marsabit (19), Tana River (17), Isiolo (16). This reflects WFP's monitoring focus on drought-prone and refugee-hosting regions.

## Caveat to Note in Dashboard
The dataset is *not* nationally representative. WFP's monitoring is concentrated in food-insecure regions. Counties like Murang'a, Nyandarua, Kakamega, Bungoma, Vihiga, Kisii, Migori, Homa Bay, Kericho, Bomet, Trans-Nzoia, Nandi, Elgeyo-Marakwet, Laikipia, Narok, Embu, Lamu have no observations.

This caveat should appear on the Geographic Disparity page footer or in a "Data Coverage" tooltip.

## Power BI Import Steps
1. Get Data → Text/CSV → load `counties_bridge.csv`
2. Set data types (MarketID = Whole Number, IsRefugeeCamp = True/False, others as Text/Decimal)
3. In Power Query, merge this query with the `DimMarket` query on `MarketID`
4. Expand the merged columns: County, IsRefugeeCamp, RefugeeComplex
5. Close & Apply
