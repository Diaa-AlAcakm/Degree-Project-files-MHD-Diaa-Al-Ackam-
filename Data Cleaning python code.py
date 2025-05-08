import pandas as pd
import numpy as np
import re
import ast

# Load the data
df = pd.read_csv('D:Dia\listings.csv')  # Update path if needed

# 1. Cleaning Price Column
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# 2. Fix Boolean Columns (t/f → True/False)
bool_columns = ['host_is_superhost', 'host_has_profile_pic', 'host_identity_verified', 'instant_bookable', 'has_availability']
for col in bool_columns:
    df[col] = df[col].map({'t': True, 'f': False})

# 3. Parse Dates Properly
date_columns = ['host_since', 'first_review', 'last_review', 'calendar_last_scraped', 'last_scraped']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# 4. Create New Useful Columns
df['availability_percentage'] = (df['availability_365'] / 365) * 100
df['listing_age_years'] = (pd.to_datetime('today') - df['host_since']).dt.days / 365
df['reviews_total'] = df['number_of_reviews']

# 5. Clean Amenities Column (Optional Simplification)
df['amenities_count'] = df['amenities'].apply(lambda x: len(re.findall(r'\"(.*?)\"', x)) if isinstance(x, str) else 0)

# 6. Clean and Expand Host Verifications
def parse_verifications(x):
    try:
        items = ast.literal_eval(x) if pd.notnull(x) else []
        return {
            'has_email': 'email' in items,
            'has_phone': 'phone' in items,
            'has_work_email': 'work_email' in items
        }
    except Exception:
        return {'has_email': False, 'has_phone': False, 'has_work_email': False}

verifications_df = df['host_verifications'].apply(parse_verifications).apply(pd.Series)
df = pd.concat([df, verifications_df], axis=1)

# Save cleaned version
df.to_csv('listings_cleaned.csv', index=False)
