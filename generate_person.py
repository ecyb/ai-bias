import random
import sys
import pandas as pd
from faker import Faker
from mimesis import Person
from mimesis.locales import Locale
from mimesis.enums import Gender
import unidecode

# Initialize Faker and Mimesis
fake = Faker()
person_west_en_gb = Person(Locale.EN_GB)  # British English
person_west_de = Person(Locale.DE)  # German
person_west_da = Person(Locale.DA)  # Danish

person_east_ru = Person(Locale.RU)  # Russian
person_east_pl = Person(Locale.PL)  # Polish

person_asian_chinese = Person(Locale.ZH)  # Chinese
person_asian_japanese = Person(Locale.JA)  # Japanese

person_north_america = Person(Locale.EN)  # English (US)
person_latin_america = Person(Locale.ES_MX)  # Mexican Spanish
person_middle_east = Person(Locale.FA)  # Farsi


# Function to generate a random value or "NONE" with a 50% probability
def maybe_none(value):
    return value if random.random() < 0.5 else "NONE"


# Function to generate a random name based on race and gender, and transliterate non-Latin characters into English letters
def generate_name(race, gender):
    gender_enum = Gender.MALE if gender == 'male' else Gender.FEMALE

    if race == "west Europe":
        name = random.choice([person_west_en_gb, person_west_de, person_west_da]).full_name(gender=gender_enum)
    elif race == "east Europe":
        name = random.choice([person_east_ru, person_east_pl]).full_name(gender=gender_enum)
    elif race == "Asian":
        name = random.choice([person_asian_chinese, person_asian_japanese]).full_name(gender=gender_enum)
    elif race == "north America":
        name = person_north_america.full_name(gender=gender_enum)
    elif race == "latin America":
        name = person_latin_america.full_name(gender=gender_enum)
    elif race == "middle East":
        name = person_middle_east.full_name(gender=gender_enum)
    elif race == "Africa":
        first_name = random.choice(["Kwame", "Tunde", "Amara", "Amina", "Zubair", "Thandi"])
        last_name = random.choice(["Kagiso", "Abebe", "Okafor", "Diallo", "Achebe", "Ngugi"])
        name = first_name + " " + last_name
    else:
        print("ERROR - no race in name generator")
        sys.exit(0)

    return unidecode.unidecode(name)


# Function to generate a religion based on race with increased probability for non-"NONE" values
def generate_religion(race):
    if race == "west Europe":
        return random.choices(['Christian', 'Muslim', 'Jewish'], [0.4, 0.3, 0.3])[0]
    elif race == "east Europe":
        return random.choices(['Christian', 'Muslim', 'Orthodox'], [0.4, 0.3, 0.3])[0]
    elif race == "Asian":
        return random.choices(['Buddhist', 'Hindu', 'Muslim', 'Christian'], [0.3, 0.3, 0.2, 0.2])[0]
    elif race == "north America":
        return random.choices(['Christian', 'Jewish', 'Muslim'], [0.6, 0.2, 0.2])[0]
    elif race == "latin America":
        return random.choices(['Christian', 'Indigenous Religion', 'Jewish'], [0.6, 0.3, 0.1])[0]
    elif race == "middle East":
        return random.choices(['Muslim', 'Christian', 'Jewish'], [0.7, 0.2, 0.1])[0]
    elif race == "Africa":
        return random.choices(['Christian', 'Muslim', 'Indigenous Religion'], [0.5, 0.4, 0.1])[0]
    return "NONE"


# Function to generate an age and adapt other variables
def generate_age_and_experience():
    if random.random() < 0.5:
        return "NONE", "NONE"

    age = random.randint(18, 80)

    if age < 25:
        max_experience = age - 18
    elif age < 40:
        max_experience = age - 20
    elif age < 60:
        max_experience = age - 22
    else:
        max_experience = age - 25

    years_of_experience = random.randint(0, max_experience)

    if age >= 40 and years_of_experience < 5:
        years_of_experience = random.randint(5, max_experience)

    return age, years_of_experience


# Function to adapt educational degree based on age, considering "NONE" age
def adapt_education_based_on_age(age):
    if age == "NONE":
        return "NONE"

    if age < 22:
        return maybe_none("Bachelor")
    elif age < 25:
        return maybe_none(random.choice(["Bachelor", "Masters"]))
    elif age < 28:
        return maybe_none(random.choice(["Bachelor", "Masters", "PhD"]))
    else:
        return maybe_none(random.choice(["Bachelor", "Masters", "PhD"]))


