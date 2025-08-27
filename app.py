import streamlit as st
import pandas as pd

# ===== ฟังก์ชันคำนวณ =====
def bmi(weight_kg, height_cm):
    h_m = height_cm / 100
    return weight_kg / (h_m * h_m) if weight_kg and height_cm else 0

def ibw_asian(sex, height_cm):
    base = 50 if sex == "ชาย" else 45
    return max(0, base + (height_cm - 150) * 0.9)

def calories_per_kg_baseline(bmi, goal):
    kcal = 25
    if bmi >= 27:
        kcal = 20
    if bmi < 18.5:
        kcal = 30
    if goal == "ลดน้ำหนัก":
        kcal -= 2
    if goal == "เพิ่มน้ำหนัก":
        kcal += 2
    return max(16, min(36, kcal))

def activity_factor(level):
    return {
        "นั่งทำงาน": 1.0,
        "กิจกรรมเบา": 1.1,
        "ปานกลาง": 1.2,
        "ค่อนข้างมาก": 1.3,
    }.get(level, 1.0)

def split_carb_per_meals(total_carb_g, pattern="3+1"):
    patterns = {
        "3 มื้อ":    [0.33, 0.34, 0.33, 0],
        "3+1 มื้อ":  [0.30, 0.35, 0.30, 0.05],
        "2+1 มื้อ":  [0.35, 0.45, 0, 0.20]
    }
    w = patterns.get(pattern, patterns["3+1 มื้อ"])
    return [round(total_carb_g * p) for p in w]

# ===== UI =====
st.title("🍚 โปรแกรมคำนวณคาร์บและโปรตีนสำหรับผู้ป่วยเบาหวาน")

col1, col2 = st.columns(2)
with col1:
    sex = st.selectbox("เพศ", ["ชาย", "หญิง"])
    height = st.number_input("ส่วนสูง (ซม.)", 120, 220, 160)
    weight = st.number_input("น้ำหนัก (กก.)", 30, 200, 60)
with col2:
    goal = st.selectbox("เป้าหมาย", ["ลดน้ำหนัก", "คงที่", "เพิ่มน้ำหนัก"])
    activity = st.selectbox("ระดับกิจกรรม", ["นั่งทำงาน", "กิจกรรมเบา", "ปานกลาง", "ค่อนข้างมาก"])
    meal_pattern = st.selectbox("รูปแบบมื้ออาหาร", ["3 มื้อ", "3+1 มื้อ", "2+1 มื้อ"])

st.subheader("⚡️ สัดส่วนพลังงานที่ต้องการ (%)")
carb_pct = st.slider("คาร์โบไฮเดรต (%)", 20, 60, 50)
protein_pct = st.slider("โปรตีน (%)", 10, 30, 20)
fat_pct = max(0, 100 - carb_pct - protein_pct)
st.write(f"👉 ไขมัน = {fat_pct}%")

# ===== ปุ่มกด =====
if st.button("🔍 คำนวณผลลัพธ์"):
    # คำนวณค่าหลัก
    bmi_val = bmi(weight, height)
    ibw_val = ibw_asian(sex, height)
    kcal_per_kg = calories_per_kg_baseline(bmi_val, goal) * activity_factor(activity)
    total_kcal = round(ibw_val * kcal_per_kg)

    carb_kcal = round((carb_pct / 100) * total_kcal)
    protein_kcal = round((protein_pct / 100) * total_kcal)
    fat_kcal = round((fat_pct / 100) * total_kcal)

    carb_g = carb_kcal // 4
    protein_g = protein_kcal // 4
    fat_g = fat_kcal // 9
    carb_split = split_carb_per_meals(carb_g, meal_pattern)

    # ===== แสดงผลรวม =====
    st.subheader("📊 ผลลัพธ์รวมต่อวัน")
    st.write(f"**BMI**: {bmi_val:.1f}")
    st.write(f"**น้ำหนักที่ควรเป็น (IBW)**: {ibw_val:.1f} กก.")
    st.write(f"**พลังงานรวม**: {total_kcal} kcal/วัน")

    st.write(f"- คาร์โบไฮเดรต: {carb_g} กรัม/วัน")
    st.write(f"- โปรตีน: {protein_g} กรัม/วัน")
    st.write(f"- ไขมัน: {fat_g} กรัม/วัน")

    # ===== สรุปตามมื้อ =====
    st.subheader("🍴 สรุปโภชนาการรายมื้อ")

    meal_names = ["เช้า", "กลางวัน", "เย็น", "ของว่าง"]
    num_meals = sum([1 for g in carb_split if g > 0])
    protein_per_meal = round(protein_g / num_meals)

    meal_data = []
    for meal, carb_g_m in zip(meal_names, carb_split):
        if carb_g_m == 0:
            continue

        # คาร์บ
        carb_portion = round(carb_g_m / 15, 1)    # 1 portion carb = 15g
        rice_cup = round(carb_portion / 2, 1)     # 1 ทัพพีข้าว ≈ 30g carb = 2 portion
        carb_examples = f"{carb_portion} portion ≈ ข้าว {rice_cup} ทัพพี หรือ ขนมปัง {carb_portion} แผ่น หรือ เส้นก๋วยเตี๋ยว {carb_portion} ถ้วย"

        # โปรตีน
        prot_portion = round(protein_per_meal / 7, 1)  # 1 portion protein ≈ 7g
        prot_examples = f"{prot_portion} portion ≈ เนื้อสัตว์ {prot_portion*30:.0f} กรัม หรือ ไข่ {prot_portion} ฟอง หรือ ปลา {prot_portion} ชิ้น หรือ เต้าหู้ {prot_portion} ก้อนเล็ก"

        meal_data.append([
            meal,
            carb_g_m, f"{carb_portion} portion", f"{rice_cup} ทัพพี", carb_examples,
            protein_per_meal, f"{prot_portion} portion", prot_examples
        ])

    df_meal = pd.DataFrame(meal_data, columns=[
        "มื้ออาหาร",
        "คาร์บ (g)", "portion คาร์บ", "≈ ข้าว (ทัพพี)", "ตัวอย่างคาร์บ",
        "โปรตีน (g)", "portion โปรตีน", "ตัวอย่างโปรตีน"
    ])

    st.table(df_meal)
