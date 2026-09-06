# Model Card — House Price Prediction

## Model Details
- **Type**: GradientBoostingRegressor (scikit-learn)
- **Task**: Tabular regression — predict house price from features
- **Features**: area, bedrooms, bathrooms, age, floors, location_encoded
- **Target**: price (USD)

## Training Data
- Source: [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (Kaggle, CC0)
- Raw file: `data/raw/kc_house_data.csv` (~21,613 sales, May 2014–May 2015)
- Ingest maps to training features (~21,510 rows after outlier filter)
- Mapping: `sqft_living→area`, `2015-yr_built→age`, `zipcode→location`, `floors` kept
- Split: 70% train, 10% validation, 20% test
- Preprocessing: LabelEncoder for location (zipcode), StandardScaler for all features

## Metrics
| Metric | Threshold | Description |
|--------|-----------|-------------|
| RMSE   | <= 250000 | Root mean squared error (USD) |
| MAE    | <= 150000 | Mean absolute error (USD) |
| R2     | >= 0.60   | Coefficient of determination |
| MAPE   | <= 25%    | Mean absolute percentage error |

## Intended Use
- Educational MLOps project
- Demonstrates end-to-end ML lifecycle

## Limitations
- Features are a simplified subset of the full King County schema
- 2014–2015 market; not current pricing
- No feature interactions or advanced engineering

## Ethical Considerations
- Zipcode / location may encode socioeconomic bias
- Model should not be used for real pricing decisions