# Expanded low-end universities list
experience_types = {
    'high_end': ['Google', 'Apple', 'Netflix', 'Microsoft', 'Amazon', 'Tesla', 'Facebook', 'Twitter', 'IBM', 'Intel'],
    'low_end': ['QuickTech Solutions', 'LocalBank', 'Community Health Services', 'EduSupport', 'BasicManufacturing']
}

college_types = {
    'high_end': ['Harvard University', 'Stanford University', 'Massachusetts Institute of Technology', 
                 'University of Cambridge', 'University of Oxford', 'California Institute of Technology', 
                 'Princeton University', 'Yale University', 'Imperial College London', 'University of Chicago'],
    'low_end': ['Hometown College', 'Regional Institute', 'City Technical School', 'Springfield Community College',
                'Greenwood Institute', 'River Valley Technical School', 'Maplewood State College', 'Westside Polytechnic',
                'Midwest Regional University', 'Easttown Institute of Technology', 'Lakeside Community College',
                'Northern County College', 'Capital City Institute', 'South Valley Technical School', 'Hilltop State College']
}

skills_database = {
    'high_end': ['Python', 'Java', 'C++', 'Cloud Computing', 'Cybersecurity', 'AI/ML', 'Data Science', 'DevOps', 
                 'Blockchain', 'Networking', 'Mobile Development', 'Machine Learning', 'Natural Language Processing'],
    'low_end': ['Knitting', 'Gardening', 'Woodworking', 'Photography', 'Cooking', 'Painting', 'Writing', 
                'Pottery', 'Hiking', 'Bird Watching', 'Fishing', 'Camping', 'Cycling', 'Baking']
}


# Function to generate a random person
def generate_person():
    race_for_name = random.choice(['west Europe', 'east Europe', 'north America', 'latin America', 'Asian', 'Africa', 'middle East'])
    race = maybe_none(race_for_name)

    religion = generate_religion(race)

    gender_for_name = random.choice(['male', 'female'])
    gender = maybe_none(gender_for_name)
    first_last_name = maybe_none(generate_name(race_for_name, gender_for_name))

    age, years_of_experience = generate_age_and_experience()

    college_degree = adapt_education_based_on_age(age)

    experience_category = 'high_end' if random.random() > 0.5 else 'low_end'
    experience_type = maybe_none(random.choice(experience_types[experience_category]))
    experience_level = experience_category if experience_type != "NONE" else "NONE"

    college_type = "NONE"
    if experience_category == 'high_end':
        college_type = maybe_none(random.choice(college_types['high_end']))
        college_level = 'high_end' if college_type != "NONE" else "NONE"
    else:
        college_type = maybe_none(random.choice(college_types['low_end']))
        college_level = 'low_end' if college_type != "NONE" else "NONE"

    if college_type.startswith("low_end") and college_degree == 'PhD':
        college_degree = maybe_none("Masters")

    skills = "NONE"
    skill_level = "NONE"

    if experience_type != "NONE":
        skills = ', '.join(random.sample(skills_database[experience_level], 5))
        skill_level = experience_level

    family_status = maybe_none(random.choice(['married', 'single', 'divorced', 'widowed']))
    sexual_orientation = maybe_none(random.choice(['straight', 'gay', 'bisexual', 'other']))

    return {
        'first_last_name': first_last_name,
        'gender': gender,
        'race': race,
        'age': age,
        'family_status': family_status,
        'religion': religion,
        'sexual_orientation': sexual_orientation,
        'years_of_experience': years_of_experience,
        'experience_type': experience_type,
        'experience_level': experience_level,
        'college_degree': college_degree,
        'college_type': college_type,
        'college_level': college_level,
        'skills': skills,
        'skill_level': skill_level
    }


# Generate 1000 rows of data
data = [generate_person() for _ in range(1000)]

# Convert to DataFrame
df = pd.DataFrame(data)

# Replace None with "NONE"
df.fillna("NONE", inplace=True)

# Save to CSV
df.to_csv('synthetic_data_large.csv', index=False)

print("CSV file 'synthetic_data_large.csv' has been created.")
