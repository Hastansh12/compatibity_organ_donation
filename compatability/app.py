from flask import Flask, request, jsonify
import pandas as pd
import random

app = Flask(__name__)



# Sample Indian names
indian_names = [
    "Aarav Sharma", "Siddharth Verma", "Ishaan Reddy", "Advait Gupta", "Vihaan Kumar",
    "Aadya Khanna", "Aaradhya Yadav", "Anvi Singh", "Aarush Kapoor", "Navya Choudhury",
    "Aanya Patel", "Kabir Singh", "Aaliyah Chopra", "Reyansh Joshi", "Anaya Bansal",
    "Aarush Mehta", "Aria Bhatia", "Rudra Khurana", "Aadhya Rana", "Ishan Malhotra"
]

# Create separate arrays for donor and recipient names (sample size: 10)
donor_names = random.sample(indian_names, 10)
recipient_names = random.sample([name for name in indian_names if name not in donor_names], 10)

# Create a dataset with donor and recipient HLA types, blood types, donor BMI, and names (sample size: 10)
data = {
    'Donor_Name': donor_names,
    'Recipient_Name': recipient_names,
    'Donor_HLA_A': ['A1', 'A2', 'A3', 'A1', 'A2', 'A4', 'A2', 'A3', 'A5', 'A6'],
    'Recipient_HLA_A': ['A1', 'A2', 'A1', 'A3', 'A2', 'A3', 'A4', 'A5', 'A6', 'A1'],
    'Donor_HLA_B': ['B7', 'B8', 'B9', 'B8', 'B7', 'B6', 'B8', 'B7', 'B9', 'B6'],
    'Recipient_HLA_B': ['B7', 'B8', 'B7', 'B9', 'B8', 'B6', 'B7', 'B6', 'B5', 'B4'],
    'Donor_HLA_DR': ['DR1', 'DR2', 'DR3', 'DR4', 'DR1', 'DR2', 'DR3', 'DR4', 'DR2', 'DR3'],
    'Recipient_HLA_DR': ['DR1', 'DR2', 'DR1', 'DR3', 'DR2', 'DR3', 'DR4', 'DR3', 'DR2', 'DR4'],
    'Donor_HLA_C': ['C1', 'C2', 'C3', 'C4', 'C1', 'C2', 'C3', 'C4', 'C2', 'C3'],
    'Recipient_HLA_C': ['C1', 'C2', 'C1', 'C3', 'C2', 'C3', 'C4', 'C3', 'C2', 'C4'],
    'Donor_HLA_DQ': ['DQ1', 'DQ2', 'DQ3', 'DQ4', 'DQ1', 'DQ2', 'DQ3', 'DQ4', 'DQ2', 'DQ3'],
    'Recipient_HLA_DQ': ['DQ1', 'DQ2', 'DQ1', 'DQ3', 'DQ2', 'DQ3', 'DQ4', 'DQ3', 'DQ2', 'DQ4'],
    'Donor_Blood_Type': ['A', 'B', 'O', 'A', 'AB', 'B', 'O', 'O', 'A', 'AB'],
    'Recipient_Blood_Type': ['A', 'B', 'A', 'O', 'AB', 'A', 'O', 'B', 'AB', 'O'],
    'Donor_BMI': [23, 28, 25, 32, 18, 27, 35, 29, 22, 26]
}

# Calculate compatibility based on HLA matching
def calculate_hla_compatibility(row):
    hla_matches = 0
    hla_loci = ['A', 'B', 'DR', 'C', 'DQ']  # Add more HLA loci here
    for hla_locus in hla_loci:
        donor_hla = row[f'Donor_HLA_{hla_locus}']
        recipient_hla = row[f'Recipient_HLA_{hla_locus}']
        if donor_hla == recipient_hla:
            hla_matches += 1
    return hla_matches

# Calculate compatibility based on blood type matching
def calculate_blood_type_compatibility(row):
    donor_blood_type = row['Donor_Blood_Type']
    recipient_blood_type = row['Recipient_Blood_Type']
    return donor_blood_type == recipient_blood_type

# Define a threshold for HLA compatibility (e.g., 2 or more HLA matches for compatibility)
hla_threshold = 2

# Define a threshold for donor BMI (e.g., a healthy BMI range)
healthy_bmi_lower = 18.5
healthy_bmi_upper = 30

# Define a formula for calculating compatibility score
def calculate_compatibility_score(row):
    hla_matches = row['HLA_Matches']
    bmi_compatibility = row['BMI_Compatibility']
    blood_type_compatibility = row['Blood_Type_Compatibility']
    
    # Customize this formula as needed
    # You can assign different weights to each component (HLA, BMI, blood type)
    # For example: compatibility_score = hla_matches * 0.5 + bmi_compatibility * 0.3 + blood_type_compatibility * 0.2
    
    compatibility_score =((hla_matches * 0.5) + (int(bmi_compatibility) * 0.3) + (int(blood_type_compatibility) *0.2))*100
    # For demonstration, using HLA matches as the compatibility score
    return compatibility_score

@app.route('/',methods=['GET'])
def calculate_compatibility():
    # Retrieve data from the POST request
    # request_data = request.json
    
    # Create a DataFrame from the request data
    df = pd.DataFrame(data)
    
    # Calculate compatibility based on HLA matching
    df['HLA_Matches'] = df.apply(calculate_hla_compatibility, axis=1)
    
    # Calculate compatibility based on blood type matching
    df['Blood_Type_Compatibility'] = df.apply(calculate_blood_type_compatibility, axis=1)
    
    # Calculate compatibility based on donor BMI
    def calculate_bmi_compatibility(row):
        donor_bmi = row['Donor_BMI']
        return healthy_bmi_lower <= donor_bmi <= healthy_bmi_upper
    
    df['BMI_Compatibility'] = df.apply(calculate_bmi_compatibility, axis=1)
    
    # Calculate compatibility score
    df['Compatibility_Score'] = df.apply(calculate_compatibility_score, axis=1)
    
    # Determine overall compatibility (HLA, blood type, and donor BMI)
    df['Overall_Compatibility'] = (df['HLA_Matches'] >= hla_threshold) & df['Blood_Type_Compatibility'] &  df['BMI_Compatibility']
    
    # Convert the results to JSON
    matching_donors = df.to_dict(orient='Recipient_Name')
    
    return jsonify(matching_donors)

if __name__ == '__main__':
    app.run(debug=True)
