import random

FIRST = [
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Reyansh","Muhammad","Sai","Arnav","Ayaan",
    "Krishna","Ishaan","Shaurya","Atharv","Advik","Pranav","Advaith","Aarush","Kabir","Ritvik",
    "Aanya","Aadhya","Ananya","Diya","Ira","Myra","Sara","Anvi","Prisha","Riya",
    "Kavya","Navya","Pari","Aditi","Saanvi","Aaradhya","Kiara","Pihu","Aarohi","Ishita"
]
LAST = [
    "Sharma","Verma","Gupta","Singh","Kumar","Patel","Reddy","Nair","Iyer","Rao",
    "Mehta","Joshi","Desai","Kulkarni","Chauhan","Yadav","Mishra","Pandey","Kapoor","Malhotra",
    "Bose","Banerjee","Chatterjee","Das","Ghosh","Roy","Sen","Shetty","Pillai","Menon"
]

def random_indian_name():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"
