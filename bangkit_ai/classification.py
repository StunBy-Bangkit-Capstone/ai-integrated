import pandas as pd


#dataset untuk indikator panjang/tinggi badan menurut umur
boys_pb_02 = pd.read_excel('dataset_baby/PB laki laki 0-2 thn.xlsx')
boys_tb_25 = pd.read_excel('dataset_baby/TB laki laki 2-5 thn.xlsx')
girl_pb_02 = pd.read_excel('dataset_baby/PB pr 0-2 thn.xlsx')
girl_tb_25 = pd.read_excel('dataset_baby/TB pr 2-5 thn.xlsx')

#dataset untuk indikator berat badan menurut umur
boys_bb = pd.read_excel('dataset_baby/BB laki laki 0-5 thn.xlsx')
girls_bb = pd.read_excel('dataset_baby/BB pr 0-5 thn.xlsx')

#dataset untuk indikator berat badan menurut panjang/tinggi badan
boys_bb_pb02 = pd.read_excel('dataset_baby/BB-PB laki-laki 0-2 thn.xlsx')
boys_bb_pb25 = pd.read_excel('dataset_baby/BB-TB laki-laki 2-5 thn.xlsx')
girls_bb_pb02 = pd.read_excel('dataset_baby/BB-PB pr 0-2 thn.xlsx')
girls_bb_pb25 = pd.read_excel('dataset_baby/BB-TB pr 2-5 thn.xlsx')

#dataset untuk indikator Indeks Massa Tubuh menurut Umur
boys_imt_02 = pd.read_excel('dataset_baby/IMT laki laki 0-2 thn.xlsx')
boys_imt_25 = pd.read_excel('dataset_baby/IMT laki laki 2-5 thn.xlsx')
girl_imt_02 = pd.read_excel('dataset_baby/IMT pr 0-2 thn.xlsx')
girl_imt_25 = pd.read_excel('dataset_baby/IMT pr 2-5 thn.xlsx')


# Fungsi untuk menghitung Z-score berdasarkan panjang/tinggi badan (length for age)
def calculate_z_score_length(gender, age, length_baby):
    if gender == "male":
        if age < 24:
            dataset = boys_pb_02
        else:
            dataset = boys_tb_25
    elif gender == "female":
        if age < 24:
            dataset = girl_pb_02
        else:
            dataset = girl_tb_25
    else:
        raise ValueError("Gender harus 'male' atau 'female'")

    row = dataset[dataset['Umur'] == age]
    if row.empty:
        raise ValueError(f"Data tidak ditemukan untuk umur {age} bulan.")

    median = row['Median'].values[0]
    minus_1_sd = row['-1 SD'].values[0]
    plus_1_sd = row['+1 SD'].values[0]

    if length_baby < median:
        z_score = (length_baby - median) / (median - minus_1_sd)
    else:
        z_score = (length_baby - median) / (plus_1_sd - median)

    return z_score


# Fungsi untuk klasifikasi status gizi berdasarkan Z-score panjang badan
def classify_nutritional_status_length(z_score):
    if z_score < -3:
        return "Sangat Pendek"
    elif -3 <= z_score < -2:
        return "Pendek"
    elif -2 <= z_score <= 3:
        return "Normal"
    elif z_score > 3:
        return "Tinggi"
    else:
        return "Tidak Diketahui"


# Fungsi untuk menghitung Z-score berdasarkan berat badan (weight for age)
def calculate_z_score_weight(weight_baby, gender, age):
    if gender == "male":
        dataset = boys_bb
    elif gender == "female":
        dataset = girls_bb
    else:
        raise ValueError("Gender harus 'male' atau 'female'")

# Mencari baris yang sesuai dengan umur
    data_row = dataset[dataset['Umur'] == age]
# Mengambil nilai Median, -1 SD, dan +1 SD
    if not data_row.empty:
        median = data_row['Median'].values[0]
        sd_minus_1 = data_row['-1 SD'].values[0]
        sd_plus_1 = data_row['+1 SD'].values[0]

# Menghitung Z-score
        if weight_baby == median:
            z_score = weight_baby - median
        elif weight_baby < median:
            z_score = (weight_baby - median) / (median - sd_minus_1)
        else:
            z_score = (weight_baby - median) / (sd_plus_1 - median)

        return z_score
    else:
        return "Data umur tidak ditemukan"


# Fungsi untuk klasifikasi status gizi berdasarkan Z-score berat badan
def classify_nutritional_status_weight(z_score):
    if z_score < -3.0:
        return "Gizi Buruk"
    elif -3.0 <= z_score < -2.0:
        return "Gizi Kurang"
    elif -2.0 <= z_score <= 2.0:
        return "Gizi Baik"
    elif z_score > 2.0:
        return "Gizi Lebih"
    else:
        return "Kategori Tidak Diketahui"

def coba(gender, age, length_baby, weight_baby):
    z_score = length_baby/age
    print(z_score)
    return z_score
    
    
