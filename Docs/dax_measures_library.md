# DAX Measures Library — Kenya Food Prices Dashboard

All measures should be placed in a dedicated "_Measures" table in Power BI (a blank table created just to hold them). DimDate must be marked as the Date Table for time intelligence to work.

## 1. Base Measures (Foundations)

```dax
Total Records = COUNTROWS(FactPrices)

Total Markets Tracked = DISTINCTCOUNT(FactPrices[MarketID])

Distinct Counties = DISTINCTCOUNT(DimMarket[County])

Distinct Commodities = DISTINCTCOUNT(FactPrices[CommodityID])

Refugee Camps Tracked =
CALCULATE(
    DISTINCTCOUNT(DimMarket[MarketID]),
    DimMarket[IsRefugeeCamp] = TRUE
)

Avg Price Per Kg = AVERAGE(FactPrices[PricePerKg])

Avg Price Per Litre = AVERAGE(FactPrices[PricePerLitre])

Median Price Per Kg = MEDIAN(FactPrices[PricePerKg])

Min Price Per Kg = MIN(FactPrices[PricePerKg])

Max Price Per Kg = MAX(FactPrices[PricePerKg])

Latest Observation Date = MAX(FactPrices[Date])

Earliest Observation Date = MIN(FactPrices[Date])

Months of Data =
DATEDIFF([Earliest Observation Date], [Latest Observation Date], MONTH)
```

## 2. Time Intelligence

```dax
Avg Price Per Kg YTD =
TOTALYTD(
    [Avg Price Per Kg],
    DimDate[Date]
)

Avg Price Per Kg PY =
CALCULATE(
    [Avg Price Per Kg],
    SAMEPERIODLASTYEAR(DimDate[Date])
)

Avg Price Per Kg LM =
CALCULATE(
    [Avg Price Per Kg],
    DATEADD(DimDate[Date], -1, MONTH)
)

YoY Price Change % =
VAR Current = [Avg Price Per Kg]
VAR Prior   = [Avg Price Per Kg PY]
RETURN
    DIVIDE(Current - Prior, Prior)

MoM Price Change % =
VAR Current = [Avg Price Per Kg]
VAR Prior   = [Avg Price Per Kg LM]
RETURN
    DIVIDE(Current - Prior, Prior)

Rolling 12M Avg Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    DATESINPERIOD(
        DimDate[Date],
        LASTDATE(DimDate[Date]),
        -12,
        MONTH
    )
)

Rolling 3M Avg Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    DATESINPERIOD(
        DimDate[Date],
        LASTDATE(DimDate[Date]),
        -3,
        MONTH
    )
)

Inflation vs 2010 Baseline =
VAR Baseline =
    CALCULATE(
        [Avg Price Per Kg],
        FILTER(ALL(DimDate), DimDate[Year] = 2010)
    )
VAR Current = [Avg Price Per Kg]
RETURN
    DIVIDE(Current - Baseline, Baseline)
```

## 3. Regional Disparity

```dax
National Avg Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    ALL(DimMarket)
)

County Premium % =
VAR County  = [Avg Price Per Kg]
VAR National = [National Avg Price Per Kg]
RETURN
    DIVIDE(County - National, National)

Min County Avg =
MINX(VALUES(DimMarket[County]), [Avg Price Per Kg])

Max County Avg =
MAXX(VALUES(DimMarket[County]), [Avg Price Per Kg])

County Spread KES =
[Max County Avg] - [Min County Avg]

County Spread % =
DIVIDE(
    [County Spread KES],
    [Min County Avg]
)
```

## 4. Refugee Camp Lens

```dax
Avg Price - Refugee Camps =
CALCULATE(
    [Avg Price Per Kg],
    DimMarket[IsRefugeeCamp] = TRUE
)

Avg Price - Non-Camp Markets =
CALCULATE(
    [Avg Price Per Kg],
    DimMarket[IsRefugeeCamp] = FALSE
)

Refugee Camp Premium KES =
[Avg Price - Refugee Camps] - [Avg Price - Non-Camp Markets]

Refugee Camp Premium % =
DIVIDE(
    [Refugee Camp Premium KES],
    [Avg Price - Non-Camp Markets]
)
```

## 5. Shock Period Analysis

```dax
Avg Price During Shocks =
CALCULATE(
    [Avg Price Per Kg],
    DimDate[IsShockPeriod] = TRUE
)

Avg Price Outside Shocks =
CALCULATE(
    [Avg Price Per Kg],
    DimDate[IsShockPeriod] = FALSE
)

Shock Severity % =
DIVIDE(
    [Avg Price During Shocks] - [Avg Price Outside Shocks],
    [Avg Price Outside Shocks]
)
```

## 6. Food Basket Index

```dax
Avg Staple Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    DimCommodity[IsKenyaStaple] = TRUE
)

Maize Avg Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    DimCommodity[CommodityName] IN { "Maize", "Maize (white)" }
)

Beans Avg Price Per Kg =
CALCULATE(
    [Avg Price Per Kg],
    DimCommodity[CommodityName] IN { "Beans", "Beans (dry)", "Beans (rosecoco)" }
)

Estimated Monthly Household Cost (KES) =
-- Assumes a standard household of 4 consumes:
-- 30 kg maize + 5 kg beans + 5 kg sukuma wiki + 4 kg sugar + 2 kg salt
VAR MaizeCost = 30 * [Maize Avg Price Per Kg]
VAR BeansCost =  5 * [Beans Avg Price Per Kg]
VAR Sukuma    =  5 * CALCULATE([Avg Price Per Kg], DimCommodity[CommodityName] = "Kale")
VAR Sugar     =  4 * CALCULATE([Avg Price Per Kg], DimCommodity[CommodityName] = "Sugar")
VAR Salt      =  2 * CALCULATE([Avg Price Per Kg], DimCommodity[CommodityName] = "Salt")
RETURN
    MaizeCost + BeansCost + Sukuma + Sugar + Salt
```

## 7. Coverage & Quality Helpers

```dax
Months Since Last Observation =
DATEDIFF(
    [Latest Observation Date],
    TODAY(),
    MONTH
)

Markets with Recent Data =
CALCULATE(
    DISTINCTCOUNT(FactPrices[MarketID]),
    FILTER(
        ALL(DimDate),
        DimDate[Date] >= EDATE(TODAY(), -12)
    )
)

Coverage Score =
DIVIDE(
    [Total Records],
    [Total Markets Tracked] * [Months of Data]
)
```

## How These Map to Zindua Concepts

| Zindua Lesson | Demonstrated By |
|---|---|
| Introduction to DAX | Every base measure |
| DAX Calculated Fields and Measures | All measures (placed in _Measures table, not on fact) |
| Common Function Categories | AVERAGE, SUM, MIN, MAX, COUNTROWS, DISTINCTCOUNT, MEDIAN, DIVIDE, MAXX, MINX, SUMX, AVERAGEX |
| Example DAX Use Cases | Ranking, KPI cards, inflation, regional comparisons |
| Joining Data With RELATED | Used implicitly; measures could be extended with RELATED for transforming dimension attributes |
| The CALCULATE Function | Every filtered measure (refugee, shock, county premium, baseline inflation) |
