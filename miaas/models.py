__author__ = 'mkk'


class Sensor:
    EHEALTHKIT = "ehealthkit"
    MINDWAVE = "mindwave"
    WITHINGS = "withings"


class Measurement:
    PULSE = "pulse"
    SPO2 = "spo2"
    BLOOD_PRESSURE = "blood pressure"
    GLUCOSE = "glucose"
    ECG = "ecg"
    EMG = "emg"
    GSR = "gsr"
    EEG = "eeg"
    TEMPERATURE = "temperature"
    WEIGHT = "weight"
    FAT = "fat"


class Context:
    PULSE = "pulse"
    SPO2 = "spo2"
    BLOOD_PRESSURE = "blood pressure"
    GLUCOSE = "glucose"
    HEART = "heart activity"
    MUSCLE = "muscle activity"
    SKIN = "skin"
    BRAIN = "brain"
    BMI = "bmi"
    FAT = "fat"
    MENTAL_STABILITY = "mental stability"
    MENTAL_STRESS = "mental stress"

    NORMAL = "Normal"
    NON_DIABETIC = "Non-diabetic"
    LOW = "Low"
    HIGH = "High"
    MEDIUM = "Medium"
    UNSTABLE = "Unstalbe"
    MEDIUM_LOW = "Medium-Low"
    OVERWEIGHT = "Overweight"

    CATEGORIES = {
        BMI: ['Very Severely Underweight', 'Severely Underweight', 'Underweight', 'Normal', 'Overweight',
              'Obese_class1', 'Obese_class2', 'Obese_class3'],
        FAT: ['Extremely Thin', 'Thin Like Athletes', 'Fitness', 'Normal', 'Obese'],
        BLOOD_PRESSURE: ['Hypotension', 'Normal', 'Pre-Hypertension', 'Hypertension Stage 1', 'Hypertension Stage 2',
                         'Hypertensive Emergency'],
        GLUCOSE: ['Low', 'Normal', 'High'],
        SPO2: ['Severely Low', 'Low', 'Mild Low', 'Normal'],
        PULSE: ['Slow', 'Normal', 'Fast'],
        HEART: ['Bad', 'Normal', 'Good'],
        MENTAL_STABILITY: ['Very Low', 'Low', 'Normal', 'High', 'Very High'],
        MENTAL_STRESS: ['Very Low', 'Low', 'Normal', 'High', 'Very High'],
        MUSCLE: ['Bad', 'Normal', 'Good']
    }


class HealthIndex:
    TOTAL_HI = "totalHI"
    BLOOD_HI = "bloodHI"
    HEART_HI = "heartHI"
    BODY_FITNESS_HI = "bodyFitnessHI"
    MUSCLE_HI = "muscleHI"
    MENTAL_HI = "mentalHI"


class UerProfile:
    WATER_INTAKE = "water_intake"
    ALCOHOL_CONSUMPTION = "alcohol_consumption"
    ALCOHOL_FREQUENCY = "alcohol_freq"
    SMOKING_STATE = "smoking_state",
    EXERCISE_TIME = "exercise_time",
    SLEEP_TIME = "sleep_time",
    HEIGHT = "height"


context_meas_relations = {
    Context.PULSE: [Measurement.PULSE],
    Context.BLOOD_PRESSURE: [Measurement.BLOOD_PRESSURE],
    Context.BMI: [Measurement.WEIGHT],
    Context.FAT: [Measurement.FAT],
    Context.HEART: [Measurement.ECG],
    Context.SPO2: [Measurement.SPO2],
    Context.GLUCOSE: [Measurement.GLUCOSE],
    Context.MUSCLE: [Measurement.EMG],
    Context.MENTAL_STABILITY: [Measurement.EEG],
    Context.MENTAL_STRESS: [Measurement.GSR]
}

hi_context_relations = {
    HealthIndex.BLOOD_HI: [Context.PULSE, Context.SPO2, Context.BLOOD_PRESSURE, Context.GLUCOSE, Context.HEART],
    HealthIndex.BODY_FITNESS_HI: [Context.BMI, Context.FAT],
    HealthIndex.HEART_HI: [Context.BLOOD_PRESSURE, Context.BMI, Context.HEART, Context.PULSE],
    HealthIndex.MENTAL_HI: [Context.MENTAL_STRESS, Context.MENTAL_STABILITY],
    HealthIndex.MUSCLE_HI: [Context.BMI, Context.FAT, Context.MUSCLE],
    HealthIndex.TOTAL_HI: [Context.BLOOD_PRESSURE, Context.MUSCLE, Context.FAT, Context.BMI, Context.GLUCOSE,
                           Context.HEART, Context.MENTAL_STRESS, Context.MENTAL_STABILITY, Context.PULSE,
                           Context.SPO2]
}