# Fungsi untuk menghitung Z-score berdasarkan berat badan menurut panjang/tinggi badan
def calculate_z_score_bb_tb(gender, age, length_baby, weight_baby):
    # Menentukan dataset yang sesuai berdasarkan gender dan umur
    if gender == "male":
        if age < 24:  # Umur 0-2 tahun
            dataset = boys_bb_pb02
        else:  # Umur 2-5 tahun
            dataset = boys_bb_pb25
    elif gender == "female":
        if age < 24:  # Umur 0-2 tahun
            dataset = girls_bb_pb02
        else:  # Umur 2-5 tahun
            dataset = girls_bb_pb25
    else:
        raise ValueError("Gender harus 'male' atau 'female'")

    # Mencari baris yang sesuai dengan panjang badan
    row = dataset[dataset['Tinggi Badan'] == length_baby]
    if row.empty:
        raise ValueError(f"Data tidak ditemukan untuk panjang badan {length_baby} cm.")

    # Mengambil nilai Median, -1 SD, dan +1 SD
    median = row['Median'].values[0]
    minus_1_sd = row['-1 SD'].values[0]
    plus_1_sd = row['+1 SD'].values[0]

    # Menghitung Z-Score
    if weight_baby == median:
        z_score = weight_baby - median
    elif weight_baby < median:
        # Jika berat badan kurang dari median
        z_score = (weight_baby - median) / (median - minus_1_sd)
    else:
        # Jika berat badan lebih besar dari median
        z_score = (weight_baby - median) / (plus_1_sd - median)

    return z_score


# Fungsi untuk klasifikasi status gizi berdasarkan Z-score berat badan menurut panjang/tinggi badan
def classify_nutritional_status_bb_tb(z_score):
    if z_score < -3.0:
        return "Sangat Kurus"
    elif -3.0 <= z_score < -2.0:
        return "Kurus"
    elif -2.0 <= z_score <= 2.0:
        return "Normal"
    elif z_score > 2.0:
        return "Gemuk"
    else:
        return "Kategori Tidak Diketahui"


# Fungsi untuk menghitung Z-score berdasarkan Indeks Massa Tubuh (IMT) menurut umur
def calculate_z_score_imt(gender, age, weight_baby, length_baby):
    # Menghitung IMT
    length_m = length_baby / 100  # Konversi panjang badan dari cm ke meter
    imt = weight_baby / (length_m ** 2)

    # Memilih dataset berdasarkan gender dan umur
    if gender == "male":
        if age < 24:
            dataset = boys_imt_02
        else:
            dataset = boys_imt_25
    elif gender == "female":
        if age < 24:
            dataset = girl_imt_02
        else:
            dataset = girl_imt_25
    else:
        raise ValueError("Gender harus 'male' atau 'female'")

    # Mencari baris yang sesuai dengan umur
    row = dataset[dataset['Umur'] == age]
    if row.empty:
        raise ValueError(f"Data tidak ditemukan untuk umur {age} bulan.")

    # Mengambil nilai Median, -3 SD, -2 SD, +1 SD, +2 SD, dan +3 SD
    median = row['Median'].values[0]
    minus_3_sd = row['-3 SD'].values[0]
    minus_2_sd = row['-2 SD'].values[0]
    plus_1_sd = row['+1 SD'].values[0]
    plus_2_sd = row['+2 SD'].values[0]
    plus_3_sd = row['+3 SD'].values[0]

    # Klasifikasi status gizi berdasarkan IMT
    if imt < minus_3_sd:
        status = "Gizi Buruk (Severely Wasted)"
    elif minus_3_sd <= imt < minus_2_sd:
        status = "Gizi Kurang (Wasted)"
    elif minus_2_sd <= imt <= plus_1_sd:
        status = "Gizi Baik (Normal)"
    elif plus_1_sd < imt <= plus_2_sd:
        status = "Berisiko Gizi Lebih (Possible Risk of Overweight)"
    elif plus_2_sd < imt <= plus_3_sd:
        status = "Gizi Lebih (Overweight)"
    elif imt > plus_3_sd:
        status = "Obesitas (Obese)"
    else:
        status = "Kategori Tidak Diketahui"

    return imt, status

def round_to_nearest_half(number):
    """Membulatkan angka ke kelipatan 0.5 terdekat"""
    return round(number * 2) / 2

def nutritional_status(gender, age, length_baby, weight_baby):
    
    # # Jika panjang badan diberikan
    # if length_baby is not None and weight_baby is None:
    #     try:
    #         z_score_length = calculate_z_score_length(gender, age, length_baby)
    #         nutritional_status_length = classify_nutritional_status_length(z_score_length)
    #         return z_score_length, nutritional_status_length 
    #     except ValueError as e:
    #         return str(e)

    # Jika berat badan diberikan
    # if weight_baby is not None and length_baby is None:
    #     try:
    #         z_score_weight = calculate_z_score_weight(weight_baby, gender, age)
    #         nutritional_status_weight = classify_nutritional_status_weight(z_score_weight)
    #         return z_score_weight, nutritional_status_weight
    #     except ValueError as e:
    #         return str(e)

    # Jika panjang badan dan berat badan keduanya diberikan (BB/TB)
  
    try:
        
        if hasattr(length_baby, 'item'):
            length_baby = float(length_baby.item())
            
        # Bulatkan length_baby ke kelipatan 0.5 untuk kalkulasi
        length_baby_rounded = round_to_nearest_half(length_baby)

        # BB/U (Weight-for-Age)
        z_score_weight = calculate_z_score_weight(weight_baby, gender, age)
        nutritional_status_weight = classify_nutritional_status_weight(z_score_weight)
        
        # PB/U (Length-for-Age)
        z_score_length = calculate_z_score_length(gender, age, length_baby_rounded)
        nutritional_status_length = classify_nutritional_status_length(z_score_length)
        
        # BB/TB (Weight-for-Length)
        z_score_bb_tb = calculate_z_score_bb_tb(gender, age, length_baby_rounded, weight_baby)
        status_bb_tb = classify_nutritional_status_bb_tb(z_score_bb_tb)
        
        # Menghitung IMT
        imt, status_imt = calculate_z_score_imt(gender, age, weight_baby, length_baby_rounded)
        return z_score_bb_tb, str(status_bb_tb), imt, str(status_imt), z_score_length, str(nutritional_status_length), z_score_weight, str(nutritional_status_weight)
    except ValueError as e:
        print("error: ", e)
        return str(e)

