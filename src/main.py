from src.loader import load_excel
from src.validator import validate

df = load_excel("data/profitandloss.xlsx")

result = validate(df, "profitandloss")

print(result)