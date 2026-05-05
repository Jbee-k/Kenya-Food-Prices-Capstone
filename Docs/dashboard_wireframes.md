# Dashboard Wireframes — Kenya Food Prices Power BI Dashboard

## Design System

**Page size:** Custom 1280 × 720 px (16:9)
**Grid:** 12-column × 24-row invisible
**Header bar (60px):** project title left | page name center | refresh date right
**Navigation pane (200px left):** vertical icon buttons for the 5 pages, bookmark-driven

**Color palette**
| Role | Hex | Use |
|---|---|---|
| Primary | `#C2410C` | High prices, shocks, alerts |
| Accent | `#15803D` | Low prices, positive change |
| Neutral text | `#1F2937` | All text |
| Background | `#F8FAFC` | Page bg |
| Diverging ramp | `#15803D` → `#FCD34D` → `#C2410C` | Maps |

**Typography**
| Element | Font | Size | Weight |
|---|---|---|---|
| H1 page title | Segoe UI | 28pt | Bold |
| H2 section heading | Segoe UI | 18pt | SemiBold |
| KPI value | Segoe UI | 36pt | Bold |
| Body | Segoe UI | 11pt | Regular |
| Caption | Segoe UI | 9pt | Regular Italic |

---

## Page 1 — Executive Overview

**Story:** What's the state of Kenya food prices today?

**KPI strip (5 cards):**
1. `[Avg Price Per Kg]` — "Avg KES / kg"
2. `[YoY Price Change %]` — "YoY change" (color-coded: red >5%, green <0%)
3. `[Total Markets Tracked]` — "Markets"
4. `[Distinct Counties]` — "Counties"
5. `[Latest Observation Date]` — "Latest data"

**Main visuals:**
- Line chart (40% width): `[Rolling 12M Avg Price Per Kg]` over `DimDate[Date]`, with shock-period shaded bands using `DimDate[IsShockPeriod]`
- Map (60% width): bubble map with `DimMarket[Latitude/Longitude]`, bubble size = observation count, color = `[Avg Price Per Kg]`
- Bar chart (50%): top 10 counties by `[Avg Price Per Kg]`, sorted descending
- Bar chart (50%): top 10 commodities by `[YoY Price Change %]`
- Text card: manual headline insight (1–2 sentences)

**Slicers:** Year (DimDate[Year]) | PriceType (FactPrices[PriceType])

---

## Page 2 — Geographic Disparity

**Story:** Which counties are paying the most for food?

**KPI strip (4 cards):**
1. `[National Avg Price Per Kg]`
2. `[Min County Avg]`
3. `[Max County Avg]`
4. `[County Spread %]`

**Main visuals:**
- Choropleth map (full width): `DimMarket[County]`, fill = `[County Premium %]`, diverging green→yellow→red
- Table (50%): rank | county | `[Avg Price Per Kg]` | `[County Premium %]` | `[MoM Price Change %]` | `[YoY Price Change %]`, sortable, conditional formatting on premium column
- Heatmap matrix (50%): rows = counties (top 20), columns = quarters, cell = `[Avg Price Per Kg]`

**Slicers:** Commodity (DimCommodity[CommodityName]) | Year | Date range

**Drill-through:** right-click county → opens hidden Page "County Detail" filtered to that county

---

## Page 3 — Commodity Trends

**Story:** How have specific commodities moved over time, and why?

**Header slicer:** Commodity (single-select), drives the whole page

**KPI strip (4 cards):**
1. `[Avg Price Per Kg]` (current)
2. `[Inflation vs 2010 Baseline]`
3. `[Rolling 12M Avg Price Per Kg]`
4. `[YoY Price Change %]`

**Main visuals:**
- Combination chart (full width): line for monthly `[Avg Price Per Kg]`, shaded bands for `IsShockPeriod`, callout text annotations on major events
- Box plot (50%): year on x-axis, `PricePerKg` distribution on y-axis, shows median, IQR, outliers
- Bar chart (50%): top 10 markets for the selected commodity by `[Avg Price Per Kg]`

**Slicers:** Commodity (header) | County | Year

---

## Page 4 — Shock Period Analysis

**Story:** How much did prices spike during Kenya's known crises?

**KPI strip (4 cards):**
1. `[Shock Severity %]`
2. `[Avg Price During Shocks]`
3. `[Avg Price Outside Shocks]`
4. Count of distinct shock events covered

**Main visuals:**
- Time series with shock bands (full width): `[Avg Price Per Kg]` line, vertical shaded bands for each shock event labeled with `DimDate[ShockEvent]`
- League table (full width): one row per shock event with: Event | Period | Avg Before | Avg During | Severity % | Most-Affected County | Most-Affected Commodity. Conditional formatting on Severity %.

**Slicers:** Commodity | County

---

## Page 5 — Refugee Camp Lens

**Story:** Are food prices fairer in Kenya's refugee camps than nearby urban markets?

**KPI strip (4 cards):**
1. `[Avg Price - Refugee Camps]`
2. `[Avg Price - Non-Camp Markets]`
3. `[Refugee Camp Premium %]` (color-coded)
4. `[Refugee Camps Tracked]`

**Main visuals:**
- Map (50%): all markets shown, refugee camps highlighted with stronger color/larger bubble; tooltip shows complex name and avg price
- Stacked bar (50%): each refugee complex (Kakuma, Dadaab, Kalobeyei) vs nearest urban market (Lodwar, Garissa, Lodwar respectively), grouped bars
- Time series (full width): two lines — `[Avg Price - Refugee Camps]` and `[Avg Price - Non-Camp Markets]` — over time
- Bar chart (full width): commodity on x, `[Refugee Camp Premium %]` on y, sorted by absolute premium

**Slicers:** Refugee Complex | Year | Commodity

---

## Hidden Page — County Detail (drill-through target)

Filtered automatically by the county the user right-clicked from any other page.

- KPIs for this county only
- Commodity-level table (commodity | avg price | YoY %)
- Time series for the county's avg price across years
- Top 5 markets within the county by observation count

---

## Navigation & Interactivity

**Page navigation:** Bookmarks pane creates clickable buttons on the left rail. Each bookmark = a single page focused with consistent slicer state.

**Cross-page filters:** None. Each page has its own slicer state by design — keeps stories independent.

**Cross-visual filters within a page:** All visuals cross-filter each other (default Power BI behavior).

**Drill-throughs:** Page 2 county → County Detail page. Page 4 shock row → Shock Detail (optional, future work).

**Tooltips:** Custom tooltip pages for the map (showing market metadata) and the league table (showing year-over-year breakdown).

---

## Mapping to Zindua Syllabus

| Lesson | Demonstrated by |
|---|---|
| Tables and Scatter Charts | Page 2 league table, Page 3 box plot |
| Bar Charts | Pages 1, 2, 5 — top-N rankings, premium-by-commodity |
| Combination Charts | Pages 3, 4 — line + shaded shock bands |
| Dashboards vs Reports | This is structured as a multi-page **report** with one summary **dashboard** page |
| Creating a Report | Whole project |
| Page View and Page Size | Custom 1280×720 page size, consistent across pages |
| Visual Interactions | Cross-filtering between visuals on same page; drill-through to County Detail |
| Principles of Data Storytelling | Each page tells one specific story; insights surfaced in headline cards |
