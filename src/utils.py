import pandas as pd
import os


def load_animal_data():
    """
    Load and preprocess animal shelter data from CSV file.

    Returns:
        pandas.DataFrame: Cleaned dataset with location data, or empty DataFrame on error
    """
    try:
        # Construct path to CSV file in data directory
        csv_path = os.path.join('..', 'data', 'aac_shelter_outcomes.csv')

        # Load the CSV data
        df = pd.read_csv(csv_path)

        # Filter out records without geographic coordinates (required for mapping)
        df = df.dropna(subset=['location_lat', 'location_long'])

        # Remove auto-generated index column if present
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)

        # Log loading results
        print(f"✅ Loaded {len(df)} animals from CSV")
        print(f"📊 Animal types: {df['animal_type'].value_counts().to_dict()}")

        # Display breakdown of 'Other' category animals for data insight
        if 'Other' in df['animal_type'].values:
            other_breeds = df[df['animal_type'] == 'Other']['breed'].value_counts().head(10)
            print(f"🦎 Top 'Other' animals: {other_breeds.to_dict()}")

        return df

    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()


def get_animal_stats(df):
    """
    Calculate summary statistics for the animal dataset.

    Args:
        df (pandas.DataFrame): Animal data

    Returns:
        dict: Dictionary containing count statistics by animal type and outcome
    """
    if df.empty:
        return {}

    animal_counts = df['animal_type'].value_counts().to_dict()

    stats = {
        'total_animals': len(df),
        'dogs': animal_counts.get('Dog', 0),
        'cats': animal_counts.get('Cat', 0),
        'other': animal_counts.get('Other', 0),
        'birds': animal_counts.get('Bird', 0),
        'livestock': animal_counts.get('Livestock', 0),
        'adopted': len(df[df['outcome_type'] == 'Adoption']),
        'unique_breeds': df['breed'].nunique()
    }

    return stats


def convert_age_to_readable(weeks):
    """
    Convert animal age from weeks to human-readable format.

    Args:
        weeks (float): Age in weeks

    Returns:
        str: Formatted age string (e.g., "2 years, 3 months")
    """
    if pd.isna(weeks) or weeks == 0:
        return "Unknown"

    years = int(weeks // 52)
    remaining_weeks = int(weeks % 52)
    months = int(remaining_weeks // 4.33)  # Approximate conversion (4.33 weeks per month)

    if years > 0:
        if months > 0:
            return f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
        else:
            return f"{years} year{'s' if years != 1 else ''}"
    elif months > 0:
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        return f"{int(weeks)} week{'s' if weeks != 1 else ''}"


def prepare_dashboard_data(df):
    """
    Prepare raw animal data for dashboard display with user-friendly formatting.

    Args:
        df (pandas.DataFrame): Raw animal data

    Returns:
        pandas.DataFrame: Processed data ready for dashboard display
    """
    if df.empty:
        return df

    # Create copy to preserve original data
    display_df = df.copy()

    # Add human-readable age column
    display_df['age_readable'] = display_df['age_upon_outcome_in_weeks'].apply(convert_age_to_readable)

    # Handle missing values in key display columns
    columns_to_clean = ['name', 'animal_type', 'breed', 'sex_upon_outcome', 'color', 'outcome_type']
    for col in columns_to_clean:
        if col in display_df.columns:
            display_df[col] = display_df[col].fillna('Unknown')
            display_df[col] = display_df[col].replace('', 'Unknown')

    # Clean animal names by removing database artifacts
    if 'name' in display_df.columns:
        # Remove asterisk prefixes used in shelter database
        display_df['name'] = display_df['name'].str.replace('*', '', regex=False)
        # Clean whitespace
        display_df['name'] = display_df['name'].str.strip()

    return display_df